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

document.getElementById('gastos').addEventListener('click', () => {
  notify('Control de gastos: módulo preparado para la siguiente fase.');
});

document.getElementById('informes').addEventListener('click', () => {
  notify('Informes: módulo preparado para la siguiente fase.');
});
