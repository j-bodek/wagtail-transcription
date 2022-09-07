document.addEventListener("DOMContentLoaded", () => {
    let fetch_message = document.getElementById('fetch_message');
    fetch_message.querySelector('.close_btn').addEventListener('click', (e) =>{
        fetch_message.classList.toggle('hide');
    });
});