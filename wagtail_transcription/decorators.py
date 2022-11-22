from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.template import loader
from django.db.models import Q
from django.db.models.functions import Lower
from typing import List, Type, Callable, Union
from django.http import HttpRequest, JsonResponse, HttpResponse
from functools import wraps

from django.apps import apps
from .models import Transcription
import logging
import pytube


def get_error_response(
    request: Type[HttpRequest],
    template: str,
    **context,
) -> Type[JsonResponse]:
    """
    Helper function that return json response with
    invalid data response
    """

    message = loader.render_to_string(
        f"wagtail_transcription/components/validation_error_popups/{template}",
        context=context,
        request=request,
    )
    return JsonResponse(
        {
            "class": "error",
            "type": "error",
            "message": message,
        }
    )


def video_data_validation(
    view_func: Type[Callable],
) -> Type[JsonResponse]:
    """
    This decorator validate if video with specified id
    is valid. If data is valid it pass additional YouTube
    instance argument to function
    """

    @wraps(view_func)
    def _wrap(
        request: Type[HttpRequest],
        *args,
        **kwargs,
    ) -> Type[JsonResponse]:

        data = request.POST
        # get app name and model name if it exists
        try:
            app, model, instance_id = data.get("parent_instance_str").split(":")
            model = apps.get_model(app, model)
        except (AttributeError, ValueError, LookupError) as e:
            logging.exception("message")
            # If there is error independent from user display easy error message
            return get_error_response(
                request,
                "base.html",
                msg="""Something went wrong. 
                Please try again or upload transcription manually""",
            )

        # check if parent_instance has 'transcription_field' field
        try:
            parent_instance = model.objects.get(id=str(instance_id))
            getattr(parent_instance, data.get("transcription_field"))
        except (AttributeError, ValueError, LookupError) as e:
            logging.exception("message")
            # If there is error independent from user display easy error message
            return get_error_response(
                request,
                "no_parent_instance.html",
                model_name=model.__name__,
            )

        # check if transcription for video with same id exists
        # or is currently running
        if Transcription.objects.filter(video_id=data.get("video_id")).exists():
            return get_error_response(
                request,
                "same_video_transcription.html",
                video_id=data.get("video_id"),
            )

        # try to get YouTube instance
        try:
            yt = pytube.YouTube(
                f'https://www.youtube.com/watch?v={data.get("video_id")}'
            )
        except (pytube.exceptions.RegexMatchError):
            logging.exception("message")
            return get_error_response(request, "invalid_video_id.html")

        try:
            # check if can find audio url for specified video
            if not yt.streams:
                raise pytube.exceptions.VideoUnavailable
        except (
            pytube.exceptions.VideoUnavailable,
            pytube.exceptions.LiveStreamError,
            pytube.exceptions.AgeRestrictedError,
            pytube.exceptions.VideoRegionBlocked,
            pytube.exceptions.MembersOnly,
            pytube.exceptions.VideoPrivate,
        ) as e:
            logging.exception("message")
            return get_error_response(request, "base.html", msg=str(e))

        return view_func(request, yt, *args, **kwargs)

    return _wrap


def staff_or_group_required(
    view_func: Union[Type[Callable], None] = None,
    redirect_field_name: str = REDIRECT_FIELD_NAME,
    login_url: str = "admin:login",
    group_names: List[int] = [],
) -> Type[HttpResponse]:
    """
    Decorator for views that checks that the user is logged in and is a staff
    member, redirecting to the login page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active
        and (
            u.is_staff
            or u.groups.annotate(lower_name=Lower("name"))
            .filter(Q(lower_name__in=[g.lower() for g in group_names]))
            .exists()
        ),
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator
