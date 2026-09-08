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
    raise RuntimeError("No se encontró NVIDIA_API_KEY. Configúrala en .env o en las variables de entorno del servicio.")

ai_client = AsyncOpenAI(
    api_key=NVIDIA_API_KEY,
    base_url=NVIDIA_BASE_URL,
    timeout=60.0,
    max_retries=2,
)

SYSTEM_PROMPT = """
Eres el asistente inteligente de un bot de Telegram conectado directamente a NVIDIA Nemotron.
Responde siempre en español, de forma natural, clara y útil.
Cada mensaje del usuario debe ser procesado por el modelo; nunca uses respuestas predefinidas para preguntas normales.
Para preguntas sencillas, responde de forma breve.
Para preguntas complejas, explica lo necesario de manera comprensible.
No inventes datos. Si no tienes suficiente información o no puedes verificar algo, dilo claramente.
""".strip()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("🚀 Abrir Mini App", web_app=WebAppInfo(url=MINI_APP_URL))
    ]]
    await update.message.reply_text(
        "¡Hola! 👋 Soy tu asistente de IA con NVIDIA Nemotron.\n\nPuedes preguntarme lo que quieras o abrir la Mini App:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def abrir_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("🚀 Abrir Mini App", web_app=WebAppInfo(url=MINI_APP_URL))
    ]]
    await update.message.reply_text("Aquí tienes tu Mini App:", reply_markup=InlineKeyboardMarkup(keyboard))


async def modelo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🤖 Motor activo: NVIDIA Nemotron\n🧠 Modelo: {NVIDIA_MODEL}\n🌐 API: NVIDIA NIM"
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
            raise RuntimeError("NVIDIA devolvió una respuesta vacía")

        await update.message.reply_text(respuesta)

    except Exception:
        logging.exception("Error al consultar NVIDIA Nemotron")
        await update.message.reply_text(
            "⚠️ No he podido consultar NVIDIA Nemotron en este momento. Revisa el registro de la terminal para ver el error exacto."
        )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error("Error de Telegram: %s", context.error, exc_info=context.error)


app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("app", abrir_app))
app.add_handler(CommandHandler("modelo", modelo))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder_mensaje))
app.add_error_handler(error_handler)

logging.info("============================================================")
logging.info("BOT IA INICIADO | NVIDIA NEMOTRON | %s", NVIDIA_MODEL)
logging.info("ENDPOINT: %s/chat/completions", NVIDIA_BASE_URL)
logging.info("============================================================")
app.run_polling(drop_pending_updates=True)
