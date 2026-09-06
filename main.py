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
