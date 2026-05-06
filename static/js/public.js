// Мобильное меню
function toggleMobileMenu() {
    const menu = document.getElementById('mobileMenu');
    const btn = document.getElementById('burgerBtn');
    menu.classList.toggle('active');
    btn.classList.toggle('active');
}

// Закрываем меню при клике на ссылку
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.mobile-nav-link').forEach(function(link) {
        link.addEventListener('click', function() {
            document.getElementById('mobileMenu').classList.remove('active');
            document.getElementById('burgerBtn').classList.remove('active');
        });
    });

    // Автоскрытие алертов
    document.querySelectorAll('.alert-pub').forEach(function(alert) {
        setTimeout(function() {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(function() { alert.remove(); }, 500);
        }, 5000);
    });
});

// ===== ТЕКСТ + ИЗОБРАЖЕНИЕ =====
var itSliderState = {};

function itSliderInit() {
    document.querySelectorAll('.it-slider').forEach(function(el) {
        var images = el.getAttribute('data-images');
        if (!images) return;
        var id = el.querySelector('[id^="it-slider-img-"]');
        if (!id) return;
        var pk = id.id.replace('it-slider-img-', '');
        itSliderState[pk] = {
            images: images.split(','),
            current: 0,
        };
    });
}

function itSliderGo(pk, index) {
    var state = itSliderState[pk];
    if (!state) return;
    state.current = index;
    document.getElementById('it-slider-img-' + pk).src = '/media/' + state.images[index];
    document.querySelectorAll('#it-slider-dots-' + pk + ' .it-slider-dot').forEach(function(d, i) {
        d.classList.toggle('active', i === index);
    });
}

function itSliderPrev(pk) {
    var state = itSliderState[pk];
    if (!state) return;
    var next = (state.current - 1 + state.images.length) % state.images.length;
    itSliderGo(pk, next);
}

function itSliderNext(pk) {
    var state = itSliderState[pk];
    if (!state) return;
    var next = (state.current + 1) % state.images.length;
    itSliderGo(pk, next);
}

function itGallerySwap(thumb, path) {
    var gallery = thumb.closest('.it-gallery');
    var main    = gallery.querySelector('.it-gallery-main img');
    if (main) main.src = '/media/' + path;
}

document.addEventListener('DOMContentLoaded', itSliderInit);