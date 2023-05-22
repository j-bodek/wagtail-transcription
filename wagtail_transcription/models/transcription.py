from wagtail.documents.models import AbstractDocument
from wagtail.admin.panels import FieldPanel
from django.db import models
from wagtail.snippets.models import register_snippet
from django.core.exceptions import ValidationError
import re


@register_snippet
class Transcription(AbstractDocument):
    video_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
    )
    verified = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)

    panels = [
        FieldPanel("title"),
        FieldPanel("video_id"),
        FieldPanel("verified"),
        FieldPanel("completed"),
        FieldPanel("file"),
        FieldPanel("tags"),
    ]

    class Meta(AbstractDocument.Meta):
        verbose_name = "Transcription"
        verbose_name_plural = "Transcriptions"

    def validate_video_id(self) -> None:
        if self.video_id is None:
            return
        yt_id_regex = re.compile(r"^[a-zA-Z0-9_-]{11}$")
        if not yt_id_regex.match(str(self.video_id)):
            raise ValidationError(
                f"""Invalid youtube video id ("{self.video_id}"). 
                Make sure it have exactly 11 characters, 
                contains only numbers, letters or dashes"""  # noqa
            )

    def validate_transcription_file(self) -> None:
        if self.file is None:
            return
        # make sure that user can not add existing publication
        extension = str(self.file).rsplit(".", 1)[-1]
        if extension != "docx":
            raise ValidationError(
                f"""Transcription file has {extension} extension. 
                Only docx files are allowed"""  # noqa
            )

    def clean(self, *args, **kwargs) -> None:
        self.validate_video_id()
        self.validate_transcription_file()
