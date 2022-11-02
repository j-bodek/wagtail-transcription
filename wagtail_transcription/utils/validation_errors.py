from django.utils.html import format_html


class TranscriptionValidationErrors:
    def GENERAL_ERROR_MESSAGE(self, model_instance=None):
        msg = """Something went wrong. 
            Please try again or upload transcription manually"""
        return self.get_full_msg(msg, model_instance)

    def NO_INSTANCE(self, model_instance=None, **kwargs):
        msg = f"""Please create '{kwargs.get('model_name')}' object first. 
        Transcription field doesn't work when creating new instance."""
        return self.get_full_msg(msg, model_instance)

    def INVALID_VIDEO_ID(self, model_instance=None):
        msg = """Invalid youtube video id. 
            Make sure it have exactly 11 characters, 
            contains only numbers, 
            letters or dashes"""
        return self.get_full_msg(msg, model_instance)

    def EXISTING_SAME_VIDEO_TRANSCRIPTION(self, model_instance=None, **kwargs):
        msg = format_html(
            f"""Transcription for video with id : 
                "{kwargs.get("video_id")}" already exists. 
                <span class="continue_btn" style="color:#007d7f; 
                text-decoration:underline; cursor:pointer">
                    Add Existing Transcription
                </span>"""
        )
        return self.get_full_msg(msg, model_instance)

    def TRANSCRIPTION_IS_RUNNING(self, model_instance=None, **kwargs):
        msg = f"""Transcription process for video with id : 
            "{kwargs.get("video_id")}" is currently running"""
        return self.get_full_msg(msg, model_instance)

    def NOT_EXISTING_VIDEO(self, model_instance=None, **kwargs):
        msg = f"""YouTube video with id : {kwargs.get("video_id")}
                does not exist"""
        return self.get_full_msg(msg, model_instance)

    def UNABLE_TO_FIND_AUDIO(self, model_instance=None, **kwargs):
        msg = f"""Unable to find audio for video with id : {kwargs.get("video_id")}.
                Make sure that video is public"""
        return self.get_full_msg(msg, model_instance)

    def get_full_msg(self, msg, model_instance=None):
        return (
            False,
            {
                "class": "error",
                "type": "error",
                "message": msg,
            },
            model_instance,
        )
