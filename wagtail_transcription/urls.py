from django.urls import path, re_path
from django.urls import path
from .views import (
    ValidateTranscriptionDataView,
    RequestTranscriptionView,
    ReceiveTranscriptionView,
    DeleteNotificationView,
    GetProcessingTranscriptionsView,
    GetTranscriptionData,
)
from django.utils.module_loading import import_string
from django.conf import settings
from .decorators import staff_or_group_required

if hasattr(settings, "RECEIVE_TRANSCRIPTION_VIEW"):
    ReceiveTranscriptionView = import_string(settings.RECEIVE_TRANSCRIPTION)
if hasattr(settings, "REQUEST_TRANSCRIPTION_VIEW"):
    RequestTranscriptionView = import_string(settings.REQUEST_TRANSCRIPTION_VIEW)

app_name = "wagtail_transcription"
urlpatterns = [
    # Transcription Urls
    path(
        "validate_transcription_data/",
        staff_or_group_required(
            ValidateTranscriptionDataView.as_view(),
            group_names=["moderators", "editors"],
        ),
        name="validate_transcription_data",
    ),
    re_path(
        r"request_transcription/(?P<token>[0-9A-Za-z_/-]+)/",
        staff_or_group_required(
            RequestTranscriptionView.as_view(),
            group_names=["moderators", "editors"],
        ),
        name="request_transcription",
    ),
    path(
        "processing_transcriptions/",
        staff_or_group_required(
            GetProcessingTranscriptionsView.as_view(),
            group_names=["moderators", "editors"],
        ),
        name="processing_transcriptions",
    ),
    path(
        "transcription_data/",
        staff_or_group_required(
            GetTranscriptionData.as_view(),
            group_names=["moderators", "editors"],
        ),
        name="transcription_data",
    ),
    re_path(
        r"^receive_transcription/(?P<video_id>[0-9A-Za-z_-]+)/(?P<user_id>[0-9]+)?$",
        ReceiveTranscriptionView.as_view(),
        name="receive_transcription",
    ),
    # Notification Urls
    path(
        "delete_notification/",
        staff_or_group_required(
            DeleteNotificationView.as_view(),
            group_names=["moderators", "editors"],
        ),
        name="delete_notification",
    ),
]
