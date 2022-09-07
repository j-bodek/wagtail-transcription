from django.http import JsonResponse
from django.views import View
from notifications.models import Notification

class DeleteNotificationView(View):
    """
    Delete Notification instance from database
    """

    def post(self, request, *args, **kwargs):
        notification_id = request.POST.get('notification_id')
        notification = Notification.objects.filter(id=notification_id)
        if notification.exists():
            notification.delete()
            return JsonResponse({"message": "Successfully deleted notification"})
        else:
            return JsonResponse({"message":"Notification does not exist"})
