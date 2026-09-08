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
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MINI_APP_URL = "https://henrydguez.github.io/telegram-bot/"
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "nvidia/nemotron-3-super-120b-a12b")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")

if not TOKEN:
    raise RuntimeError("No se encontró BOT_TOKEN. Configúralo como variable de entorno o secreto.")

if NVIDIA_API_KEY:
    ai_client = AsyncOpenAI(api_key=NVIDIA_API_KEY, base_url=NVIDIA_BASE_URL)
    AI_PROVIDER = "NVIDIA Nemotron"
    AI_MODEL = NVIDIA_MODEL
elif OPENAI_API_KEY:
    ai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    AI_PROVIDER = "OpenAI"
    AI_MODEL = OPENAI_MODEL
else:
    raise RuntimeError("No se encontró NVIDIA_API_KEY ni OPENAI_API_KEY.")

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
    if not mensaje:
        return

    try:
        response = await ai_client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": mensaje},
            ],
            max_tokens=500,
            temperature=0.7,
        )

        respuesta = (response.choices[0].message.content or "").strip()
        if not respuesta:
            respuesta = "No he podido generar una respuesta. Inténtalo de nuevo."

        await update.message.reply_text(respuesta)

    except Exception:
        logging.exception("Error al consultar %s", AI_PROVIDER)
        await update.message.reply_text(
            "Ahora mismo no puedo consultar la IA. Inténtalo de nuevo en unos segundos. 😕"
        )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error("Error de Telegram: %s", context.error, exc_info=context.error)


app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("app", abrir_app))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder_mensaje))
app.add_error_handler(error_handler)

logging.info("Bot iniciado usando %s (%s)", AI_PROVIDER, AI_MODEL)
app.run_polling(drop_pending_updates=True)
