import html
import logging
import os
import re
import tempfile
from pathlib import Path
from urllib.parse import quote_plus, urlparse
from urllib.request import Request, urlopen

from dotenv import load_dotenv
from faster_whisper import WhisperModel
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
WEB_SEARCH_ENABLED = os.getenv("WEB_SEARCH_ENABLED", "true").lower() == "true"
WEB_SEARCH_MAX_RESULTS = int(os.getenv("WEB_SEARCH_MAX_RESULTS", "5"))
VOICE_ENABLED = os.getenv("VOICE_ENABLED", "true").lower() == "true"
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
WHISPER_COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "int8")

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

whisper_model = None

SYSTEM_PROMPT = """
Eres el asistente inteligente de un bot de Telegram conectado directamente a NVIDIA Nemotron.
Responde siempre en español, de forma natural, clara y útil.
Cada mensaje del usuario debe ser procesado por el modelo; nunca uses respuestas predefinidas para preguntas normales.
Para preguntas sencillas, responde de forma breve.
Para preguntas complejas, explica lo necesario de manera comprensible.
No inventes datos.
Cuando recibas resultados de búsqueda web, úsalos para responder preguntas actuales y cita las fuentes con [1], [2], etc.
No presentes una fuente como prueba de algo que no aparece en su contenido.
Si las fuentes son contradictorias, indícalo y prioriza fuentes oficiales o de mayor autoridad.
Si no tienes suficiente información o no puedes verificar algo, dilo claramente.
""".strip()

WEB_TRIGGERS = (
    "hoy", "ahora", "actual", "actualizado", "último", "última", "últimos", "últimas",
    "noticias", "reciente", "recientes", "esta semana", "este mes", "2026", "precio",
    "precios", "cotización", "cotiza", "tipo de cambio", "horario", "horarios", "abierto",
    "abierta", "disponible", "disponibilidad", "evento", "eventos", "partido", "resultados",
    "quién es el actual", "quien es el actual", "busca", "buscar", "investiga", "consulta en internet",
    "en internet", "web", "fuentes", "según internet", "qué pasó", "que paso", "últimas noticias",
)


def necesita_busqueda_web(texto: str) -> bool:
    texto_normalizado = " ".join(texto.lower().split())
    return any(trigger in texto_normalizado for trigger in WEB_TRIGGERS)


def limpiar_url(url: str) -> str:
    parsed = urlparse(html.unescape(url))
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}" if parsed.path else f"{parsed.scheme}://{parsed.netloc}"


def buscar_en_web(query: str, max_results: int = WEB_SEARCH_MAX_RESULTS) -> list[dict]:
    url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; TelegramAIBot/1.0; +https://telegram.org/)"
        },
    )

    with urlopen(request, timeout=10) as response:
        page = response.read().decode("utf-8", errors="replace")

    results = []
    pattern = re.compile(
        r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
        re.IGNORECASE | re.DOTALL,
    )
    snippet_pattern = re.compile(
        r'<(?:a|div)[^>]+class="result__snippet"[^>]*>(.*?)</(?:a|div)>',
        re.IGNORECASE | re.DOTALL,
    )

    links = pattern.findall(page)
    snippets = snippet_pattern.findall(page)

    for index, (raw_url, raw_title) in enumerate(links[:max_results]):
        clean_url = limpiar_url(raw_url)
        title = re.sub(r"<[^>]+>", " ", raw_title)
        title = html.unescape(" ".join(title.split()))
        snippet = ""
        if index < len(snippets):
            snippet = re.sub(r"<[^>]+>", " ", snippets[index])
            snippet = html.unescape(" ".join(snippet.split()))

        if clean_url and title:
            results.append({"title": title, "url": clean_url, "snippet": snippet})

    return results


def formatear_resultados_web(resultados: list[dict]) -> str:
    if not resultados:
        return "No se encontraron resultados web relevantes."

    partes = ["RESULTADOS DE BÚSQUEDA WEB:"]
    for i, resultado in enumerate(resultados, start=1):
        partes.append(
            f"[{i}] {resultado['title']}\n"
            f"URL: {resultado['url']}\n"
            f"Resumen: {resultado['snippet']}"
        )
    return "\n\n".join(partes)


