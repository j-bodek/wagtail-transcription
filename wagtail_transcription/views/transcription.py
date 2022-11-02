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
from ..models import Transcription
import re
from ..wagtail_hooks import TranscriptionAdmin
from django.shortcuts import get_object_or_404
from django.db import transaction
from wagtail_transcription.exceptions import InvalidRequest


class ValidateTranscriptionDataView(TranscriptionDataValidationMixin, View):
    """
    Validate video_id, model_instance_str, check if transcription for same video is running
    If data valid return modal with video title, link, thumbnail, channel name and button to continue
    If data invalid return modal with appropriate error message
    """

    def post(self, request, *args, **kwargs):
        data = request.POST
        is_data_valid, response_message, _ = self.data_validation(data)
        response_message = self.format_response_message(
            data, is_data_valid, response_message
        )
        return JsonResponse(response_message)

    def format_response_message(self, data, is_data_valid, response_message):
        if not is_data_valid:
            message = format_html(
                f"""
                <h3 style="color: #842e3c; margin:0"><b>{response_message.get("message")}</b></h3>
            """
            )
            response_message["message"] = message
        else:
            audio_url, audio_duration = self.yt_audio_and_duration(data.get("video_id"))
            video_title, video_thumbnail, channel_name = self.get_youtube_video_data(
                data.get("video_id")
            )
            # generate video info popup content
            TRANSCRIPTION_VIDEO_INFO_POPUP = f"""
                <h3 style="color: #0c622e; font-weight:bold">
                    Transcription process will take about 
                    {self.format_seconds(audio_duration//1.25)}
                </h3>
                <a href="https://www.youtube.com/watch?v={data.get('video_id')}" target="_blank">
                    <div style="display: flex; background: #262626">
                        <img src="{video_thumbnail}" alt="{channel_name}-image">
                        <div style="padding-left: .5rem; padding-top: .5rem; height: fit-content;">
                            <p style="font-size:14px; line-height:1; margin:0; color: white;">
                                {video_title}
                            </p>
                            <p style="font-size:12px; color:#a3a3a3; margin: 0; margin-top: .25rem">
                                {channel_name}
                            </p>
                        </div>
                    </div>
                </a>
                <div style="display:flex; margin-top: 1rem; justify-content: right">
                    <form method="POST" action="{reverse('wagtail_transcription:request_transcription')}">
                        <input type="hidden" name="csrfmiddlewaretoken" value="{csrf.get_token(self.request)}">
                        <input type="hidden" name="video_id" value="{(data.get('video_id'))}">
                        <input type="hidden" name="transcription_field" value="{(data.get('transcription_field'))}">
                        <input type="hidden" name="field_name" value="{(data.get('field_name'))}">
                        <input type="hidden" name="audio_url" value="{audio_url}">
                        <input type="hidden" name="audio_duration" value="{audio_duration}">
                        <input type="hidden" name="edit_url" value="{(data.get('edit_url'))}">
                        <input type="hidden" name="model_instance_str" value="{(data.get('model_instance_str'))}">
                        <button class="continue_btn button action-save" action="button">Continue</button>
                    </form>
                </div>
            """
            message = format_html(TRANSCRIPTION_VIDEO_INFO_POPUP)
            response_message["message"] = message

        return response_message

    def format_seconds(self, seconds):
        """
        Format seconds to user friendly format
        """
        hours, seconds = (
            f"{int(seconds//3600)} hour{'s' if seconds//3600 > 1 else ''} "
            if seconds // 3600 > 0
            else "",
            seconds - ((seconds // 3600) * 3600),
        )
        minutes, seconds = (
            f"{int(seconds//60)} minute{'s' if seconds//60 > 1 else ''} "
            if seconds // 60 > 0
            else "",
            seconds - ((seconds // 60) * 60),
        )
        seconds = f"{int(seconds)} second{'s' if seconds > 1 else ''}"
        return f"{hours} {minutes} {seconds}"

    def yt_audio_and_duration(self, video_id):
        yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
        audio_url = yt.streams.all()[0].url  # Get the URL of the video stream
        return audio_url, yt.length

    def get_youtube_video_data(self, video_id):
        # get title, thumbnail, author
        url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={settings.YOUTUBE_DATA_API_KEY}"
        r = requests.get(url)
        snippet = r.json()["items"][0]["snippet"]
        return (
            snippet["title"],
            snippet["thumbnails"]["default"]["url"],
            snippet["channelTitle"],
        )


class RequestTranscriptionView(TranscriptionDataValidationMixin, View):

    api_token = settings.ASSEMBLY_API_TOKEN

    def post(self, request, *args, **kwargs):
        data = request.POST
        video_id = data.get("video_id")

        # validate data
        is_data_valid, response_message, _ = self.data_validation(data)
        error_msg = None
        if is_data_valid:
            # encode model_instance_str, transcription_field, field_name to base 64
            model_instance_str_b64 = urlsafe_base64_encode(
                force_bytes(data.get("model_instance_str"))
            )
            transcription_field_b64 = urlsafe_base64_encode(
                force_bytes(data.get("transcription_field"))
            )
            field_name_b64 = urlsafe_base64_encode(force_bytes(data.get("field_name")))
            edit_url_b64 = urlsafe_base64_encode(force_bytes(data.get("edit_url")))

            try:
                webhook_url = settings.BASE_URL + reverse(
                    "wagtail_transcription:receive_transcription",
                    kwargs={
                        "m": model_instance_str_b64,
                        "t": transcription_field_b64,
                        "f": field_name_b64,
                        "e": edit_url_b64,
                        "v": video_id,
                        "u": request.user.id,
                    },
                )

                with transaction.atomic():
                    # create transcription with completed=False
                    Transcription.objects.create(
                        title=f"auto_transcription-{video_id}",
                        video_id=video_id,
                    )
                    response = self.request_audio_transcription(
                        "https://invalid_url", webhook_url
                    )
                    # if response do not have header raise error
                    if response.get("id") is None:
                        error_msg = response.get("error")
                        raise ValueError()
            except Exception as e:
                print(e)
                response_message = {
                    "class": "error",
                    "type": "error",
                    "message": (
                        error_msg or "Ops... Something went wrong. Try again later."
                    ),
                }

        return JsonResponse(response_message)

    def request_audio_transcription(self, audio_url, webhook_url):
        """
        Send transcription request to assemblyai
        """
        endpoint = "https://api.assemblyai.com/v2/transcript"
        json = {
            "audio_url": audio_url,
            "webhook_url": webhook_url,
            "speaker_labels": True,
        }
        headers = {
            "authorization": self.api_token,
            "content-type": "application/json",
        }

        r = requests.post(endpoint, json=json, headers=headers)
        response = r.json()
        return response


@method_decorator(
    csrf_exempt, name="dispatch"
)  # this allows to receive post request without csrf protection
class ReceiveTranscriptionView(ReceiveTranscriptionMixin, View):
    """
    This view is used to receive transcription response from assemblyai
    and based on that create transcription object or display error
    """

    api_token = settings.ASSEMBLY_API_TOKEN

    def post(self, request, m, f, t, e, v, u, *args, **kwargs):
        # decode url parameters
        model_instance_str = force_str(
            urlsafe_base64_decode(m)
        )  # get model-instance-str
        transcription_field = force_str(
            urlsafe_base64_decode(t)
        )  # get transcription-field
        field_name = force_str(urlsafe_base64_decode(f))  # get field-name
        edit_url = force_str(urlsafe_base64_decode(e))
        video_id = v  # get youtube video id
        user_id = int(u)  # get user id

        try:
            request_body = json.loads(request.body.decode("utf-8"))
            status = request_body.get("status")
            transcript_id = request_body.get("transcript_id")
        except Exception as e:
            print(e)
            status, transcript_id = None, None

        try:
            transcription_response = self.get_transcription(transcript_id)
            if status == "completed" and transcript_id:
                # process transcription
                transcription_document = self.process_transcription_response(
                    transcription_response=transcription_response,
                    video_id=video_id,
                    model_instance_str=model_instance_str,
                    field_name=field_name,
                    transcription_field=transcription_field,
                )
                notification_message = self.get_notification_message(
                    transcription_document=transcription_document,
                    edit_url=edit_url,
                    video_id=video_id,
                )
                response_type = "success"
            else:
                # If error delete uncompleted Transcription
                Transcription.objects.filter(video_id=video_id).delete()
                notification_message = self.get_notification_message(
                    error=True,
                    edit_url=edit_url,
                    video_id=video_id,
                    extra_text=transcription_response.get("error", ""),
                )
                response_type = "error"

        except Exception as e:
            print(e)
            # If error delete uncompleted Transcription
            Transcription.objects.filter(video_id=video_id).delete()
            notification_message = self.get_notification_message(
                error=True, edit_url=edit_url, video_id=video_id
            )
            response_type = "error"

        # send notification
        notify.send(
            sender=self.get_user(user_id),
            recipient=self.get_user(user_id),
            verb="Message",
            description=notification_message,
        )
        return JsonResponse({"type": response_type})

    def process_transcription_response(
        self,
        transcription_response,
        video_id,
        model_instance_str,
        field_name,
        transcription_field,
    ):
        """
        transcription_response - AssemblyAi response with transcription data https://www.assemblyai.com/docs/walkthroughs#getting-the-transcription-result
        video_id - id of youtube video for which transcription was made
        model_instance_str - string that allow to get model instance "app:model_name:instance_id"
        field_name = name of field with video_id
        transcription_field = name of field for transcription
        """
        words = transcription_response.get("words")
        transcription_string = self.process_transcription_words(words)
        io_output = self.transcription_string_to_docx(transcription_string)
        transcription_document = self.add_docx_to_wagtail_docs(io_output, video_id)
        # add transcription_document to model_instance transcription field
        model_instance = self.get_model_instance(model_instance_str)
        setattr(model_instance, field_name, video_id)
        setattr(model_instance, transcription_field, transcription_document)
        model_instance.save()

        return transcription_document


class GetProcessingTranscriptionsView(View):
    """
    Return ids of precessing transcriptions
    """

    def get(self, request, *args, **kwargs):
        transcriptions_video_ids = list(
            Transcription.objects.filter(completed=False).values_list(
                "video_id", flat=True
            )
        )

        transcriptions_video_ids = {
            video_id: True for video_id in transcriptions_video_ids
        }
        return JsonResponse(transcriptions_video_ids)


class GetTranscriptionData(View):
    """
    Return transcription id, title and edit url
    based od video_id
    """

    def get(self, request, *args, **kwargs):
        video_id = request.GET.get("video_id")
        yt_id_regex = re.compile(r"^[a-zA-Z0-9_-]{11}$")
        if not yt_id_regex.match(str(video_id)):
            transcription = None
        else:
            transcription = get_object_or_404(Transcription, video_id=video_id)

        return JsonResponse(
            {
                "new_transcription_id": None if not transcription else transcription.id,
                "new_transcription_title": None
                if not transcription
                else transcription.title,
                "new_transcription_edit_url": None
                if not transcription
                else TranscriptionAdmin().url_helper.get_action_url(
                    "edit", transcription.id
                ),
            }
        )
