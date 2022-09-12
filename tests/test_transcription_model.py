from wagtail.tests.utils import WagtailPageTests
from wagtail_transcription.models import Transcription
from django.core.validators import ValidationError

class TestTranscriptionModel(WagtailPageTests):
    def setUp(self):
        Transcription.objects.create(
            title='Valid Transcription',
            video_id='aaaaaaaaaaa'
        )

    def test_create_transcription_with_invalid_video_id(self):
        transcription = Transcription(
            title='Valid Transcription',
            video_id='too_short'
        )
        try:
            transcription.clean()
        except ValidationError as e:
            self.assertTrue(transcription.video_id in str(e))

    def test_create_transcription_with_invalid_transcription_file(self):
        transcription = Transcription(
            title='Valid Transcription',
            video_id='aaaaaaaaaaa',
            file='transcription.txt'
        )
        try:
            transcription.clean()
            self.fail('Expected ValidationError')
        except ValidationError as e:
            self.assertTrue('txt' in str(e))

    def test_create_transcription_with_valid_data(self):
        transcription = Transcription(
            title='Valid Transcription',
            video_id='aaaaaaaaaaa',
            file='transcription.docx'
        )
        transcription.clean()

    def test_can_delete_transcription(self):
        transcription_num_before_delete = Transcription.objects.all().count()
        Transcription.objects.get(title='Valid Transcription').delete()
        self.assertEqual(transcription_num_before_delete - 1, Transcription.objects.all().count())


