# django
from django.http import JsonResponse, HttpRequest
from django.views import View
from django.utils.html import format_html
from django.shortcuts import reverse, get_object_or_404
from django.conf import settings
from django.middleware import csrf
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.db.models import Model
from django.db import transaction
from django.template import loader
from django.apps import apps

# notifications
from notifications.signals import notify

# pytube
from pytube import YouTube

# wagtail transcription
# from wagtail_transcription.views.mixins import ReceiveTranscriptionMixin
from wagtail_transcription.decorators import video_data_validation
from wagtail_transcription.models import Transcription
from wagtail_transcription.wagtail_hooks import TranscriptionAdmin
from wagtail_transcription.tokens import validated_video_data_token

# other packages
import requests
import json
import re
import time
from typing import Type
import logging


class GetProcessingTranscriptionsView(View):
    """
    Return ids of precessing transcriptions
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
