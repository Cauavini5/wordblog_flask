const lita = ['CARRÒ']

function normalizeString(str) {
    return str.toLowerCase().replace(/[\W_]+/g, ''); // Remove pontuação e normaliza case
}

if (lita.includes('CARRO')) {
    console.log('yes')
} else {
    console.log('not')
}