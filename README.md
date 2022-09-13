# Wagtail Transcription
[wagtail-transcription](https://pypi.org/project/wagtail-transcription/ "wagtail-transcription") is app for Wagtail that allows to create transcriptions for YouTube videos automatically with just few clicks! To create transcription it use [AssemblyAi](https://www.assemblyai.com/ "AssemblyAi") API.

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
##### 1. Run migrations
After installing wagtail-transcription and adding it to installed apps run migrations:
```
python manage.py migrate
```

##### 2. Add wagtail-transcription urls
Add following to your project urls.py
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


##### 3. Add ASSEMBLY_API_TOKEN
In your settigns file add '**ASSEMBLY_API_TOKEN**' ([to get it create Assembly Ai account](https://app.assemblyai.com/signup "to get it create Assembly Ai account"))
```
ASSEMBLY_API_TOKEN = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
```


##### 4. Forward your localhost (developement)
<b style="color:red;">IMPORTANT</b>
After transcription process ends [AssemblyAi](https://www.assemblyai.com/ "AssemblyAi") will send request to one of wagtail-transcription views. To receive it on local server you have to forward your localhost. Best and easiest option is use tunelling service like [localltunnel](https://theboroer.github.io/localtunnel-www/ "localltunnel").

##### 5. Add BASE_URL 
In your settings file add '**BASE_URL = "base_url"**' this is used when sending webhook_url for [AssemblyAi](https://www.assemblyai.com/ "AssemblyAi"). In developement you should set it to forward url. If you use [localltunnel](https://theboroer.github.io/localtunnel-www/ "localltunnel") it will be something like this **'https://your_subdomain.loca.lt'**
```
BASE_URL = "base_url"
```

##### 6. Add DOCUMENTS_GROUP (Optional) 
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
**video_id** field accept only youtube video id (not urls).<br/>
**VideoTranscriptionPanel** takes two arguments:
- field_name - name of field for video_id
- transcription_field - name of transcription field

<b style="color:red;">IMPORTANT</b>
You can only generate a transcript on an existing object, if you try to do this in page creation view you will get an error.

