from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    modeladmin_register,
)

from .transcription import Transcription

class TranscriptionAdmin(ModelAdmin):
    model = Transcription
    menu_icon = "doc-full-inverse"
    base_url_path = 'documents/transcription'
    menu_order = 200
    add_to_admin_menu = True
    list_display = (
        "title",
        "video_id",
        "completed",
        "verified",
    )
    list_filter = ["completed", "verified"]
    search_fields = ["title"]

modeladmin_register(TranscriptionAdmin)