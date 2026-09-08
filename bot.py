import logging
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

TOKEN = os.getenv("BOT_TOKEN")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
MINI_APP_URL = "https://henrydguez.github.io/telegram-bot/"
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "nvidia/nemotron-3-super-120b-a12b")

if not TOKEN:
    raise RuntimeError("No se encontró BOT_TOKEN. Configúralo en el entorno del bot.")

if not NVIDIA_API_KEY:
    raise RuntimeError("No se encontró NVIDIA_API_KEY. Configúrala en el archivo .env o en las variables de entorno del servicio.")

ai_client = AsyncOpenAI(
    api_key=NVIDIA_API_KEY,
    base_url=NVIDIA_BASE_URL,
)

SYSTEM_PROMPT = """
Eres el asistente inteligente de un bot de Telegram.
Responde siempre en español, de forma natural, clara y útil.
No te limites a respuestas predefinidas: analiza cada mensaje y genera una respuesta nueva usando el modelo de IA.
Para preguntas sencillas, responde de forma breve.
Para preguntas complejas, razona y explica lo necesario de manera comprensible.
No inventes datos. Si no tienes suficiente información o no puedes verificar algo, dilo claramente.
""".strip()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton(
            "🚀 Abrir Mini App",
            web_app=WebAppInfo(url=MINI_APP_URL),
        )
    ]]
    await update.message.reply_text(
        "¡Hola! 👋 Soy tu asistente de IA con NVIDIA Nemotron.\n\nPuedes preguntarme lo que quieras o abrir la Mini App:",
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
    if not mensaje:
        return

    try:
        response = await ai_client.chat.completions.create(
            model=NVIDIA_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": mensaje},
            ],
            max_tokens=1000,
            temperature=0.7,
            stream=False,
        )

        respuesta = (response.choices[0].message.content or "").strip()
        if not respuesta:
            respuesta = "No he podido generar una respuesta. Inténtalo de nuevo."

        await update.message.reply_text(respuesta)

    except Exception:
        logging.exception("Error al consultar NVIDIA Nemotron")
        await update.message.reply_text(
            "Ahora mismo no puedo consultar NVIDIA Nemotron. Inténtalo de nuevo en unos segundos. 😕"
        )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error("Error de Telegram: %s", context.error, exc_info=context.error)


app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("app", abrir_app))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder_mensaje))
app.add_error_handler(error_handler)

logging.info("Bot iniciado con NVIDIA Nemotron: %s", NVIDIA_MODEL)
app.run_polling(drop_pending_updates=True)
