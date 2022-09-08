function ChangeTranscription(transcription_field_id, new_transcription_id, new_transcription_title, new_transcription_edit_url){
    let transcription_field = document.getElementById(transcription_field_id);
    if (transcription_field.value != new_transcription_id){
        transcription_field.value = new_transcription_id;
        transcription_field.parentNode.querySelector('.title').innerHTML = new_transcription_title;
        transcription_field.parentNode.querySelector('.chooser').classList.remove('blank');
        transcription_field.parentNode.querySelector('a.edit-link').href = new_transcription_edit_url;
    }
}
