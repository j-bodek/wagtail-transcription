from django import template
from django.template.defaulttags import register
from django.db import models

register = template.Library()

@register.filter
def get_app_model_id(instance):
    """
    This tag takes django model instance and return string : "app:model_name:instance_id"
    """
    model = type(instance)
    if issubclass(model, models.Model):
        app = model._meta.app_label
        return f"{app}:{model.__name__}:{instance.id}"
    return False