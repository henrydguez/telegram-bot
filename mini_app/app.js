const tg = window.Telegram?.WebApp;

if (tg) {
  tg.ready();
  tg.expand();
  tg.setHeaderColor('#0b3d91');
  tg.setBackgroundColor('#f5f8fd');
}

const notify = (message) => {
  if (tg?.showAlert) tg.showAlert(message);
  else alert(message);
};

const openMovementType = (type) => {
  notify(type === 'income'
    ? 'Ingreso seleccionado. Aquí construiremos el registro de ingresos.'
    : 'Gasto seleccionado. Aquí construiremos el registro de gastos.');
};

document.getElementById('gastos').addEventListener('click', () => {
  const menu = document.querySelector('.menu');
  menu.innerHTML = `
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

  document.getElementById('income').addEventListener('click', () => openMovementType('income'));
  document.getElementById('expense').addEventListener('click', () => openMovementType('expense'));
});

document.getElementById('informes').addEventListener('click', () => {
  notify('Informes: módulo preparado para la siguiente fase.');
});
