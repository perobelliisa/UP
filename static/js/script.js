$(document).ready(function(){
    $('.carrossel').owlCarousel({
        loop: true,                  // Permite looping infinito
        margin: 10,                  // Margem entre os itens
        nav: true,                  // Não tem setas de navegação
        responsiveClass: true,       // Ajuste de responsividade
        autoplay: true,              // Ativa o autoplay
        autoplayTimeout: 3000,       // Tempo de troca automática (3000ms = 3 segundos)
        autoplayHoverPause: true,    // Pausa o autoplay quando o mouse está sobre o carrossel
        items: 1,                    
        center: true,                // Centraliza os itens
        autoWidth: false             // Não permite largura automática
    });
});
