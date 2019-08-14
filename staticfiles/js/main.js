var pusher = new Pusher('b8eda2b75c1b1e5efd54', {
    cluster: 'ap2',
    forceTLS: true
  });



function isEmpty(obj) {
    return Object.keys(obj).length === 0;
}
const divEl = document.querySelector('.new_message_box');
const sup = document.querySelector('#notify');


let count = 1
let notifications = []
var channel = pusher.subscribe('my-channel');
channel.bind('an-event', function(data) {
    let json = JSON.stringify(data)
    let obj  = JSON.parse(json)
    notifications.push(obj)
    if (notifications.length>0){
        sup.classList.add('icon')
        sup.textContent = notifications.length

        for(let i=0; i<notifications.length;i++){
            const pElement = document.createElement('p')
            pElement.appendChild(document.createTextNode(notifications[i].message))
            divEl.appendChild(pElement)
        }

        

    }else{
        sup.classList.remove('icon')
        
    }

    
});