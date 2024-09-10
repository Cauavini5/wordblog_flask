const updateBtn = document.querySelectorAll('.updateBtn');
const FormOfUpdate = document.querySelectorAll('.FormOfUpdate');

updateBtn.forEach((el, index) => {
    el.addEventListener('click', (ev) => {
        ev.preventDefault()
        
        FormOfUpdate[index].style.display = 'grid'
    })
})