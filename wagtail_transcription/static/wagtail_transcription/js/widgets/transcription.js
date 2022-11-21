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

    function getAutoTranscription(fetch_message, transcription_btn){
        let form = fetch_message.querySelector("form");
        fetch(form.action ,{
            method: 'POST',
            body: new FormData(form),
        })
        .then(response => response.json())
        .then(r => {
            console.log(r)
            if(r.type == 'success'){
                transcription_btn.innerHTML = 'Transcription in process ...'
                transcription_btn.dataset.active = false;
                ListenTranscriptionBtnsClicked();
            }else if(r.type == 'error'){
                let fetch_message = document.getElementById('fetch_message');
                fetch_message.className = `fetch_message ${r.class}`;
                fetch_message.querySelector('.fetch_message_content').innerHTML = r.message;
            }
        });
        fetch_message.classList.toggle('hide');
    };
    
    function validateTranscriptionData(transcription_btn, video_id){
        // create data that will be send
        const CreateData = new FormData();
        CreateData.append("video_id", video_id);
        CreateData.append("parent_instance_str", transcription_btn.dataset.parent_instance_str);
        CreateData.append("transcription_field", transcription_btn.dataset.transcription_field);
        CreateData.append("transcription_field_id", transcription_btn.dataset.transcription_field_id);
        CreateData.append("field_name", transcription_btn.dataset.field_name);
        CreateData.append("csrfmiddlewaretoken", getCookie('csrftoken'));

        // set ajax_send to true in order to provide sending another request
        ajax_send = true;
        // send post request to DataView
        fetch(transcription_btn.dataset.action_url,{
            method: 'POST',
            body:CreateData,
        })
        .then(response => response.json())
        .then(r => {
            transcription_btn.innerHTML = `Auto Transcription`
            // if response message is success open edit source page and add source to publication
            ajax_send = false;
            let fetch_message = document.getElementById('fetch_message');
            fetch_message.className = `fetch_message ${r.class}`;
            fetch_message.querySelector('.fetch_message_content').innerHTML = r.message;
            // listen if continue btn is clicked
            if(r.type == 'success'){
                fetch_message.querySelector('.continue_btn').addEventListener('click', e=>{
                    e.preventDefault();
                    getAutoTranscription(fetch_message, transcription_btn);
                });
            }else if(r.type == 'error-id_exists'){
                fetch_message.querySelector('.continue_btn').addEventListener('click', e=>{
                    fetch_message.classList.toggle('hide');
                    ChangeTranscription(transcription_btn, video_id);
                })
            }
        })
        .catch((error) => {
            transcription_btn.innerHTML = `Auto Transcription`
            // if error display it
            ajax_send = false;
            console.log(error);
        });
    };

    function ListenTranscriptionBtnsClicked(){
        transcription_btns.forEach(btn=>{
            btn.addEventListener('click', e=>{
                if (btn.dataset.active == 'false') return;
    
                let video_id = btn.parentNode.querySelector('input').value;
                btn.innerHTML = `<span class="lds-facebook"><div></div><div></div><div></div></span>`
                if (!ajax_send) {
                    validateTranscriptionData(btn, video_id)
                }
            });
        });
    }

    ListenTranscriptionBtnsClicked();
    
});