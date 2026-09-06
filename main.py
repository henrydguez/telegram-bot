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


async def responder_hola(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text and update.message.text.lower().strip() == "hola":
        await update.message.reply_text("Hola, ¿cómo estás? 😜")
        await update.message.reply_text("¿En qué te puedo ayudar?")


app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder_hola))

print("Bot iniciado")
app.run_polling()
