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