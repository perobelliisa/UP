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

if (porcentagem) {
    porcentagem.addEventListener("input", function () {
        var lucro = document.getElementById("lucro");
        document.getElementById("valor").innerText = lucro.value + "%";
    });
}

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
function mostrarSenha(id, olho) {
    const modo = localStorage.getItem('modo');
    if (document.getElementById(id).type === 'password') {
        document.getElementById(id).type = 'text';
        if (modo === 'escuro') {
            document.getElementById(olho).src = "../static/img/olho-aberto-claro.png";
        }
        else {
            document.getElementById(olho).src = "../static/img/olho-aberto-escuro.png";
        }
    }
    else {
        document.getElementById(id).type = 'password';
        if (modo === 'escuro') {
            document.getElementById(olho).src = "../static/img/olho-fechado-claro.png";
        }
        else {
            document.getElementById('olho').src = "../static/img/olho-fechado-escuro.png";
        }
    }
}

// Script para fechar mensagens
function fecharMensagem(id) {
    document.getElementById(id).style.display = 'none'

};

// Script para trocar o modo
function toggleModo() {
    const checkbox = document.querySelector('.switch input');

    if (checkbox.checked) {
        // modo escuro
        localStorage.setItem('modo', 'escuro');
        document.getElementById('modo').innerText = 'Escuro';
    } else {
        // modo claro
        localStorage.setItem('modo', 'claro');
        document.getElementById('modo').innerText = 'Claro';
    }

    carregarModo();
}


function carregarModo() {
    const root = document.documentElement;
    const modo = localStorage.getItem('modo');
    const checkbox = document.querySelector('.switch input');

    if (modo === 'escuro') {
        // modo escuro
        root.style.setProperty('--claro-fundo', '#1A1A1A');
        root.style.setProperty('--claro-texto', '#EDEDED');
        root.style.setProperty('--claro-menu', '#2D2D2D');
        root.style.setProperty('--claro-botoes', '#FF906E')
        root.style.setProperty('--claro-hover', '#FF5C39');
        root.style.setProperty('--claro-cartoes', '#262626');
        root.style.setProperty('--claro-depoimentos', '#6C6C6C');
        root.style.setProperty('--fundo-acerto', '#246024');
        root.style.setProperty('--fundo-erro', '#832B28');
        root.setAttribute('data-modo', 'escuro');
        document.getElementById('email').src = "../static/img/email-icone-claro.png";
        if (document.getElementById('banner')) {
            document.getElementById('banner').style.backgroundImage.src = "../static/img/fundoescuro.png";
        }

        if (document.getElementById('faq')) {
            document.getElementById('faq').style.backgroundImage.src = "../static/img/fundoescuro.png";
        }

        if (document.getElementById('linha-faq')) {
            document.getElementById('linha-faq').style.backgroundColor = "#4C2F26";
        }

        if (document.getElementById('olho')) {
            document.getElementById('olho').src = "../static/img/olho-fechado-claro.png";
        }

        if (document.getElementById('olhoC')) {
            document.getElementById('olhoC').src = "../static/img/olho-fechado-claro.png";
        }

        if (checkbox) {
            checkbox.checked = true;
            document.getElementById('modo').innerText = 'Escuro';
        }
    } else {
        // modo claro
        root.style.setProperty('--claro-fundo', '#FEFBF0');
        root.style.setProperty('--claro-texto', '#2D2D2D');
        root.style.setProperty('--claro-menu', '#FEDFCD');
        root.style.setProperty('--claro-botoes', '#FF906E');
        root.style.setProperty('--claro-hover', '#FF5C39');
        root.style.setProperty('--claro-cartoes', '#FFFFFF');
        root.style.setProperty('--claro-depoimentos', '#6C6C6C');
        root.style.setProperty('--fundo-acerto', '#B9FFB9');
        root.style.setProperty('--fundo-erro', '#FFBFBD');
        root.setAttribute('data-modo', 'claro');
        document.getElementById('email').src = "../static/img/email-icone-escuro.png";
        if (document.getElementById('banner')) {
            document.getElementById('banner').style.backgroundImage.src = "../static/img/fundoclaro.png";
        }

        if (document.getElementById('faq')) {
            document.getElementById('faq').style.backgroundImage.src = "../static/img/fundoclaro.png";
        }

        if (document.getElementById('linha-faq')) {
            document.getElementById('linha-faq').style.backgroundColor = "var(--linha)";
        }

        if (document.getElementById('olho')) {
            document.getElementById('olho').src = "../static/img/olho-fechado-escuro.png";
        }

        if (document.getElementById('olhoC')) {
            document.getElementById('olhoC').src = "../static/img/olho-fechado-escuro.png";
        }

        if (checkbox) {
            checkbox.checked = false;
            document.getElementById('modo').innerText = 'Claro';
        }
    }
}

window.document.addEventListener('DOMContentLoaded', carregarModo);