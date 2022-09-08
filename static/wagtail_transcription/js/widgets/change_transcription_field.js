
function ChangeTranscription(transcription_btn, video_id){
    fetch(transcription_btn.dataset.transcription_data_url + '?' + new URLSearchParams({video_id:video_id}) ,{
        method: 'GET',
    })
    .then(response => response.json())
    .then(r => {
        let transcription_field_id = transcription_btn.dataset.transcription_field_id;
        let new_transcription_id = r.new_transcription_id;
        let new_transcription_title = r.new_transcription_title;
        let new_transcription_edit_url = r.new_transcription_edit_url;
        let transcription_field = document.getElementById(transcription_field_id);
        if (transcription_field && new_transcription_id && transcription_field.value != new_transcription_id){
            transcription_field.value = new_transcription_id;
            transcription_field.parentNode.querySelector('.title').innerHTML = new_transcription_title;
            transcription_field.parentNode.querySelector('.chooser').classList.remove('blank');
            transcription_field.parentNode.querySelector('a.edit-link').href = new_transcription_edit_url;
        }
    });
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
            }else if(r[btn.parentNode.querySelector('input').value] != true && btn.dataset.active == 'false'){
                btn.innerHTML = 'Auto Transcription';
                delete btn.dataset.active;
                let video_id = btn.parentNode.querySelector('input').value;
                ChangeTranscription(btn, video_id);
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