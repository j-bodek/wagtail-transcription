from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.functions import Lower
from typing import List


def staff_or_group_required(
    view_func=None,
    redirect_field_name=REDIRECT_FIELD_NAME,
    login_url="admin:login",
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
