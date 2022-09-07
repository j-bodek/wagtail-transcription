document.addEventListener("DOMContentLoaded", () => {
    let transcription_btns = document.querySelectorAll("[name='auto-transcription-btn']");
    let ajax_send = false;

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function getAutoTranscription(fetch_message){
        let form = fetch_message.querySelector("form");
        fetch(form.action ,{
            method: 'POST',
            body: new FormData(form),
        })
        .then(response => response.json())
        .then(r => {
            // if response message is success open edit source page and add source to publication
            console.log(r)
        });
        fetch_message.classList.toggle('hide');
    };
    
    function validateTranscriptionData(transcription_btn, video_id, action_url, model_instance, transcription_field, field_name){
        // create data that will be send
        const CreateData = new FormData();
        CreateData.append("video_id", video_id);
        CreateData.append("model_instance", model_instance);
        CreateData.append("transcription_field", transcription_field);
        CreateData.append("field_name", field_name);
        CreateData.append("edit_url", window.location.href);
        CreateData.append("csrfmiddlewaretoken", getCookie('csrftoken'));

        // set ajax_send to true in order to provide sending another request
        ajax_send = true;
        // send post request to DataView
        fetch(action_url,{
            method: 'POST',
            body:CreateData,
        })
        .then(response => response.json())
        .then(r => {
            transcription_btn.innerHTML = `Auto Transcription`
            // if response message is success open edit source page and add source to publication
            ajax_send = false;
            let fetch_message = document.getElementById('fetch_message');
            fetch_message.className = `fetch_message ${r.type}`;
            fetch_message.querySelector('.fetch_message_content').innerHTML = r.message;
            // listen if continue btn is clicked
            if(r.type == 'success'){
                fetch_message.querySelector('.continue_btn').addEventListener('click', e=>{
                    e.preventDefault();
                    getAutoTranscription(fetch_message);
                });
            };
        })
        .catch((error) => {
            transcription_btn.innerHTML = `Auto Transcription`
            // if error display it
            ajax_send = false;
            console.log(error);
        });
    };
    
    transcription_btns.forEach(btn=>{
        btn.addEventListener('click', e=>{
            let video_id_input = btn.parentNode.querySelector('input');
            let video_id = video_id_input.value;
            let action_url = btn.dataset.action_url;
            let model_instance = btn.dataset.model_instance;
            let transcription_field = btn.dataset.transcription_field;
            let field_name = btn.dataset.field_name;
            btn.innerHTML = `<span class="lds-facebook"><div></div><div></div><div></div></span>`
            if (!ajax_send) {
                validateTranscriptionData(btn, video_id, action_url, model_instance, transcription_field, field_name)
            }
        });
    });
});