// Автоматически скрываем alerts через 5 секунд
document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(function () { alert.remove(); }, 500);
        }, 5000);
    });
});

// ===== DRAG & DROP СОРТИРОВКА =====
function initSortable(listId, reorderUrl) {
    const el = document.getElementById(listId);
    if (!el) return;

    Sortable.create(el, {
        handle: '.drag-handle',
        animation: 150,
        ghostClass: 'sortable-ghost',
        onEnd: function () {
            const items = el.querySelectorAll('[data-id]');
            const order = Array.from(items).map(function (item) {
                return item.getAttribute('data-id');
            });

            fetch(reorderUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({ order: order }),
            })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.ok) {
                    console.error('Ошибка сохранения порядка');
                }
            });
        }
    });
}

function getCookie(name) {
    let value = null;
    document.cookie.split(';').forEach(function (c) {
        c = c.trim();
        if (c.startsWith(name + '=')) {
            value = decodeURIComponent(c.slice(name.length + 1));
        }
    });
    return value;
}