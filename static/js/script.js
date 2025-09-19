$(document).ready(function(){
    $(".carrossel-esquerda").owlCarousel({
        loop: true,
        dots: true,
        margin: 30,
        autoplay: true,
        autoplayTimeout: 5000,
        autoplaySpeed: 2000,
        slideTransition: 'linear',
        autoplayHoverPause: true,
        responsive:{
            0:{
                items: 1
            },
            600:{
                items: 2
            },
            1000:{
                items: 2
            }
        }
    });

    $(".carrossel-direita").owlCarousel({
        loop: true,
        dots: true,
        margin: 30,
        autoplay: true,
        autoplayTimeout: 5000,
        autoplaySpeed: 2000,
        slideTransition: 'linear',
        autoplayHoverPause: true,
        rtl: true,
        responsive:{
            0:{
                items: 1
            },
            600:{
                items: 2
            },
            1000:{
                items: 2
            }
        }
    });
});