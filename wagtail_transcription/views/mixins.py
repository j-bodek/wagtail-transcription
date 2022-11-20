import requests
from docx import Document as docx_document
import tempfile
import io
from django.core.files.base import File
from django.apps import apps
from django.urls import reverse
from django.utils.html import format_html
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from ..models import Transcription
import os
from django.conf import settings


class ReceiveTranscriptionMixin:
    """
    Contains methods that help to clean transcripted audio data,
    create transcription docx file and set it for Transcription object
    """

    def get_user(self, user_id):
        return get_object_or_404(User, id=user_id)

    def get_model_instance(self, model_instance_str):
        try:
            app, model, instance_id = model_instance_str.split(":")
            model_instance = apps.get_model(app, model).objects.get(id=str(instance_id))
            return model_instance
        except (AttributeError, ValueError, LookupError):
            return None

    def get_transcription(self, transcript_id):
        # GET TRANSCRIPED FILE
        endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
        headers = {
            "authorization": self.api_token,
        }
        r = requests.get(endpoint, headers=headers)
        return r.json()

    def format_start_time(self, start):
        # FUNCTION TO FORMAT START TIME
        hours, start = start // 3600000, start - (start // 3600000) * 3600000
        minutes, start = start // 60000, start - (start // 60000) * 60000
        seconds, start = start // 1000, start - (start // 1000) * 1000
        miliseconds = start
        return f"[{hours:02d}:{minutes:02d}:{seconds:02d}.{miliseconds:03d}]"

    def process_transcription_words(self, words):
        phrases, phrase, speaker = [], [], None
        for word in words:
            if not speaker:
                speaker = {
                    "start": self.format_start_time(word["start"]),
                    "speaker": word["speaker"],
                }

            if speaker["speaker"] != word["speaker"]:
                phrases.append({**speaker, "phrase": " ".join(phrase)})
                speaker = {
                    "start": self.format_start_time(word["start"]),
                    "speaker": word["speaker"],
                }
                phrase = [word["text"]]

            elif speaker["speaker"] == word["speaker"]:
                phrase.append(word["text"])
        phrases.append({**speaker, "phrase": " ".join(phrase)})
        return phrases

    def transcription_string_to_docx(self, transcription_phrases):
        document = docx_document()
        with tempfile.NamedTemporaryFile() as tmp:
            for phrase in transcription_phrases:
                start_paragraph = document.add_paragraph()
                run = start_paragraph.add_run(str(phrase.get("start")))
                run.bold = True
                document.add_paragraph(phrase.get("phrase") + "\n")

            document.save(tmp.name)
            io_output = io.BytesIO(tmp.read())
        return io_output

    def add_docx_to_wagtail_docs(self, io_output, video_id):
        docx_file = File(io_output, name=f"auto_transcription-{video_id}.docx")
        transcription = Transcription.objects.get(video_id=video_id)
        transcription.file = docx_file
        transcription.completed = True
        transcription.save()
        return transcription

    def get_notification_message(
        self,
        transcription_document=None,
        error=False,
        edit_url=None,
        video_id=None,
        **kwargs,
    ):
        """
        This method is used to create notification popup displayed for user
        when transcription is done
        """
        message = format_html(
            f"""
            <div class="notification-header {'error' if error else ''}">
                <p class="notification-header-text">
                    <i class="bi bi-square-fill"></i>
                    <b style="margin: auto 0;">
                        {
                        'Error During Transcription Process' if error
                        else 'New Transcription'
                        }
                    </b>
                <p>
                <p class="notification-close" 
                data-action_url={reverse("wagtail_transcription:delete_notification")}>
                    <i class="bi bi-x"></i>
                </p>
            </div>
            <div class="notification-message {'error' if error else ''}">
                <p>{kwargs.get("extra_text", "")}</p>
                <a target="_blank" href="{edit_url}">Check Page</a>
                <a target="_blank" 
                href="{f'https://www.youtube.com/watch?v={video_id}' 
                if error else os.path.join(settings.MEDIA_ROOT, transcription_document.file.url)}">
                    {
                    'Check video' if error 
                    else 'Download Transcription File <i class="bi bi-download"></i>'
                    }
                </a>
            </div>
        """
        )
        return message
