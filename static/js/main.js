// main.js – utilitarios globales
console.log('Sistema Procesional Señor de los Milagros – v1.0');

// ── Menú lateral (sidebar off-canvas) ──
document.addEventListener('DOMContentLoaded', () => {
  const toggle  = document.getElementById('navToggle');
  const sidebar = document.getElementById('sidebarMenu');
  const overlay = document.getElementById('sidebarOverlay');
  if (!toggle || !sidebar || !overlay) return;

  function cerrarMenu() {
    sidebar.classList.remove('open');
    overlay.classList.remove('open');
    toggle.setAttribute('aria-expanded', 'false');
  }

  function abrirMenu() {
    sidebar.classList.add('open');
    overlay.classList.add('open');
    toggle.setAttribute('aria-expanded', 'true');
  }

  toggle.addEventListener('click', () => {
    sidebar.classList.contains('open') ? cerrarMenu() : abrirMenu();
  });

  overlay.addEventListener('click', cerrarMenu);

  sidebar.querySelectorAll('a').forEach(a => a.addEventListener('click', cerrarMenu));

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') cerrarMenu();
  });
});
