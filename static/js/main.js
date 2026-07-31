// Auto-dismiss flash messages after 5 seconds
document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.flash-message');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = 'opacity 0.3s';
            alert.style.opacity = '0';
            setTimeout(function () { alert.remove(); }, 300);
        }, 5000);
    });
});

// Loading state on form submit — disables submit button to prevent double-clicks
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('form').forEach(function (form) {
        form.addEventListener('submit', function () {
            var btn = form.querySelector('button[type="submit"]');
            if (btn && !btn.disabled) {
                btn.disabled = true;
                btn.dataset.originalText = btn.textContent;
                btn.textContent = 'Memproses...';
            }
        });
    });
});

// Mobile menu toggle
document.addEventListener('DOMContentLoaded', function () {
    var menuBtn = document.getElementById('mobile-menu-btn');
    var menu = document.getElementById('mobile-menu');
    if (menuBtn && menu) {
        menuBtn.addEventListener('click', function () {
            menu.classList.toggle('hidden');
        });
    }
});

// Dark mode toggle
(function () {
    var THEME_KEY = 'dishub-theme';

    function getPreferredTheme() {
        var stored = localStorage.getItem(THEME_KEY);
        if (stored) return stored;
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dishub-dark' : 'dishub';
    }

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        updateIcons(theme);
    }

    function updateIcons(theme) {
        var sunIcons = document.querySelectorAll('.theme-icon-sun');
        var moonIcons = document.querySelectorAll('.theme-icon-moon');
        var isDark = theme === 'dishub-dark';
        sunIcons.forEach(function (el) { el.classList.toggle('hidden', isDark); });
        moonIcons.forEach(function (el) { el.classList.toggle('hidden', !isDark); });
    }

    // Apply immediately
    var theme = getPreferredTheme();
    applyTheme(theme);

    document.addEventListener('DOMContentLoaded', function () {
        // Wire up toggle buttons
        var toggleBtns = document.querySelectorAll('.theme-toggle-btn');
        toggleBtns.forEach(function (btn) {
            btn.addEventListener('click', function () {
                var current = document.documentElement.getAttribute('data-theme') || 'dishub';
                var next = current === 'dishub' ? 'dishub-dark' : 'dishub';
                localStorage.setItem(THEME_KEY, next);
                applyTheme(next);
            });
        });

        // Also update icons on DOMContentLoaded in case they weren't ready
        updateIcons(theme);
    });
})();
