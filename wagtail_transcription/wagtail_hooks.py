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
from django.utils.html import format_html
import requests


class TranscriptionAdmin(ModelAdmin):
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

    def video(self, obj):
        url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={obj.video_id}&key={settings.YOUTUBE_DATA_API_KEY}"
        r = requests.get(url)
        try:
            snippet = r.json()["items"][0]["snippet"]
            snippet = f"""
            <img src='{snippet["thumbnails"]["default"]["url"]}' width="60"/>
            <p style="font-size:10px; margin-left: .5rem">{snippet["title"]}</p>
            """
        except IndexError:
            snippet = "Video Url"

        return format_html(
            f"""
            <a target="_blank" style="display:flex; max-width:200px"
            href="https://www.youtube.com/watch?v={obj.video_id}">
            {snippet}
            </a>
        """
        )

    def register_with_wagtail(self):
        @hooks.register("register_permissions")
        def register_permissions():
            return self.get_permissions_for_registration()

        @hooks.register("register_admin_urls")
        def register_admin_urls():
            return self.get_admin_urls_for_registration()

        menu_hook = (
            "register_settings_menu_item"
            if self.add_to_settings_menu
            else "register_admin_menu_item"
        )

        if hasattr(settings, "DOCUMENTS_GROUP") and settings.DOCUMENTS_GROUP is True:
            """
            Hide Documents menu item and create custom documents group
            """

            @hooks.register("construct_main_menu")
            def hide_snippets_menu_item(request, menu_items):
                menu_items[:] = [
                    item for item in menu_items if item.name != "documents"
                ]

            @hooks.register(menu_hook)
            def register_admin_menu_item():
                menu_items = [
                    DocumentsMenuItem(
                        _("Documents"),
                        reverse("wagtaildocs:index"),
                        name="documents",
                        icon_name="doc-full-inverse",
                        order=400,
                    ),
                    self.get_menu_item(),
                ]
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
            """
            Create Transcription menu item
            """

            @hooks.register(menu_hook)
            def register_admin_menu_item():
                return self.get_menu_item()

        # Overriding the explorer page queryset is a somewhat 'niche' / experimental
        # operation, so only attach that hook if we specifically opt into it
        # by returning True from will_modify_explorer_page_queryset
        if self.will_modify_explorer_page_queryset():

            @hooks.register("construct_explorer_page_queryset")
            def construct_explorer_page_queryset(parent_page, queryset, request):
                return self.modify_explorer_page_queryset(
                    parent_page, queryset, request
                )

        self.register_admin_url_finders()


modeladmin_register(TranscriptionAdmin)
