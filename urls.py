from django.urls import path, re_path
from django.urls import path
from .views import ValidateTranscriptionDataView, RequestTranscriptionView, ReceiveTranscriptionView, DeleteNotificationView, GetProcessingTranscriptionsView

app_name = 'wagtail_transcription'
urlpatterns = [
    path('validate_transcription_data/', ValidateTranscriptionDataView.as_view(), name='validate_transcription_data'),
    path('request_transcription/', RequestTranscriptionView.as_view(), name='request_transcription'),
    path('processing_transcriptions/', GetProcessingTranscriptionsView.as_view(), name='processing_transcriptions'),
    re_path(r'^receive_transcription/(?P<m>[0-9A-Za-z_/-]+)/(?P<t>[0-9A-Za-z_/-]+)/(?P<f>[0-9A-Za-z_/-]+)/(?P<e>[0-9A-Za-z_/-]+)/(?P<v>[0-9A-Za-z_-]+)/(?P<u>[0-9]+)?$', ReceiveTranscriptionView.as_view(), name='receive_transcription'),

    path('delete_notification/', DeleteNotificationView.as_view(), name='delete_notification'),
]
