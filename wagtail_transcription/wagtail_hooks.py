from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    modeladmin_register,
)
from wagtail import VERSION as WAGTAIL_VERSION
from wagtail import hooks
from .models import Transcription
from wagtail.documents.wagtail_hooks import DocumentsMenuItem
from django.utils.translation import gettext_lazy as _
from django.shortcuts import reverse
from wagtail.admin.menu import Menu, SubmenuMenuItem
from django.conf import settings
from django.template import loader
import requests
from typing import Type


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
        This method is responsible for displaying formated video
        data (thumbnail, title, url)
        """

        url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={obj.video_id}&key={settings.YOUTUBE_DATA_API_KEY}"
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
        if hasattr(settings, "DOCUMENTS_GROUP") and settings.DOCUMENTS_GROUP is True:
            """
            If DOCUMENTS_GROUP menu variable is set to True merge documents
            and tanscription into one menu group
            """

            # remove documents snippet
            @hooks.register("construct_main_menu")
            def hide_snippets_menu_item(request, menu_items):
                menu_items[:] = [
                    item for item in menu_items if item.name != "documents"
                ]

            # create submenu item
            menu_items = self.get_submenu_items()
            if WAGTAIL_VERSION >= (4, 0):
                submenu = Menu(items=menu_items)
            else:
                from wagtail.contrib.modeladmin.menus import SubMenu

                submenu = SubMenu(menu_items)
            return SubmenuMenuItem(
                "Documents",
                submenu,
                classnames="doc-full-inverse",
                name="custom-documents",
            )
        else:
            return super().get_menu_item()

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
