const msgbox = document.querySelectorAll(".msgbox")
const user_name = document.querySelectorAll(".user_name")


user_name.forEach((el, i) => {
    msgbox[i].style.display = 'none';
    el.addEventListener('click', () => {
        msgbox[i].style.display = 'block';
    })
})