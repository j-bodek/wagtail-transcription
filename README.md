# Wagtail Transcription
[wagtail-transcription](https://pypi.org/project/wagtail-transcription/ "wagtail-transcription") is app for Wagtail that allows to create transcriptions for YouTube videos automaticlly with just few clicks! To create transcription it use [AssemblyAi](https://www.assemblyai.com/ "AssemblyAi") API.

![transcription_gif](images/transcription_gif.gif)

```
pip install wagtail-transcription
```

Then add `wagtail_transcription` and `notifications` to your installed apps:
***Note: Make sure that 'wagtail_transcription' is added before 'wagtail.admin'. Otherwise, administration page will not work properly***
```
INSTALLED_APPS = [
    ...
    'wagtail_transcription',
	'notifications',
	...
]
```

## SetUp
After installing wagtail-transcription and adding it to installed apps run migrations:
```
python manage.py migrate
```
Then add following to your project urls.py
```
from wagtail_transcription import urls as wagtail_transcription_url
import notifications.urls

urlpatterns = [
	...
    path("wagtail_transcription/", include(wagtail_transcription_url)),
    re_path(r'^inbox/notifications/', include(notifications.urls, namespace='notifications')),
	...
]
```

In your settigns file add '**ASSEMBLY_API_TOKEN**' ([to get it create Assembly Ai account](https://app.assemblyai.com/signup "to get it create Assembly Ai account"))
```
ASSEMBLY_API_TOKEN = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
```

***Optional*** 
In your settings file add '**DOCUMENTS_GROUP = True**'  to create menu group from wagtail documents and transcription
```
DOCUMENTS_GROUP = True
```


## Usage
In model that you want to add dynamically generated transcryption
```
from wagtail_transcription.edit_handlers import VideoTranscriptionPanel
from wagtail_transcription.models import Transcription

class YourModel(Orderable, models.Model):
    video_id = video_id = models.CharField(max_length=255, blank=True)
    transcription = models.ForeignKey(
        Transcription,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        MultiFieldPanel([
            VideoTranscriptionPanel('video_id', transcription_field='transcription'),
            FieldPanel('transcription'),
        ], heading="Video and Transcription"),
    ]
```
**video_id** field accept only youtube video id (not urls). **VideoTranscriptionPanel** takes two arguments:
- field_name - name of field for video_id
- transcription_field - name of transcription field
