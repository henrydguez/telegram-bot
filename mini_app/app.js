const tg = window.Telegram?.WebApp;
const STORAGE_KEY = 'financial_movements_v1';

if (tg) {
  tg.ready();
  tg.expand();
  tg.setHeaderColor('#0b3d91');
  tg.setBackgroundColor('#ffffff');
}

const menu = document.getElementById('menu');

const notify = (message) => {
  if (tg?.showAlert) tg.showAlert(message);
  else alert(message);
};

const getMovements = () => {
  try {
    const data = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    return Array.isArray(data) ? data : [];
  } catch { return []; }
};

const saveMovements = (movements) => localStorage.setItem(STORAGE_KEY, JSON.stringify(movements));
const formatMoney = (value) => new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(value);
const formatDate = (value) => {
  if (!value) return '';
  const [year, month, day] = value.split('-');
  return `${day}/${month}/${year}`;
};
const escapeHtml = (value) => String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#039;');

const renderSummary = () => {
  const movements = getMovements();
  const income = movements.filter((m) => m.type === 'income').reduce((sum, m) => sum + m.amount, 0);
  const expense = movements.filter((m) => m.type === 'expense').reduce((sum, m) => sum + m.amount, 0);
  return `<section class="summary" aria-label="Resumen financiero">
    <div class="summary-card"><small>Ingresos</small><strong>${formatMoney(income)}</strong></div>
    <div class="summary-card"><small>Gastos</small><strong>${formatMoney(expense)}</strong></div>
    <div class="summary-card summary-balance"><small>Saldo</small><strong>${formatMoney(income - expense)}</strong></div>
  </section>`;
};

const renderMovementList = () => {
  const movements = getMovements().sort((a, b) => `${b.date}${b.createdAt}`.localeCompare(`${a.date}${a.createdAt}`));
  if (!movements.length) return '<section class="movements"><div class="empty-state">Aún no hay movimientos registrados.</div></section>';
  return `<section class="movements" aria-label="Movimientos registrados">
    <div class="section-title"><h2>Movimientos</h2><span>${movements.length}</span></div>
    <div class="movement-list">${movements.map((movement) => `<article class="movement-item">
      <div class="movement-icon ${movement.type}">${movement.type === 'income' ? '+' : '−'}</div>
      <div class="movement-info"><strong>${escapeHtml(movement.category)}</strong><small>${formatDate(movement.date)}${movement.description ? ` · ${escapeHtml(movement.description)}` : ''}</small></div>
      <div class="movement-amount ${movement.type}">${movement.type === 'income' ? '+' : '−'}${formatMoney(movement.amount)}</div>
    </article>`).join('')}</div>
  </section>`;
};

const renderMovementMenu = () => {
  menu.innerHTML = `<button class="back-button" id="back-home" type="button"><span>‹</span> Atrás</button>
    ${renderSummary()}
    <section class="movement-actions" aria-label="Registrar movimiento">
      <button class="action-tile income-tile" id="income" type="button"><span class="tile-icon">＋</span><strong>Ingreso</strong><small>Registrar dinero recibido</small></button>
      <button class="action-tile expense-tile" id="expense" type="button"><span class="tile-icon">−</span><strong>Gastos</strong><small>Registrar dinero gastado</small></button>
    </section>
    ${renderMovementList()}`;

  document.getElementById('back-home').addEventListener('click', renderHome);
  document.getElementById('income').addEventListener('click', () => renderForm('income'));
  document.getElementById('expense').addEventListener('click', () => renderForm('expense'));
};

const renderForm = (type) => {
  const isIncome = type === 'income';
  const categories = isIncome ? ['Nómina', 'Freelance', 'Ventas', 'Inversiones', 'Otros'] : ['Vivienda', 'Alimentación', 'Transporte', 'Salud', 'Ocio', 'Compras', 'Servicios', 'Otros'];
  menu.innerHTML = `<button class="back-button" id="back-movements" type="button"><span>‹</span> Atrás</button>
    <section class="form-card ${type}-form">
      <div class="form-heading"><div class="form-icon ${type}">${isIncome ? '+' : '−'}</div><div><p class="eyebrow-dark">NUEVO MOVIMIENTO</p><h2>${isIncome ? 'Registrar ingreso' : 'Registrar gasto'}</h2></div></div>
      <form id="movement-form">
        <label>Importe <span>€</span><input id="amount" name="amount" type="number" min="0.01" step="0.01" inputmode="decimal" placeholder="0,00" required autofocus></label>
        <label>Fecha <input id="date" name="date" type="date" required></label>
        <label>Categoría<select id="category" name="category" required><option value="" selected disabled>Selecciona una categoría</option>${categories.map((category) => `<option value="${category}">${category}</option>`).join('')}</select></label>
        <label>Descripción <span>opcional</span><textarea id="description" name="description" rows="3" maxlength="160" placeholder="Añade una descripción"></textarea></label>
        <button class="primary-button ${type}" type="submit">Guardar movimiento</button>
      </form>
    </section>`;

  document.getElementById('date').value = new Date().toISOString().slice(0, 10);
  document.getElementById('back-movements').addEventListener('click', renderMovementMenu);
  document.getElementById('movement-form').addEventListener('submit', (event) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const amount = Number(String(form.get('amount')).replace(',', '.'));
    const date = String(form.get('date') || '');
    const category = String(form.get('category') || '');
    const description = String(form.get('description') || '').trim();
    if (!Number.isFinite(amount) || amount <= 0 || !date || !category) { notify('Completa el importe, la fecha y la categoría con valores válidos.'); return; }
    const movements = getMovements();
    movements.push({ id: crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`, type, amount: Math.round(amount * 100) / 100, date, category, description, createdAt: new Date().toISOString() });
    saveMovements(movements);
    renderMovementMenu();
    notify(`${isIncome ? 'Ingreso' : 'Gasto'} guardado correctamente.`);
  });
};

const renderHome = () => {
  menu.innerHTML = `<button class="menu-card" id="gastos" type="button"><span class="icon">↕</span><span class="card-text"><strong>Control de gastos</strong><small>Registra y organiza tus movimientos</small></span><span class="arrow">›</span></button>
    <button class="menu-card" id="informes" type="button"><span class="icon">▥</span><span class="card-text"><strong>Informes</strong><small>Consulta el resumen de tus finanzas</small></span><span class="arrow">›</span></button>`;
  bindHomeEvents();
};

const bindHomeEvents = () => {
  document.getElementById('gastos').addEventListener('click', renderMovementMenu);
  document.getElementById('informes').addEventListener('click', () => notify('Informes: módulo preparado para la siguiente fase.'));
};

bindHomeEvents();