def obtener_whisper_model():
    global whisper_model
    if whisper_model is None:
        logging.info(
            "Cargando Whisper | modelo=%s | device=%s | compute_type=%s",
            WHISPER_MODEL,
            WHISPER_DEVICE,
            WHISPER_COMPUTE_TYPE,
        )
        whisper_model = WhisperModel(
            WHISPER_MODEL,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE,
        )
        logging.info("Whisper listo")
    return whisper_model


def transcribir_audio(audio_path: str) -> str:
    model = obtener_whisper_model()
    segments, info = model.transcribe(
        audio_path,
        language="es",
        beam_size=5,
        vad_filter=True,
    )
    texto = " ".join(segment.text.strip() for segment in segments if segment.text.strip()).strip()
    logging.info("Voz transcrita | idioma=%s | texto=%s", info.language, texto)
    return texto


async def llamar_modelo(mensaje: str, contexto_web: str | None = None) -> str:
    user_content = mensaje
    if contexto_web:
        user_content = (
            "Usa los siguientes resultados de búsqueda web como contexto para responder. "
            "Cita las fuentes con [1], [2], etc. y no inventes información que no esté respaldada.\n\n"
            f"{contexto_web}\n\nPREGUNTA DEL USUARIO:\n{mensaje}"
        )

    response = await ai_client.chat.completions.create(
        model=NVIDIA_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        max_tokens=1200,
        temperature=0.5,
        stream=False,
    )

    respuesta = (response.choices[0].message.content or "").strip()
    if not respuesta:
        raise RuntimeError("NVIDIA devolvió una respuesta vacía")
    return respuesta


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("🚀 Abrir Mini App", web_app=WebAppInfo(url=MINI_APP_URL))
    ]]
    await update.message.reply_text(
        "¡Hola! 👋 Soy tu asistente de IA con NVIDIA Nemotron.\n\n"
        "Puedo responder preguntas normales, consultar información actualizada en la web y entender mensajes de voz.\n\n"
        "También puedes usar /buscar para forzar una búsqueda web.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def abrir_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("🚀 Abrir Mini App", web_app=WebAppInfo(url=MINI_APP_URL))
    ]]
    await update.message.reply_text("Aquí tienes tu Mini App:", reply_markup=InlineKeyboardMarkup(keyboard))


async def modelo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🤖 Motor activo: NVIDIA Nemotron\n"
        f"🧠 Modelo: {NVIDIA_MODEL}\n"
        f"🌐 API: NVIDIA NIM\n"
        f"🔎 Búsqueda web: {'activa' if WEB_SEARCH_ENABLED else 'desactivada'}\n"
        f"🎙️ Voz: {'activa' if VOICE_ENABLED else 'desactivada'}\n"
        f"📝 Whisper: {WHISPER_MODEL}"
    )


async def buscar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    query = " ".join(context.args).strip()
    if not query:
        await update.message.reply_text("Uso: /buscar qué ha pasado hoy con... ")
        return

    if not WEB_SEARCH_ENABLED:
        await update.message.reply_text("🔎 La búsqueda web está desactivada en la configuración.")
        return

    try:
        await update.message.reply_text("🔎 Buscando información actualizada...")
        resultados = buscar_en_web(query)
        contexto = formatear_resultados_web(resultados)
        respuesta = await llamar_modelo(query, contexto)
        await update.message.reply_text(respuesta)

        if resultados:
            fuentes = "\n\n🔗 Fuentes:\n" + "\n".join(
                f"[{i}] {r['url']}" for i, r in enumerate(resultados, start=1)
            )
            if len(fuentes) <= 3500:
                await update.message.reply_text(fuentes)

    except Exception:
        logging.exception("Error durante la búsqueda web")
        await update.message.reply_text(
            "⚠️ No he podido realizar la búsqueda web en este momento. Inténtalo de nuevo."
        )


