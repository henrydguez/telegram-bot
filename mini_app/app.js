const telegram = window.Telegram?.WebApp;

if (telegram) {
  telegram.ready();
  telegram.expand();
}

const user = telegram?.initDataUnsafe?.user;
const saludo = document.getElementById("saludo");
const boton = document.getElementById("accion");
const resultado = document.getElementById("resultado");

if (user?.first_name) {
  saludo.textContent = `Hola, ${user.first_name} 👋`;
}

boton.addEventListener("click", () => {
  resultado.textContent = "¡La Mini App funciona correctamente! 🎉";
  telegram?.HapticFeedback?.notificationOccurred("success");
});
