from django.http import JsonResponse, HttpRequest
from django.views import View
from notifications.models import Notification
from typing import Type


class DeleteNotificationView(View):
    """
    Delete Notification instance from database
    """

    http_method_names = ["post"]

    def post(
        self,
        request: Type[HttpRequest],
        *args,
        **kwargs,
    ) -> Type[JsonResponse]:

        notification_id = request.POST.get("notification_id")
        notification = Notification.objects.filter(id=notification_id)
        if notification.exists():
            notification.delete()
            return JsonResponse({"message": "Successfully deleted notification"})
        else:
            return JsonResponse({"message": "Notification does not exist"})
