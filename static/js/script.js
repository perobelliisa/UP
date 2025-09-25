// Script para mostrar/ocultar respostas no FAQ
function mostrarResposta(id) {
    if (document.getElementById(id).style.display === 'block') {
        document.getElementById(id).style.display = 'none'
    }
    else {
        document.getElementById(id).style.display = 'block'
    }
}

// Script para atualizar o valor da barra de lucro
var porcentagem = document.getElementById("lucro");

porcentagem.addEventListener("input", function() {
    var lucro = document.getElementById("lucro");
    document.getElementById("valor").innerText = lucro.value + "%";
});

// Script para mostrar/ocultar card de adição de insumo
function adicionarInsumo() {
    if (document.getElementById("adicionarInsumo").style.display === 'block') {
        document.getElementById("adicionarInsumo").style.display = 'none';
    }
    else {
        document.getElementById("adicionarInsumo").style.display = 'block';
    }
}

// Script para mostrar/ocultar campos de quantidade dos ingredientes
function mostrarQuantidade(id) {
    if (document.getElementById(id).style.display === 'flex') {
        document.getElementById(id).style.display = 'none'
    }
    else {
        document.getElementById(id).style.display = 'flex'
    }
}

// Script para mostrar/ocultar menu mobile
function mostrarMenu(id) {
    if (document.getElementById(id).style.display === 'flex') {
        document.getElementById(id).style.display = 'none';
    }
    else {
        document.getElementById(id).style.display = 'flex';
    }
}

// Script para mostrar/ocultar senha
function mostrarSenha(id) {
    if (document.getElementById(id).type === 'password') {
        document.getElementById(id).type = 'text';
    }
    else {
        document.getElementById(id).type = 'password';
    }
}

