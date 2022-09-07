from wagtail.documents.models import Document
import re
import urllib
from django.apps import apps
from PIL import ImageFile
from django.urls import reverse

class TranscriptionDataValidationMixin:
    def data_validation(self, video_id, model_instance_str, transcription_field):
        
        # get app name, model name and instance id and check if it exists
        try:
            app, model, instance_id = model_instance_str.split(':')
            model_instance = apps.get_model(app, model).objects.get(id=str(instance_id))
            # check if model_instance has transcription_field field
            getattr(model_instance, transcription_field)
        except (AttributeError, ValueError, LookupError):
            # If there is error independent from user display easy error message
            return False, {"type": "error", "message":f'Something went wrong. Please try again or upload transcription manually'}, None

        # check if video id is valid
        yt_id_regex = re.compile(r'^[a-zA-Z0-9_-]{11}$')
        if not yt_id_regex.match(video_id):
            return False, {"type": "error", "message":f'Invalid youtube video id. Make sure it have exactly 11 characters, contains only numbers, letters or dashes'}, model_instance
        
        # check if transcription for video with same id exists
        same_video_transcriptions = Document.objects.filter(title__endswith=video_id)
        if same_video_transcriptions.exists():
            return False, {"type": "error", "message":f'Transcription for video with id : "{video_id}" already exists. Check it <a target="_blank" href="{reverse("wagtaildocs:edit", args=(same_video_transcriptions.first().id ,))}">here</a>'}, model_instance

        try:
            yt_thumbnail_url = f"http://img.youtube.com/vi/{video_id}/mqdefault.jpg"
            width, _ = self.get_online_img_size(yt_thumbnail_url)
            # HACK a mq thumbnail has width of 320.
            # if the video does not exist(therefore thumbnail don't exist), a default thumbnail of 120 width is returned.
            if width == 120:
                return False, {"type": "error", "message":f'YouTube video with id : {video_id} does not exist'}, model_instance
        except urllib.error.HTTPError:
            return False, {"type": "error", "message":f'YouTube video with id : {video_id} does not exist'}, model_instance

        return True, {"type": "success"}, model_instance

    def get_online_img_size(self, uri):
        """
        Get image size by it's url (None if not known), return width, height
        """
        file = urllib.request.urlopen(uri)
        size = file.headers.get("content-length")
        if size: size = int(size)
        p = ImageFile.Parser()
        while 1:
            data = file.read(1024)
            if not data:
                break
            p.feed(data)
            if p.image:
                return p.image.size
                break
        file.close()
        return None
