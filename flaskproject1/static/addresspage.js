
const btn = document.getElementById("btn");

btn.addEventListener("click", (ev) => {
    ev.preventDefault()
    const cep = document.getElementById('cep').value;
    if (cep.length === 8) {
        fetch(`https://viacep.com.br/ws/${cep}/json/`)
            .then(response => response.json())
            .then(data => {
                if (!data.erro) {
                    document.getElementById('rua').value = data.logradouro;
                    document.getElementById('cidade').value = data.localidade;
                    document.getElementById('estado').value = data.uf;
                } else {
                    alert("CEP não encontrado!");
                }
            })
            .catch(error => {
                alert("Erro ao buscar o CEP!");
                console.error("Erro:", error);
            });
    } else {
        alert("CEP inválido!");
    }
})

