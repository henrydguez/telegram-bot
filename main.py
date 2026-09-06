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
    """Obtiene la cotización EUR/COP visible en Google Finance."""
    url = "https://www.google.com/finance/quote/EUR-COP?hl=es"
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    with urllib.request.urlopen(request, timeout=10) as response:
        html = response.read().decode("utf-8", errors="ignore")

    patrones = [
        r"EUR\s*/\s*COP.{0,5000}?([0-9]{1,3}(?:[.,][0-9]{3})+(?:[.,][0-9]+)?)",
        r"Euro\s*/\s*Peso colombiano.{0,5000}?([0-9]{1,3}(?:[.,][0-9]{3})+(?:[.,][0-9]+)?)",
        r'class="P6K39c"[^>]*>([0-9.,]+)<',
    ]

    valor_texto = None
    for patron in patrones:
        match = re.search(patron, html, re.IGNORECASE | re.DOTALL)
        if match:
            valor_texto = match.group(1)
            break

    if not valor_texto:
        raise ValueError("No se pudo localizar la tasa EUR/COP en Google Finance")

    if "," in valor_texto and "." in valor_texto:
        valor_texto = valor_texto.replace(".", "").replace(",", ".")
    elif "," in valor_texto:
        valor_texto = valor_texto.replace(",", ".")
    elif valor_texto.count(".") > 1:
        valor_texto = valor_texto.replace(".", "")

    tasa = Decimal(valor_texto)
    if tasa <= 0:
        raise ValueError("La tasa obtenida no es válida")
    return tasa


def parsear_cantidad(texto):
    """Convierte cantidades españolas como 1000, 1.000 o 1.000,50 a Decimal."""
    texto = texto.strip()
    if "," in texto and "." in texto:
        if texto.rfind(",") > texto.rfind("."):
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", "")
    elif "," in texto:
        partes = texto.split(",")
        texto = texto.replace(",", ".") if len(partes[-1]) != 3 else texto.replace(",", "")
    elif "." in texto:
        partes = texto.split(".")
        if len(partes[-1]) == 3:
            texto = texto.replace(".", "")

    return Decimal(texto)


def convertir_moneda(mensaje):
    """Detecta EUR/COP y realiza la conversión en ambos sentidos."""
    texto = mensaje.lower().strip()
    texto = texto.replace("→", " a ").replace("->", " a ").replace("⇒", " a ")
    texto = texto.replace("€", " eur ")
    texto = re.sub(r"\beuros?\b", "eur", texto)
    texto = re.sub(r"\bpesos?\s+colombianos?\b", "cop", texto)
    texto = re.sub(r"\bpeso\s+colombiano\b", "cop", texto)
    texto = re.sub(r"\bpesos?\b", "cop", texto)

    numero = r"([0-9][0-9.,]*)"
    patron_eur = re.search(rf"{numero}\s*eur\b.*?\bcop\b", texto)
    patron_cop = re.search(rf"{numero}\s*cop\b.*?\beur\b", texto)

    if not patron_eur and not patron_cop:
        return None

    match = patron_eur or patron_cop
    try:
        cantidad = parsear_cantidad(match.group(1))
        if cantidad <= 0:
            return "La cantidad debe ser mayor que cero."
    except (InvalidOperation, ValueError):
        return "No pude entender la cantidad. Prueba, por ejemplo: 100 euros a pesos colombianos."

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

    # Respuestas conversacionales solicitadas.
    if mensaje == "hola":
        await update.message.reply_text("Hola, ¿cómo estás? 😜")
        return

    if mensaje == "bien":
        await update.message.reply_text("¿En qué te puedo ayudar?")
        return

    if mensaje == "mal":
        await update.message.reply_text("Vaya 😔, espero que mejore tu día.")
        return

    if mensaje in ("buenos días", "buenos dias"):
        await update.message.reply_text("¡Buenos días! ☀️")
        return

    if mensaje == "gracias":
        await update.message.reply_text("¡De nada! 😊")
        return

    conversion = convertir_moneda(mensaje)
    if conversion:
        await update.message.reply_text(conversion)
        return


app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder_mensaje))

print("Bot iniciado")
app.run_polling()
