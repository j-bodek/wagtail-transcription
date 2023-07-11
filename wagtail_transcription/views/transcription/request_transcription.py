# django
from django.http import JsonResponse, HttpRequest
from django.views import View
from django.shortcuts import reverse
from django.conf import settings
from django.db.models import Model
from django.db import transaction
from django.apps import apps

# wagtail transcription
from wagtail_transcription.models import Transcription
from wagtail_transcription.tokens import validated_video_data_token

# other packages
import requests
from typing import Type
import logging


class RequestTranscriptionView(View):

    """
    This view is used to request transcription process and init
    Transcription instance. This request takes token as url parameter
    to check if video data was previously validated.

    This view get following data in request post:
    -   csrfmiddleware token - django token used to protect from
        cross site request forgery attacks

    -   video_id - id of youtube video

    -   audio_url - url of audio from which transcript will be
        created

    -   transcription_field - parent model field which willbe used
        to set transcription instance

    -   field_name - name of field for youtube id
    """

    api_token = settings.ASSEMBLY_API_TOKEN
    http_method_names = ["post"]

    def post(
        self,
        request: Type[HttpRequest],
        token: str,
        *args,
        **kwargs,
    ) -> Type[JsonResponse]:
        data = request.POST
        # check if data was validated
        if not validated_video_data_token.check_token(
            request.user, data.get("video_id"), token
        ):
            return JsonResponse(
                {
                    "class": "success",
                    "type": "success",
                    "message": "",
                }
            )

        error_msg = None
        try:
            with transaction.atomic():
                # create transcription with completed=False
                transcription = Transcription.objects.create(
                    title=f"auto_transcription-{data.get('video_id')}",
                    video_id=data.get("video_id"),
                )
                # set transcription for parent model
                model_instance = self.get_parent_instance(
                    data.get("parent_instance_str")
                )
                # set video_id
                setattr(model_instance, data.get("field_name"), data.get("video_id"))
                # set transcription instance
                setattr(model_instance, data.get("transcription_field"), transcription)
                model_instance.save()

                response = self.request_audio_transcription()
                # if response do not have id raise error
                if response.get("id") is None:
                    error_msg = response.get("error")
                    raise ValueError()

            return JsonResponse({"class": "success", "type": "success"})

        except Exception as e:
            logging.exception("message")
            return JsonResponse(
                {
                    "class": "error",
                    "type": "error",
                    "message": (
                        error_msg or "Ops... Something went wrong. Try again later."
                    ),
                }
            )

    def get_parent_instance(
        self,
        parent_instance_str: str,
    ) -> Type[Model]:
        """
        This method is used to get model instance from its str
        representation. "app:model_name:instance_id"
        """

        try:
            app, model, instance_id = parent_instance_str.split(":")
            model_instance = apps.get_model(app, model).objects.get(id=str(instance_id))
            return model_instance
        except (AttributeError, ValueError, LookupError):
            return None

    def request_audio_transcription(self) -> dict:
        """
        Send transcription request to assemblyai
        """

        # webhook_url will be then used by assemblyai to send
        # request about finished transcription or errors
        webhook_url = settings.BASE_URL.strip("/") + reverse(
            "wagtail_transcription:receive_transcription",
            kwargs={
                "video_id": self.request.POST.get("video_id"),
                "user_id": self.request.user.id,
            },
        )

        # send request to assemblyai
        endpoint = "https://api.assemblyai.com/v2/transcript"
        json = {
            "audio_url": self.request.POST.get("audio_url"),
            "webhook_url": webhook_url,
            "speaker_labels": True,
        }
        headers = {
            "authorization": self.api_token,
            "content-type": "application/json",
        }

        r = requests.post(endpoint, json=json, headers=headers)
        return r.json()
