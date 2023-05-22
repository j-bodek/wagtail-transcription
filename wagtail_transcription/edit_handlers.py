from wagtail.admin.panels import FieldPanel
from .widgets import AutoVideoTranscriptionWidget


class VideoTranscriptionPanel(FieldPanel):
    def __init__(
        self,
        field_name,
        transcription_field="transcription",
        custom_class="",
        custom_css=None,
        custom_js=None,
        **kwargs
    ):
        super().__init__(field_name, **kwargs)
        self.transcription_field = transcription_field
        self.custom_class = custom_class
        self.custom_css = custom_css
        self.custom_js = custom_js

    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs.update(
            transcription_field=self.transcription_field,
            custom_class=self.custom_class,
            custom_css=self.custom_css,
            custom_js=self.custom_js,
        )
        return kwargs

    def get_form_options(self):
        """
        Overwrite default widget
        """
        options = super().get_form_options()
        # if user does not specify custom widget
        if not self.widget:
            options["widgets"] = {
                self.field_name: AutoVideoTranscriptionWidget(),
            }

        # add transcription_field to widget attrs
        options["widgets"][self.field_name].attrs.update(
            {"transcription_field": self.transcription_field}
        )
        # add custom widget class, css, js
        options["widgets"][self.field_name].attrs.update(
            {"custom_class": self.custom_class}
        )
        options["widgets"][self.field_name].attrs.update(
            {"custom_css": self.custom_css}
        )
        options["widgets"][self.field_name].attrs.update({"custom_js": self.custom_js})
        return options

    class BoundPanel(FieldPanel.BoundPanel):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            try:
                transcription_bound_field = self.form[self.panel.transcription_field]
                self.transcription_field_id = (
                    transcription_bound_field.field.widget.attrs.get("id")
                    or transcription_bound_field.auto_id
                )
            except KeyError:
                self.transcription_field_id = None

        def render_as_field(self):
            """
            Overwrite default method to add instance and field_name to widget attrs
            """
            self.bound_field.field.widget.attrs.update({"instance": self.instance})
            self.bound_field.field.widget.attrs.update({"field_name": self.field_name})
            self.bound_field.field.widget.attrs.update(
                {"transcription_field_id": self.transcription_field_id}
            )
            return super().render_as_field()

        def get_context_data(self, parent_context=None):
            """
            For wagtail version >= 4
            """
            self.bound_field.field.widget.attrs.update({"instance": self.instance})
            self.bound_field.field.widget.attrs.update({"field_name": self.field_name})
            self.bound_field.field.widget.attrs.update(
                {"transcription_field_id": self.transcription_field_id}
            )
            return super().get_context_data(parent_context)
