import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("No se encontró BOT_TOKEN en el archivo .env")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! 👋 Soy tu bot de Telegram.")


async def responder_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    mensaje = update.message.text.strip().lower()

    if mensaje == "hola":
        await update.message.reply_text("Hola, ¿cómo estás? 😜")
    elif mensaje == "bien":
        await update.message.reply_text("¿En qué te puedo ayudar?")
    elif mensaje == "mal":
        await update.message.reply_text("Vaya 😔, espero que mejore tu día.")
    elif mensaje in ("buenos días", "buenos dias"):
        await update.message.reply_text("¡Buenos días! ☀️")
    elif mensaje == "gracias":
        await update.message.reply_text("¡De nada! 😊")


app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder_mensaje))

print("Bot iniciado")
app.run_polling()
