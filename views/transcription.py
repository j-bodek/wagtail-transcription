from django.http import JsonResponse
from django.views import View
from django.utils.html import format_html
from django.shortcuts import reverse
from .mixins import TranscriptionDataValidationMixin, ReceiveTranscriptionMixin
from pytube import YouTube
from django.conf import settings
import requests
from django.middleware import csrf
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from notifications.signals import notify

class ValidateTranscriptionDataView(TranscriptionDataValidationMixin, View):
    """
    Validate video_id, model_instance_str, check if transcription for same video is running
    If data valid return modal with video title, link, thumbnail, channel name and button to continue
    If data invalid return modal with appropriate error message
    """
    def post(self, request, *args, **kwargs):
        data = request.POST
        video_id = data.get('video_id')
        edit_url = data.get('edit_url')
        # this string allow to dynamically get any model instance
        model_instance_str = data.get('model_instance')
        transcription_field = data.get('transcription_field')
        field_name = data.get('field_name')
        # validate data
        is_data_valid, response_message, _ = self.data_validation(video_id, model_instance_str, transcription_field)
        response_message = self.format_response_message(video_id, edit_url, transcription_field, field_name, model_instance_str, is_data_valid, response_message)
        return JsonResponse(response_message)

    def format_response_message(self, video_id, edit_url, transcription_field, field_name, model_instance_str, is_data_valid, response_message):
        if not is_data_valid:
            message = format_html(f"""
                <h3 style="color: #842e3c; margin:0"><b>{response_message.get("message")}</b></h3>
            """)
            response_message['message'] = message
        else:
            audio_url, audio_duration = self.yt_audio_and_duration(video_id)
            video_title, video_thumbnail, channel_name = self.get_youtube_video_data(video_id)
            message = format_html(f"""
                <h3 style="color: #0c622e; font-weight:bold">Transcription process will take about {self.format_seconds(audio_duration//1.25)}</h3>
                <a href="https://www.youtube.com/watch?v={video_id}" target="_blank">
                    <div style="display: flex; background: #262626">
                        <img src="{video_thumbnail}" alt="{channel_name}-image">
                        <div style="padding-left: .5rem; padding-top: .5rem; height: fit-content;">
                            <p style="font-size:14px; line-height:1; margin:0; color: white;">{video_title}</p>
                            <p style="font-size:12px; color:#a3a3a3; margin: 0; margin-top: .25rem">{channel_name}</p>
                        </div>
                    </div>
                </a>
                <div style="display:flex; margin-top: 1rem; justify-content: right">
                    <form method="POST" action="{reverse('wagtail_transcription:request_transcription')}">
                        <input type="hidden" name="csrfmiddlewaretoken" value="{csrf.get_token(self.request)}">
                        <input type="hidden" name="video_id" value="{video_id}">
                        <input type="hidden" name="transcription_field" value="{transcription_field}">
                        <input type="hidden" name="field_name" value="{field_name}">
                        <input type="hidden" name="audio_url" value="{audio_url}">
                        <input type="hidden" name="audio_duration" value="{audio_duration}">
                        <input type="hidden" name="edit_url" value="{edit_url}">
                        <input type="hidden" name="model_instance_str" value="{model_instance_str}">
                        <button class="continue_btn button action-save" action="button">Continue</button>
                    </form>
                </div>
            """)
            response_message['message'] = message

        return response_message

    def format_seconds(self, seconds):
        """
        Format seconds to user friendly format
        """
        hours, seconds = f"{int(seconds//3600)} hour{'s' if seconds//3600 > 1 else ''} " if seconds//3600 > 0 else '', seconds - ((seconds//3600 )* 3600)
        minutes, seconds = f"{int(seconds//60)} minute{'s' if seconds//60 > 1 else ''} " if seconds//60 > 0 else '', seconds - ((seconds//60 )* 60)
        seconds = f"{int(seconds)} second{'s' if seconds > 1 else ''}"
        return f"{hours} {minutes} {seconds}"
        
    def yt_audio_and_duration(self, video_id):
        yt = YouTube(f'https://www.youtube.com/watch?v={video_id}')
        audio_url = yt.streams.all()[0].url  # Get the URL of the video stream
        return audio_url, yt.length

    def get_youtube_video_data(self, video_id):
        # get title, thumbnail, author
        url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={settings.YOUTUBE_DATA_API_KEY}'
        r = requests.get(url)
        snippet = r.json()['items'][0]['snippet']
        return snippet['title'], snippet['thumbnails']['default']['url'], snippet['channelTitle']

class RequestTranscriptionView(TranscriptionDataValidationMixin, View):

    api_token = settings.ASSEMBLY_API_TOKEN

    def post(self, request, *args, **kwargs):
        data = request.POST
        video_id = data.get('video_id')
        # this string allow to dynamically get any model instance
        model_instance_str = data.get('model_instance_str')
        transcription_field = data.get('transcription_field')
        field_name = data.get('field_name')
        edit_url = data.get("edit_url")

        # validate data
        is_data_valid, response_message, _ = self.data_validation(video_id, model_instance_str, transcription_field)
        if is_data_valid:
            # encode model_instance_str, transcription_field, field_name to base 64
            model_instance_str_b64 = urlsafe_base64_encode(force_bytes(model_instance_str))
            transcription_field_b64 = urlsafe_base64_encode(force_bytes(transcription_field))
            field_name_b64 = urlsafe_base64_encode(force_bytes(field_name))
            edit_url_b64 = urlsafe_base64_encode(force_bytes(edit_url))

            webhook_url = settings.BASE_URL + reverse('wagtail_transcription:receive_transcription', 
            kwargs={'m':model_instance_str_b64, 't':transcription_field_b64, 'f':field_name_b64, 'e':edit_url_b64, 'v':video_id, 'u': request.user.id})
            self.transcript_audio(data.get("audio_url"), webhook_url)

        return JsonResponse(response_message)
 
    def transcript_audio(self, audio_url, webhook_url):
        # TRANSCRIPE UPLOADED FILE
        endpoint = "https://api.assemblyai.com/v2/transcript"
        json = {
            "audio_url": audio_url,
            "webhook_url": webhook_url,
        }
        headers = {
            "authorization": self.api_token,
            "content-type": "application/json",
        }

        r = requests.post(endpoint, json=json, headers=headers)
        response = r.json()
        return response