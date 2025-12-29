# django
from django.http import JsonResponse, HttpRequest
from django.views import View
from django.shortcuts import get_object_or_404

# notifications

# pytube

# wagtail transcription
# from wagtail_transcription.views.mixins import ReceiveTranscriptionMixin
from wagtail_transcription.models import Transcription
from wagtail_transcription.wagtail_hooks import TranscriptionAdmin

# other packages
import re
from typing import Type


class GetProcessingTranscriptionsView(View):
    """
    Return ids of processing transcriptions
    """

    http_method_names = ["get"]

    def get(
        self,
        request: Type[HttpRequest],
        *args,
        **kwargs,
    ) -> Type[JsonResponse]:
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

    http_method_names = ["get"]

    def get(
        self,
        request: Type[HttpRequest],
        *args,
        **kwargs,
    ) -> Type[JsonResponse]:
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
