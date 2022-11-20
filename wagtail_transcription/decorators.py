from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.db.models.functions import Lower
from typing import List, Type, Callable
from django.http import HttpRequest, JsonResponse
from functools import wraps

from django.apps import apps
from .models import Transcription
from wagtail_transcription.utils.validation_errors import TranscriptionValidationErrors
import logging
import pytube

TRANSCRIPTION_VALIDATION_ERRORS = TranscriptionValidationErrors()


def video_data_validation(view_func: Type[Callable]) -> Type[JsonResponse]:
    """
    This decorator validate if video with specified id
    is valid. If data is valid it pass additional YouTube
    instance argument to function
    """

    @wraps(view_func)
    def _wrap(request: Type[HttpRequest], *args, **kwargs):
        data = request.POST
        # get app name and model name if it exists
        try:
            app, model, instance_id = data.get("model_instance_str").split(":")
            model = apps.get_model(app, model)
        except (AttributeError, ValueError, LookupError) as e:
            logging.exception("message")
            # If there is error independent from user display easy error message
            return TRANSCRIPTION_VALIDATION_ERRORS.GENERAL_ERROR_MESSAGE()

        # check if model_instance has 'transcription_field' field
        try:
            model_instance = model.objects.get(id=str(instance_id))
            getattr(model_instance, data.get("transcription_field"))
        except (AttributeError, ValueError, LookupError) as e:
            logging.exception("message")
            # If there is error independent from user display easy error message
            return TRANSCRIPTION_VALIDATION_ERRORS.NO_INSTANCE(
                model_name=model.__name__
            )

        # check if transcription for video with same id exists
        # or is currently running
        if Transcription.objects.filter(video_id=data.get("video_id")).exists():
            return TRANSCRIPTION_VALIDATION_ERRORS.SAME_VIDEO_TRANSCRIPTION(
                model_instance=model_instance, video_id=data.get("video_id")
            )

        # try to get YouTube instance
        try:
            yt = pytube.YouTube(
                f'https://www.youtube.com/watch?v={data.get("video_id")}'
            )
        except (pytube.exceptions.RegexMatchError):
            logging.exception("message")
            data = TRANSCRIPTION_VALIDATION_ERRORS.INVALID_VIDEO_ID(
                model_instance=model_instance
            )
            return JsonResponse(data)

        try:
            # check if can find audio url for specified video
            if not yt.streams.all():
                return TRANSCRIPTION_VALIDATION_ERRORS.UNABLE_TO_FIND_AUDIO(
                    model_instance=model_instance, video_id=data.get("video_id")
                )
        except (
            pytube.exceptions.VideoUnavailable,
            pytube.exceptions.LiveStreamError,
            pytube.exceptions.AgeRestrictedError,
            pytube.exceptions.VideoRegionBlocked,
            pytube.exceptions.MembersOnly,
            pytube.exceptions.VideoPrivate,
        ) as e:
            logging.exception("message")
            data = TRANSCRIPTION_VALIDATION_ERRORS.get_full_msg(msg=str(e))
            return JsonResponse(data)

        return view_func(request, yt, *args, **kwargs)

    return _wrap


def staff_or_group_required(
    view_func=None,
    redirect_field_name=REDIRECT_FIELD_NAME,
    login_url: str = "admin:login",
    group_names: List[int] = [],
):
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
