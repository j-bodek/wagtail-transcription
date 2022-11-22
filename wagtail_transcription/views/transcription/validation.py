# django
from django.http import JsonResponse, HttpRequest
from django.views import View
from django.conf import settings
from django.utils.decorators import method_decorator
from django.template import loader

# pytube
from pytube import YouTube

# wagtail transcription
from wagtail_transcription.decorators import video_data_validation
from wagtail_transcription.tokens import validated_video_data_token

# other packages
import requests
import time
from typing import Type


class ValidateTranscriptionDataView(View):
    """
    Validate video_id, model_instance_str, check if transcription for same video is running
    If data valid return modal with video title, link, thumbnail, channel name and button
    to continue. If data invalid return modal with appropriate error message

    This view get following data via post request:
    -   csrfmiddleware token - django token used to protect from
        cross site request forgery attacks

    -   video_id - id of youtube video

    -   parent_instance_str - string used to get instance of parent model (model
        to which transcription will be assigned)

    -   transcription_field - parent model field which willbe used
        to set transcription instance

    -   transcription_field_id - html id of field to which
        transcription will be associated

    -   field_name - name of field for youtube id
    """

    http_method_names = ["post"]

    @method_decorator(video_data_validation)
    def post(
        self,
        request: Type[HttpRequest],
        youtube_instance: Type[YouTube],
        *args,
        **kwargs,
    ) -> Type[JsonResponse]:

        self.youtube_instance = youtube_instance
        data = self.get_context_data(request.POST)
        return JsonResponse(data)

    def get_context_data(self, data: dict) -> dict:
        """
        return data that will be returned by JsonResponse
        """

        # get video data (title, thumbnail, channel etc)
        url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={data.get('video_id')}&key={settings.YOUTUBE_DATA_API_KEY}"
        r = requests.get(url)
        snippet = r.json()["items"][0]["snippet"]

        # generate video info popup content
        message = loader.render_to_string(
            "wagtail_transcription/components/transcription_info_popup.html",
            context={
                "token": validated_video_data_token.make_token(
                    self.request.user, data.get("video_id")
                ),
                "audio_duration": time.strftime(
                    "%H:%M:%S", time.gmtime(self.youtube_instance.length // 1.25)
                ),
                "video_title": snippet["title"],
                "video_thumbnail": snippet["thumbnails"]["default"]["url"],
                "channel_name": snippet["channelTitle"],
                "audio_url": self.youtube_instance.streams[0].url,
                **{k: data.get(k) for k, _ in data.items()},
            },
            request=self.request,
        )

        return {
            "class": "success",
            "type": "success",
            "message": message,
        }
