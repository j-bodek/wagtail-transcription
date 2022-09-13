from django.urls import path, re_path
from django.urls import path
from .views import (
    ValidateTranscriptionDataView, 
    RequestTranscriptionView, 
    ReceiveTranscriptionView, 
    DeleteNotificationView, 
    GetProcessingTranscriptionsView, 
    GetTranscriptionData
)
from django.contrib.admin.views.decorators import staff_member_required


app_name = 'wagtail_transcription'
urlpatterns = [
    path('validate_transcription_data/', staff_member_required(ValidateTranscriptionDataView.as_view()), name='validate_transcription_data'),
    path('request_transcription/', staff_member_required(RequestTranscriptionView.as_view()), name='request_transcription'),
    path('processing_transcriptions/', staff_member_required(GetProcessingTranscriptionsView.as_view()), name='processing_transcriptions'),
    path('transcription_data/', staff_member_required(GetTranscriptionData.as_view()), name='transcription_data'),
    re_path(r'^receive_transcription/(?P<m>[0-9A-Za-z_/-]+)/(?P<t>[0-9A-Za-z_/-]+)/(?P<f>[0-9A-Za-z_/-]+)/(?P<e>[0-9A-Za-z_/-]+)/(?P<v>[0-9A-Za-z_-]+)/(?P<u>[0-9]+)?$', ReceiveTranscriptionView.as_view(), name='receive_transcription'),

    path('delete_notification/', staff_member_required(DeleteNotificationView.as_view()), name='delete_notification'),
]
