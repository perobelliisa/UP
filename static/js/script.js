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

// Script para mostrar/ocultar card de adição de categoria
function adicionarCategoria() {
    if (document.getElementById("adicionarCategoria").style.display === 'block') {
        document.getElementById("adicionarCategoria").style.display = 'none';
    }
    else {
        document.getElementById("adicionarCategoria").style.display = 'block';
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

// Script para mostrar mensagem de acerto
document.addEventListener("DOMContentLoaded", function() {
    if (window.location.pathname.includes("dashboard.html")) {
        if ( document.getElementById("mensagemAcerto").style.display === 'flex') {
            document.getElementById("mensagemAcerto").style.display = 'none'
        }
        else {
            document.getElementById("mensagemAcerto").style.display = 'flex'
        }
    }
});

// Script para trocar o modo
function toggleModo() {
    const root = document.documentElement;
    const checkbox = document.querySelector('.switch input');

    if (checkbox.checked) {
        // modo escuro
        root.style.setProperty('--claro-fundo', '#1A1A1A');
        root.style.setProperty('--claro-texto', '#EDEDED');
        root.style.setProperty('--claro-menu', '#2D2D2D');
        root.style.setProperty('--claro-botoes', '#FF906E')
        root.style.setProperty('--claro-hover', '#FF5C39');
        root.style.setProperty('--claro-cartoes', '#262626');
        root.style.setProperty('--claro-depoimentos', '#EDEDED');
        root.setAttribute('data-modo', 'escuro');
        localStorage.setItem('modo', 'escuro');
    } else {
        // modo claro
        root.style.setProperty('--claro-fundo', '#FEFBF0');
        root.style.setProperty('--claro-texto', '#2D2D2D');
        root.style.setProperty('--claro-menu', '#FEDFCD');
        root.style.setProperty('--claro-botoes', '#FF906E');
        root.style.setProperty('--claro-hover', '#FF5C39');
        root.style.setProperty('--claro-cartoes', '#FFFFFF');
        root.style.setProperty('--claro-depoimentos', '#6C6C6C');
        root.setAttribute('data-modo', 'claro');
        localStorage.setItem('modo', 'claro');
    }
}

