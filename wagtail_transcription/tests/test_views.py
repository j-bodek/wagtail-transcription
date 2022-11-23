from wagtail_transcription.models import Transcription
from wagtail_transcription.wagtail_hooks import TranscriptionAdmin
from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.urls.base import reverse
from notifications.signals import notify
from notifications.models import Notification

class TestViews(TestCase):
    def setUp(self):
        # create new superuser
        self.superuser = User.objects.create_superuser(username='superuser', email='superuser@gmail.com')
        self.superuser.set_password('superuser123')
        self.superuser.save()
        # login superuser
        self.logged_in_superuser = Client()
        self.logged_in_superuser.login(username='superuser', password='superuser123')

        # create new regular user
        self.user = User.objects.create(username='user')
        self.user.set_password('user123')
        self.user.save()
        # login regular user
        self.logged_in_user = Client()
        self.logged_in_user.login(username='user', password='user123')

        self.notification = notify.send(sender=self.superuser, recipient=self.superuser, verb="Message", description="Notification")[0][1][0]
        self.transcription = Transcription(
            title='Valid Transcription',
            video_id='aaaaaaaaaaa',
            file="file.docx",
        )
        self.transcription.save()


    def check_if_regular_user_have_access(self, url):
        r = self.logged_in_user.get(url)
        self.assertEqual(r.status_code, 302)
        r = self.logged_in_user.post(url)
        self.assertEqual(r.status_code, 302)

    def test_delete_notification_view(self):
        url = reverse("wagtail_transcription:delete_notification")
        self.check_if_regular_user_have_access(url)
        # try with existing notification
        r = self.logged_in_superuser.post(url, data={'notification_id': self.notification.id})
        self.assertEqual(r.json().get('message'), 'Successfully deleted notification')
        self.assertNotIn(self.notification.id, Notification.objects.all().values_list('id', flat=True))
        # try with non existing notification
        r = self.logged_in_superuser.post(url, data={'notification_id': self.notification.id + 100})
        self.assertEqual(r.json().get('message'), 'Notification does not exist')

    def test_get_processing_transcriptions_view(self):
        url = reverse("wagtail_transcription:processing_transcriptions")
        self.check_if_regular_user_have_access(url)
        r = self.logged_in_superuser.get(url)
        self.assertEqual(r.json().get(self.transcription.video_id), True)
        self.transcription.completed = True
        self.transcription.save()
        r = self.logged_in_superuser.get(url)
        self.assertEqual(r.json().get(self.transcription.video_id), None)

    def test_get_transcription_data_view(self):
        url = reverse("wagtail_transcription:transcription_data")
        self.check_if_regular_user_have_access(url)
        # try with invalid video_id
        r = self.logged_in_superuser.get(url, data={"video_id":"too_short"})
        self.assertEqual(len(set([v for k, v in r.json().items()])), 1)
        self.assertIn(None, list(r.json().values()))
        # try with existing and non existing video_id
        r = self.logged_in_superuser.get(url, data={"video_id":"bbbbbbbbbbb"})
        self.assertEqual(r.status_code, 404)
        r = self.logged_in_superuser.get(url, data={'video_id': self.transcription.video_id})
        r_json = r.json()
        self.assertEqual(r_json.get('new_transcription_id'), self.transcription.id)
        self.assertEqual(r_json.get('new_transcription_title'), self.transcription.title)
        self.assertEqual(r_json.get('new_transcription_edit_url'), TranscriptionAdmin().url_helper.get_action_url("edit", self.transcription.id))
