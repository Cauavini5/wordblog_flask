const logo = document.getElementById("logo")
const messagesDiv = document.getElementById("messages")

messagesDiv.style.display = 'none'
logo.addEventListener('click', () => {
   
    if(messagesDiv.classList.contains('boxmsg')) {
        messagesDiv.style.display = 'none'
        messagesDiv.classList.remove('boxmsg')
    } else {
        messagesDiv.classList.add('boxmsg')
        messagesDiv.style.display = 'block'
    }
})