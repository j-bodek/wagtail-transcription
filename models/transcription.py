from wagtail.documents.models import AbstractDocument
from wagtail.admin.edit_handlers import (
    FieldPanel
)
from django.db import models

class Transcription(AbstractDocument):
    video_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    verified = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    
    panels = [
        FieldPanel('title'),
        FieldPanel('video_id'),
        FieldPanel('verified'),
        FieldPanel('completed'),
        FieldPanel('file'),
        FieldPanel("tags"),
    ]

    # admin_form_fields = ("title", "video_id", "verified", "completed", "file", "collection", "tags")

    class Meta(AbstractDocument.Meta):
        permissions = [
            ("choose_document", "Can choose document"),
        ]
        verbose_name = "Transcription"
        verbose_name_plural = "Transcriptions"