from django.template import Context, Template
from django.test import TestCase
from wagtail_transcription.models import Transcription

class TestTranscriptionTemplateTags(TestCase):

    def setUp(self):
        self.transcription = Transcription(
            title='Valid Transcription',
            video_id='aaaaaaaaaaa',
            file='file.txt',
        )
        self.transcription.save()

    def render_template(self, string, context=None):
        context = context or {}
        context = Context(context)
        return Template(string).render(context)
    
    def test_get_app_model_id_with_invalid_values(self):
        invalid_values = ['string', 10, 'app:model:1']
        for value in invalid_values:
            rendered = self.render_template(
                '{% load transcription_tags %}'
                '{{ "hello"|get_app_model_id }}'
            )
            if rendered != 'False':
                self.fail(f"get_app_model_id for value {value} should return False")
            
    def test_get_app_model_id_with_valid_value(self):
        rendered = self.render_template(
            '{% load transcription_tags %}'
            '{{ transcription|get_app_model_id }}',
            context = {'transcription':self.transcription}
        )

        if rendered != f'wagtail_transcription:Transcription:{str(self.transcription.id)}':
            self.fail(f"get_app_model_id for value '{self.transcription}' should return 'wagtail_transcription:Transcription:{str(self.transcription.id)}'")
    
