function custom_fill_notification_list(data) {
    var menus = document.getElementsByClassName(notify_menu_class);
    if (menus) {
        var messages = data.unread_list.map(function (item) {
            message = `
            <div data-notification_id='${item.id}' class="notification-content">
                ${item.description}			    
            </div>
            `        
            return '<li>' + message + '</li>';
        }).join('')

        for (var i = 0; i < menus.length; i++){
            menus[i].innerHTML = messages;
        }
    }
    // listen notification close btn clicked
    listenNotificationClose();
}

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

function deletNotification(notification_id, action_url){
    // create data that will be send
    const CreateData = new FormData();
    CreateData.append("notification_id", notification_id);
    CreateData.append("csrfmiddlewaretoken", getCookie('csrftoken'));

    // send post request to DataView
    fetch(action_url,{
        method: 'POST',
        body:CreateData,
    })
    .then(response => response.json())
    .then(r => {
        console.log(r);
    })
    .catch((error) => {
        console.log(error);
    });
};

function listenNotificationClose(){
    let NotificationCloseBtns = document.querySelectorAll('.notification-close');
    NotificationCloseBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            let notification_id = btn.closest('.notification-content').dataset.notification_id;
            let action_url = btn.dataset.action_url;
            btn.closest('li').style.display = 'none';
            deletNotification(notification_id, action_url);
        })
    })
}
