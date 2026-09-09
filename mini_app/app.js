const tg = window.Telegram?.WebApp;

if (tg) {
  tg.ready();
  tg.expand();
  tg.setHeaderColor('#0b3d91');
  tg.setBackgroundColor('#f5f8fd');
}

const menu = document.getElementById('menu');

const notify = (message) => {
  if (tg?.showAlert) tg.showAlert(message);
  else alert(message);
};

const renderHome = () => {
  menu.innerHTML = `
    <button class="menu-card" id="gastos" type="button">
      <span class="icon">↕</span>
      <span class="card-text"><strong>Control de gastos</strong><small>Registra y organiza tus movimientos</small></span>
      <span class="arrow">›</span>
    </button>
    <button class="menu-card" id="informes" type="button">
      <span class="icon">▥</span>
      <span class="card-text"><strong>Informes</strong><small>Consulta el resumen de tus finanzas</small></span>
      <span class="arrow">›</span>
    </button>
  `;
  bindHomeEvents();
};

const renderMovementMenu = () => {
  menu.innerHTML = `
    <button class="back-button" id="back-home" type="button" aria-label="Volver a la pantalla de inicio">
      <span>‹</span> Atrás
    </button>
    <button class="menu-card" id="income" type="button">
      <span class="icon">＋</span>
      <span class="card-text"><strong>Ingreso</strong><small>Registrar un nuevo ingreso</small></span>
      <span class="arrow">›</span>
    </button>
    <button class="menu-card" id="expense" type="button">
      <span class="icon">−</span>
      <span class="card-text"><strong>Gastos</strong><small>Registrar un nuevo gasto</small></span>
      <span class="arrow">›</span>
    </button>
  `;

  document.getElementById('back-home').addEventListener('click', renderHome);
  document.getElementById('income').addEventListener('click', () => notify('Ingreso seleccionado. Aquí construiremos el registro de ingresos.'));
  document.getElementById('expense').addEventListener('click', () => notify('Gasto seleccionado. Aquí construiremos el registro de gastos.'));
};

const bindHomeEvents = () => {
  document.getElementById('gastos').addEventListener('click', renderMovementMenu);
  document.getElementById('informes').addEventListener('click', () => {
    notify('Informes: módulo preparado para la siguiente fase.');
  });
};

bindHomeEvents();
