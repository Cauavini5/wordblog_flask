const bars = document.getElementById('header_logo');
const menu = document.getElementById('menu');
const items = document.getElementById('items')

const Init = () => {
    items.style.display = 'none'
}
Init()

bars.addEventListener('click', () => {
    
    if(menu.classList.contains('menu')) {
        menu.classList.remove('menu')
        items.style.display = 'none'
    } else {
        menu.classList.add('menu')
        items.style.display = 'grid'
        
    }
})