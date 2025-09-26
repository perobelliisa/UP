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
            document.getElementById(olho).src = "../static/img/olho-fechado-escuro.png";
        }
    }
}

// Script para fechar mensagens
function fecharMensagem(id) {
    document.getElementById(id).style.display = 'none'

};

// Script para trocar o modo
function toggleModo() {
    /*toggleModo é ativado quando o usuário clica no checkbox e assim é ativada a verificação se esse checkbox está checked ou não
    Caso esteja, é armazenado que o modo é o escuro no localStorage e, caso não, é armazenado que o modo é o claro*/
    const checkbox = document.querySelector('.switch input');

    if (checkbox.checked) {
        // modo escuro
        localStorage.setItem('modo', 'escuro'); /*armazer na localstorege que o modo é o escuro*/
        document.getElementById('modo').innerText = 'Escuro'; /*verificar se está no modo escuro , para ficar escrito escuro do lado do botão*/
    } else {
        // modo claro
        localStorage.setItem('modo', 'claro');
        document.getElementById('modo').innerText = 'Claro'; /*verificar se está no modo claro, para ficar escrito claro do lado do botão*/
    }

    carregarModo();
}


function carregarModo() /* so aqui vai  fazer a verificação do modo para mudar as variaveis  do modo claro para o modo escuro*/ {
    const root = document.documentElement; /* root pega tudo que esta no html*/
    const modo = localStorage.getItem('modo'); /*estou procurando o que eu salvei como modo no meu localstorege*/
    const checkbox = document.querySelector('.switch input');

    if (modo === 'escuro') /*modificar as variaveis de cor do modo claro para o modo escuro*/ {
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
        root.style.setProperty('--linha', '#4C2F26');
        root.setAttribute('data-modo', 'escuro');
        document.getElementById('email').src = "../static/img/email-icone-claro.png"; /*aqui estou dizendo que tem email em todas as paginas(rodape) icone, para mudar quando estiver no mdo escuro para o icone claro*/
        if (document.getElementById('banner')) {
            document.getElementById('banner').style.backgroundImage = "url('../static/img/fundoescuro.png')"; /* vai verificar o banner, pois nao é o mesmo banner para o modo claro e modo escuro, estnao aqui vai mudar para o banner do modo escuro*/
        }
        /* IF VERIFICA SE O ID QUE VC QUER MEXER EXISTE NAQUELA PÁGINA PARA O JAVA SCRIPTH NÃO TRAVAR*/

        if (document.getElementById('faq')) {
            document.getElementById('faq').style.backgroundImage = "url('../static/img/fundoescuro.png')"; /* pq o fundo aqui tambem é no modo escuro, pois não é o mesmo para o modo claro e o modo escuro*/
        }

        if (document.getElementById('olho')) {
            document.getElementById('olho').src = "../static/img/olho-fechado-claro.png";
        }
        /*PARA VERFICAR SE O ELEMENTO QUE EU VOU MEXER  EXISTE NAQUELA PÁGINA*/

        if (document.getElementById('olhoC')) {
            document.getElementById('olhoC').src = "../static/img/olho-fechado-claro.png";
        }
        /*NÃO PODE TER DOIS ELEMENTOS COM A MESMA ID, TEM EM ALGUMAS PAGINA QUE SO TENHA SENHA OU SO CONFIRMAR SENHA, POR ISSO É SEPARADO*/

        if (checkbox) {
            checkbox.checked = true;
            document.getElementById('modo').innerText = 'Escuro';
        }
        /*PARA GARANTIR QUE A CHECKBOX VAI FICAR MARCADA*/

    } else {
        // modo claro (MUDANCA DAS VARIAVEIS DO MODO ESCURO PARA O MODO CLARO)
        root.style.setProperty('--claro-fundo', '#FEFBF0');
        root.style.setProperty('--claro-texto', '#2D2D2D');
        root.style.setProperty('--claro-menu', '#FEDFCD');
        root.style.setProperty('--claro-botoes', '#FF906E');
        root.style.setProperty('--claro-hover', '#FF5C39');
        root.style.setProperty('--claro-cartoes', '#FFFFFF');
        root.style.setProperty('--claro-depoimentos', '#6C6C6C');
        root.style.setProperty('--fundo-acerto', '#B9FFB9');
        root.style.setProperty('--fundo-erro', '#FFBFBD');
        root.style.setProperty('--linha', '#FEDFCD');
        root.setAttribute('data-modo', 'claro');
        document.getElementById('email').src = "../static/img/email-icone-escuro.png";
        /*O EMAIL NÃO TEM O IF PQ TODAS AS PAGINAS TEM FOOTER, ICONE*/
        if (document.getElementById('banner')) {
            document.getElementById('banner').style.backgroundImage = "url('../static/img/fundoclaro.png')"; /* vai verificar o banner, pois nao é o mesmo banner para o modo claro e modo escuro, estão aqui vai mudar para o banner do modo claro*/
        }

        if (document.getElementById('faq')) {
            document.getElementById('faq').style.backgroundImage = "url('../static/img/fundoclaro.png')"; /* pq o fundo aqui tambem é no modo claro, pois não é o mesmo para o modo claro e o modo escuro*/
        }

        if (document.getElementById('olho')) {
            document.getElementById('olho').src = "../static/img/olho-fechado-escuro.png";
        }
        /*PARA VERFICAR SE O ELEMENTO QUE EU VOU MEXER  EXISTE NAQUELA PÁGINA*/

        if (document.getElementById('olhoC')) {
            document.getElementById('olhoC').src = "../static/img/olho-fechado-escuro.png";
        }
        /*NÃO PODE TER DOIS ELEMENTOS COM A MESMA ID, TEM EM ALGUMAS PAGINA QUE SO TENHA SENHA OU SO CONFIRMAR SENHA, POR ISSO É SEPARADO, pois se não  vai travar*/

        if (checkbox) {
            checkbox.checked = false;
            document.getElementById('modo').innerText = 'Claro';
        }
        /*PARA GARANTIR QUE A CHECKBOX VAI FICAR MARCADA, mesmo que eu sair do site vai ficar selecionado aquela opcção que eu marquei*/
    }
}

window.document.addEventListener('DOMContentLoaded', carregarModo); 
/*sempre que abrir uma janela ele carregar o modo*/