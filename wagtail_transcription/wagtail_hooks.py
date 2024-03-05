from typing import Type

import requests
from django.conf import settings
from django.template import loader
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from wagtail import VERSION as WAGTAIL_VERSION
from wagtail import hooks
from wagtail.admin.menu import Menu, SubmenuMenuItem
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.documents.wagtail_hooks import DocumentsMenuItem

from .models import Transcription


class TranscriptionAdmin(ModelAdmin):
    """
    This class define Transcription Admin
    """

    model = Transcription
    menu_icon = "doc-full-inverse"
    base_url_path = "transcription"
    menu_order = 200
    list_display = (
        "title",
        "video",
        "completed",
        "verified",
    )
    list_filter = ["completed", "verified"]
    search_fields = ["title"]

    def video(self, obj: Type[Transcription]):
        """
        This method is responsible for displaying formatted video
        data (thumbnail, title, url)
        """

        url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={obj.video_id}&key={settings.YOUTUBE_DATA_API_KEY}"  # noqa
        r = requests.get(url)
        context = {"obj": obj}
        try:
            snippet = r.json()["items"][0]["snippet"]
            context.update(
                {
                    "thumbnail": snippet["thumbnails"]["default"]["url"],
                    "title": snippet["title"],
                }
            )
        except IndexError:
            context.update({"thumbnail": None, "title": None})

        return loader.render_to_string(
            "wagtail_transcription/admin/video_data.html",
            context=context,
        )

    def get_menu_item(self):
        if (
            not hasattr(settings, "DOCUMENTS_GROUP")
            or settings.DOCUMENTS_GROUP is not True
        ):
            return super().get_menu_item()
        """
            If DOCUMENTS_GROUP menu variable is set to True merge documents
            and tanscription into one menu group
        """

        # remove documents snippet
        @hooks.register("construct_main_menu")
        def hide_snippets_menu_item(request, menu_items):
            menu_items[:] = [item for item in menu_items if item.name != "documents"]

        # create submenu item
        menu_items = self.get_submenu_items()
        if WAGTAIL_VERSION >= (4, 0):
            submenu = Menu(items=menu_items)
        else:
            from wagtail_modeladmin.menus import SubMenu

            submenu = SubMenu(menu_items)
        return SubmenuMenuItem(
            "Documents",
            submenu,
            classnames="doc-full-inverse",
            name="custom-documents",
        )

    def get_submenu_items(self) -> list:
        """
        returns list of submenu items
        """

        return [
            DocumentsMenuItem(
                _("Documents"),
                reverse("wagtaildocs:index"),
                name="documents",
                icon_name="doc-full-inverse",
                order=400,
            ),
            super().get_menu_item(),
        ]


modeladmin_register(TranscriptionAdmin)
