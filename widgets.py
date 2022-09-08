from django.forms.widgets import Input

class AutoVideoTranscriptionWidget(Input):
    class Media:
        css = {
            "all": (
                "wagtail_transcription/style/widgets/transcription.css",
            )
        }
        js = [
            "wagtail_transcription/js/widgets/change_transcription_field.js",
            "wagtail_transcription/js/widgets/transcription.js",
        ]

    input_type = "text"
    template_name = 'wagtail_transcription/widgets/transcription.html'
