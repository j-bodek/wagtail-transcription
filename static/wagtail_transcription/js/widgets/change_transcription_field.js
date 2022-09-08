function ChangeTranscription(transcription_field_id, new_transcription_id, new_transcription_title, new_transcription_edit_url){
    let transcription_field = document.getElementById(transcription_field_id);
    if (transcription_field && transcription_field.value != new_transcription_id){
        transcription_field.value = new_transcription_id;
        transcription_field.parentNode.querySelector('.title').innerHTML = new_transcription_title;
        transcription_field.parentNode.querySelector('.chooser').classList.remove('blank');
        transcription_field.parentNode.querySelector('a.edit-link').href = new_transcription_edit_url;
    }
}

function CheckNewAndRunningTranscriptions(transcription_btns){
    fetch(processing_transcriptions_url ,{
        method: 'GET',
    })
    .then(response => response.json())
    .then(r => {
        transcription_btns.forEach(btn => {
            if(r[btn.parentNode.querySelector('input').value] == true){
                btn.innerHTML = 'Transcription in process ...';
                btn.dataset.active = false;
            }
        })
    });
}

document.addEventListener("DOMContentLoaded", () => {
    let transcription_btns = document.querySelectorAll("[name='auto-transcription-btn']");

    CheckNewAndRunningTranscriptions(transcription_btns);
    setInterval(function() {
        CheckNewAndRunningTranscriptions(transcription_btns);
    }, 15000)
});