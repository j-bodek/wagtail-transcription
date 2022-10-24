# Wagtail Transcription
[wagtail-transcription](https://pypi.org/project/wagtail-transcription/ "wagtail-transcription") is app for Wagtail that allows to create transcriptions for YouTube videos automatically with just few clicks! To create transcription it use [AssemblyAi](https://www.assemblyai.com/ "AssemblyAi") API.

![transcription_gif](images/transcription_gif.gif)

#### Standard Installation
```
pip install wagtail-transcription
```

#### Installation For Developement
If you want to install wagtail-transcription to develop it clone this repository to your project. After that run
```python
pip install -e path_to_wagtail_transcription_core_folder
```
This will create folder (inside your env lib directory) with json file storing path to wagtail-transcription package. Later setps are the same.


After installation add `wagtail_transcription` and `notifications` to your installed apps:
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
from django.urls import include, path, re_path
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

##### 4. Add YouTube Data API token
In your settings file add **YOUTUBE_DATA_API_KEY**. To create one check [official documentation](https://developers.google.com/youtube/v3/getting-started "official documentation").

```
YOUTUBE_DATA_API_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
```

##### 5. Forward your localhost (developement)
<b style="color:red;">IMPORTANT</b>
After transcription process ends [AssemblyAi](https://www.assemblyai.com/ "AssemblyAi") will send request to one of wagtail-transcription views. To receive it on local server you have to forward your localhost. Best and easiest option is use tunelling service like [localltunnel](https://theboroer.github.io/localtunnel-www/ "localltunnel").

##### 6. Add BASE_URL 
In your settings file add '**BASE_URL = "base_url"**' this is used when sending webhook_url for [AssemblyAi](https://www.assemblyai.com/ "AssemblyAi"). In developement you should set it to forward url. If you use [localltunnel](https://theboroer.github.io/localtunnel-www/ "localltunnel") it will be something like this **'https://your_subdomain.loca.lt'**
```
BASE_URL = "base_url"
```

##### 7. Add DOCUMENTS_GROUP (Optional) 
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
    video_id = models.CharField(max_length=255, blank=True)
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
**VideoTranscriptionPanel** takes five arguments:
- field_name - name of field for video_id
- transcription_field - name of transcription field
- custom_class - class of transcription widget
- custom_css - custom css that will be loaded with transcritpion widget
- custom_js - custom js that will be loaded with transcritpion widget

<b style="color:red;">IMPORTANT</b>
You can only generate a transcript on an existing object, if you try to do this in page creation view you will get an error.

## Customization
To be more comfortable with customization checkout [AssemblyAi Docs](https://www.assemblyai.com/docs/ "AssemblyAi Docs")
#### Add custom Transcription Widget class, css and js
In your VideoTranscriptionPanel add
```
VideoTranscriptionPanel('video_id', transcription_field='transcription', custom_class='custom_transcription', custom_css='app_name/css/custom_transcription.css', custom_js='app_name/js/custom_transcription.js'),
```

#### Add custom RequestTranscriptionView
In your settings add
```
REQUEST_TRANSCRIPTION_VIEW = "app_name.module_name.YourRequestTranscriptionView"
```
You can easily overwrite how request to AssemblyAi is send by overwriteing request_audio_transcription method
```
from wagtail_transcription.views import RequestTranscriptionView
class YourRequestTranscriptionView(RequestTranscriptionView):

    def request_audio_transcription(self, audio_url, webhook_url):
        """
		Your awesome request logic
		"""
        return response
```

#### Add custom ReceiveTranscriptionView
In your settings add
```
RECEIVE_TRANSCRIPTION_VIEW = "app_name.module_name.YourReceiveTranscriptionView"
```
Now you can easily overwrite how request with transcription is processed

```
from wagtail_transcription.views import ReceiveTranscriptionView

class YourReceiveTranscriptionView(ReceiveTranscriptionView):

    def process_transcription_response(self, transcription_response, 	video_id, model_instance_str, field_name, transcription_field):
        """
        transcription_response - AssemblyAi response with transcription data 
        video_id - id of youtube video for which transcription was made
        model_instance_str - string that allow to get model instance "app:model_name:instance_id"
        field_name = name of field with video_id
        transcription_field = name of field for transcription
        """
        ...
		Your transcription processing logic here
		...
		super().process_transcription_response(transcription_response, 	video_id, model_instance_str, field_name, transcription_field)
```