async def procesar_voz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.voice:
        return

    if not VOICE_ENABLED:
        await update.message.reply_text("🎙️ La función de voz está desactivada.")
        return

    try:
        await update.message.reply_text("🎙️ Entendido. Estoy transcribiendo tu mensaje...")

        telegram_file = await context.bot.get_file(update.message.voice.file_id)
        with tempfile.TemporaryDirectory(prefix="telegram_voice_") as temp_dir:
            audio_path = Path(temp_dir) / "mensaje.ogg"
            await telegram_file.download_to_drive(custom_path=str(audio_path))
            texto = transcribir_audio(str(audio_path))

        if not texto:
            await update.message.reply_text("⚠️ No he podido entender el audio. Inténtalo de nuevo, por favor.")
            return

        contexto_web = None
        resultados = []
        if WEB_SEARCH_ENABLED and necesita_busqueda_web(texto):
            logging.info("Búsqueda web automática desde voz: %s", texto)
            try:
                resultados = buscar_en_web(texto)
                contexto_web = formatear_resultados_web(resultados)
            except Exception:
                logging.exception("La búsqueda web desde voz falló; continúo solo con IA")

        respuesta = await llamar_modelo(texto, contexto_web)
        await update.message.reply_text(respuesta)

        if contexto_web and resultados:
            fuentes = "🔗 Fuentes consultadas:\n" + "\n".join(
                f"[{i}] {r['url']}" for i, r in enumerate(resultados, start=1)
            )
            if len(fuentes) <= 3500:
                await update.message.reply_text(fuentes)

    except Exception:
        logging.exception("Error procesando mensaje de voz")
        await update.message.reply_text(
            "⚠️ No he podido procesar el mensaje de voz. Revisa el registro de la terminal para ver el error exacto."
        )


async def responder_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    mensaje = update.message.text.strip()
    if not mensaje:
        return

    try:
        contexto_web = None
        resultados = []
        if WEB_SEARCH_ENABLED and necesita_busqueda_web(mensaje):
            logging.info("Búsqueda web automática: %s", mensaje)
            try:
                resultados = buscar_en_web(mensaje)
                contexto_web = formatear_resultados_web(resultados)
            except Exception:
                logging.exception("La búsqueda web automática falló; continúo solo con IA")

        respuesta = await llamar_modelo(mensaje, contexto_web)
        await update.message.reply_text(respuesta)

        if contexto_web and resultados:
            fuentes = "🔗 Fuentes consultadas:\n" + "\n".join(
                f"[{i}] {r['url']}" for i, r in enumerate(resultados, start=1)
            )
            if len(fuentes) <= 3500:
                await update.message.reply_text(fuentes)

    except Exception:
        logging.exception("Error al consultar NVIDIA Nemotron")
        await update.message.reply_text(
            "⚠️ No he podido procesar tu mensaje en este momento. Revisa el registro de la terminal para ver el error exacto."
        )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error("Error de Telegram: %s", context.error, exc_info=context.error)


app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("app", abrir_app))
app.add_handler(CommandHandler("modelo", modelo))
app.add_handler(CommandHandler("buscar", buscar))
app.add_handler(MessageHandler(filters.VOICE, procesar_voz))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder_mensaje))
app.add_error_handler(error_handler)

logging.info("============================================================")
logging.info("BOT IA INICIADO | NVIDIA NEMOTRON | %s", NVIDIA_MODEL)
logging.info("BÚSQUEDA WEB: %s", "ACTIVA" if WEB_SEARCH_ENABLED else "DESACTIVADA")
logging.info("VOZ: %s | WHISPER: %s", "ACTIVA" if VOICE_ENABLED else "DESACTIVADA", WHISPER_MODEL)
logging.info("ENDPOINT: %s/chat/completions", NVIDIA_BASE_URL)
logging.info("============================================================")
app.run_polling(drop_pending_updates=True)
