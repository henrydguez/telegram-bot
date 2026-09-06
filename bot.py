import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MINI_APP_URL = "https://henrydguez.github.io/telegram-bot/"

if not TOKEN:
    raise RuntimeError("No se encontró BOT_TOKEN en el archivo .env")

if not OPENAI_API_KEY:
    raise RuntimeError("No se encontró OPENAI_API_KEY en el archivo .env")

openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
Eres el asistente de un bot de Telegram.
Responde siempre en español, de forma clara, natural y útil.
Para preguntas sencillas, responde de forma breve.
Si el usuario hace una pregunta más compleja, explica lo necesario sin complicar innecesariamente la respuesta.
No inventes datos. Si no tienes suficiente información para responder con seguridad, dilo claramente.
""".strip()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton(
            "🚀 Abrir Mini App",
            web_app=WebAppInfo(url=MINI_APP_URL),
        )
    ]]
    await update.message.reply_text(
        "¡Hola! 👋 Soy tu asistente de Telegram.\n\nPuedes preguntarme lo que quieras o abrir la Mini App:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def abrir_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton(
            "🚀 Abrir Mini App",
            web_app=WebAppInfo(url=MINI_APP_URL),
        )
    ]]
    await update.message.reply_text(
        "Aquí tienes tu Mini App:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def responder_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    mensaje = update.message.text.strip()

    try:
        response = await openai_client.responses.create(
            model="gpt-5.6",
            instructions=SYSTEM_PROMPT,
            input=mensaje,
            max_output_tokens=500,
        )

        respuesta = response.output_text.strip()

        if not respuesta:
            respuesta = "No he podido generar una respuesta. Inténtalo de nuevo."

        await update.message.reply_text(respuesta)

    except Exception as error:
        print(f"Error al consultar OpenAI: {error}")
        await update.message.reply_text(
            "Ahora mismo no puedo consultar la IA. Inténtalo de nuevo en unos segundos. 😕"
        )


app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("app", abrir_app))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder_mensaje))

print("Bot iniciado con IA")
app.run_polling()
