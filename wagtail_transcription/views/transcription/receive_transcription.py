# django
from django.http import JsonResponse, HttpRequest
from django.views import View
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.template import loader
from django.core.files.base import File
from django.contrib.auth import get_user_model

# notifications
from notifications.signals import notify

# wagtail transcription
from wagtail_transcription.views.mixins import ProcessTranscriptionMixin
from wagtail_transcription.models import Transcription

# other packages
import json
from typing import Type
import logging


# this allows to receive post request without csrf protection
@method_decorator(csrf_exempt, name="dispatch")
class ReceiveTranscriptionView(ProcessTranscriptionMixin, View):
    """
    This view is used to receive transcription response from assemblyai
    and based on that response create transcription object or display error
    """

    api_token = settings.ASSEMBLY_API_TOKEN
    http_method_names = ["post"]

    def post(
        self,
        request: Type[HttpRequest],
        video_id: str,
        user_id: str,
        *args,
        **kwargs,
    ) -> Type[JsonResponse]:

        try:
            request_body = json.loads(request.body.decode("utf-8"))
            status = request_body.get("status")
            transcript_id = request_body.get("transcript_id")
        except Exception as e:
            logging.exception("message")
            status, transcript_id = None, None

        try:
            transcription_response = self.get_transcription(transcript_id)
            if status == "completed" and transcript_id:
                # process transcription
                transcription = self.process_transcription_response(
                    transcription_response=transcription_response,
                    video_id=video_id,
                )
                notification_message = loader.render_to_string(
                    "wagtail_transcription/components/transcription_received_popup.html",
                    context={"transcription": transcription, "video_id": video_id},
                    request=self.request,
                )
                response_type = "success"
            else:
                # If error delete uncompleted Transcription
                Transcription.objects.filter(video_id=video_id).delete()
                notification_message = loader.render_to_string(
                    "wagtail_transcription/components/transcription_received_popup.html",
                    context={
                        "error": True,
                        "video_id": video_id,
                        "extra_text": transcription_response.get("error", ""),
                    },
                    request=self.request,
                )
                response_type = "error"

        except Exception as e:
            logging.exception("message")
            # If error delete uncompleted Transcription
            Transcription.objects.filter(video_id=video_id).delete()
            notification_message = loader.render_to_string(
                "wagtail_transcription/components/transcription_received_popup.html",
                context={"error": True, "video_id": video_id},
                request=self.request,
            )
            response_type = "error"

        # send notification
        user = get_user_model().objects.get(id=int(user_id))
        notify.send(
            sender=user,
            recipient=user,
            verb="Message",
            description=notification_message,
        )
        return JsonResponse({"type": response_type})

    def process_transcription_response(
        self,
        transcription_response: dict,
        video_id: str,
    ) -> Type[Transcription]:
        """
        -   transcription_response - AssemblyAi response with transcription data
            https://www.assemblyai.com/docs/walkthroughs#getting-the-transcription-result

        -   video_id - id of youtube video for which transcription was made
        """

        words = transcription_response.get("words")
        transcript_docx_io = self.create_transcript_docx(words)

        # create file instance
        docx_file = File(
            transcript_docx_io,
            name=f"auto_transcription-{video_id}.docx",
        )
        # update Transcription instance
        transcription = Transcription.objects.get(video_id=video_id)
        transcription.file = docx_file
        transcription.completed = True
        transcription.save()
        # return transcription
        return transcription
