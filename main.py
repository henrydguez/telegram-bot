import os
import re
import urllib.request
from decimal import Decimal, InvalidOperation
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("No se encontró BOT_TOKEN en el archivo .env")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! 👋 Soy tu bot de Telegram.")


def obtener_tasa_eur_cop():
    """Obtiene la tasa EUR/COP mostrada por Google Finance."""
    url = "https://www.google.com/finance/quote/EUR-COP?hl=es"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
    )

    with urllib.request.urlopen(request, timeout=10) as response:
        html = response.read().decode("utf-8", errors="ignore")

    # Google Finance suele incluir la cotización en un elemento con clase P6K39c.
    match = re.search(r'class="P6K39c"[^>]*>([0-9.,]+)<', html)
    if not match:
        raise ValueError("No se pudo localizar la tasa EUR/COP en Google Finance")

    valor = match.group(1).replace(",", "")
    return Decimal(valor)


def convertir_moneda(mensaje):
    """Detecta cantidades y convierte entre euros y pesos colombianos."""
    texto = mensaje.lower().replace("€", " euros ").replace("$", " pesos ")

    patron_eur = re.search(
        r"([0-9][0-9.,]*)\s*(?:euros?|eur)\b.*?(?:pesos?|cop)", texto
    )
    patron_cop = re.search(
        r"([0-9][0-9.,]*)\s*(?:pesos?|cop)\b.*?(?:euros?|eur)", texto
    )

    if not patron_eur and not patron_cop:
        return None

    match = patron_eur or patron_cop
    cantidad_texto = match.group(1)

    # Acepta formatos como 1000, 1.000, 1,000 y 1.000,50.
    if "," in cantidad_texto and "." in cantidad_texto:
        if cantidad_texto.rfind(",") > cantidad_texto.rfind("."):
            cantidad_texto = cantidad_texto.replace(".", "").replace(",", ".")
        else:
            cantidad_texto = cantidad_texto.replace(",", "")
    elif "," in cantidad_texto:
        partes = cantidad_texto.split(",")
        cantidad_texto = (
            cantidad_texto.replace(",", "")
            if len(partes[-1]) == 3
            else cantidad_texto.replace(",", ".")
        )
    elif "." in cantidad_texto:
        partes = cantidad_texto.split(".")
        cantidad_texto = (
            cantidad_texto.replace(".", "")
            if len(partes[-1]) == 3
            else cantidad_texto
        )

    try:
        cantidad = Decimal(cantidad_texto)
        if cantidad <= 0:
            return "La cantidad debe ser mayor que cero."
    except InvalidOperation:
        return "No pude entender la cantidad. Prueba, por ejemplo: 100 euros a pesos."

    try:
        tasa = obtener_tasa_eur_cop()
    except Exception:
        return (
            "No pude consultar la tasa actual de Google Finance en este momento. "
            "Inténtalo de nuevo en unos segundos."
        )

    if patron_eur:
        resultado = cantidad * tasa
        return (
            f"💱 {cantidad:,.2f} EUR = {resultado:,.0f} COP\n"
            f"📊 Tasa: 1 EUR = {tasa:,.2f} COP\n"
            "Fuente: Google Finance"
        )

    resultado = cantidad / tasa
    return (
        f"💱 {cantidad:,.0f} COP = {resultado:,.2f} EUR\n"
        f"📊 Tasa: 1 EUR = {tasa:,.2f} COP\n"
        "Fuente: Google Finance"
    )


async def responder_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    mensaje = update.message.text.strip().lower()

    conversion = convertir_moneda(mensaje)
    if conversion:
        await update.message.reply_text(conversion)
        return

    if context.user_data.get("esperando_como_estas"):
        context.user_data["esperando_como_estas"] = False

        if mensaje in ("bien", "bien gracias", "muy bien", "genial", "perfecto"):
            await update.message.reply_text("¿En qué te puedo ayudar?")
        elif mensaje in ("mal", "muy mal", "triste", "regular"):
            await update.message.reply_text("Vaya 😔, espero que mejore tu día.")
        else:
            await update.message.reply_text("Gracias por contármelo 😊 ¿En qué te puedo ayudar?")
        return

    if mensaje == "hola":
        context.user_data["esperando_como_estas"] = True
        await update.message.reply_text("Hola, ¿cómo estás? 😜")
        return

    if mensaje in ("buenos días", "buenos dias"):
        await update.message.reply_text("¡Buenos días! ☀️")
        return

    if mensaje in ("gracias", "muchas gracias"):
        await update.message.reply_text("¡De nada! 😊")
        return


app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder_mensaje))

print("Bot iniciado")
app.run_polling()
