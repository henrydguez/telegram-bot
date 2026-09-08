import hashlib
import hmac
import json
import os
import time
from urllib.parse import parse_qsl

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from telegram import Update

# Importamos el bot existente para reutilizar comandos, búsqueda web, voz y streaming.
import bot as telegram_bot

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "nvidia/nemotron-3-super-120b-a12b")
TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_INITDATA_MAX_AGE = int(os.getenv("TELEGRAM_INITDATA_MAX_AGE", "86400"))
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "").rstrip("/")
WEBHOOK_PATH = "/telegram/webhook"

if not NVIDIA_API_KEY:
    raise RuntimeError("NVIDIA_API_KEY is required")
if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is required")

client = AsyncOpenAI(api_key=NVIDIA_API_KEY, base_url=NVIDIA_BASE_URL, timeout=120.0, max_retries=2)

SYSTEM_PROMPT = """Eres el asistente inteligente de una Mini App de Telegram conectado a NVIDIA Nemotron.
Responde siempre en español, de forma natural, clara y útil.
Mantén el contexto de la conversación.
No inventes datos. Si no sabes algo, dilo claramente.
Para preguntas sencillas, responde brevemente; para preguntas complejas, explica lo necesario."""

app = FastAPI(title="Telegram Nemotron 24/7 API", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://henrydguez.github.io"],
    allow_credentials=False,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type"],
)


class Message(BaseModel):
    role: str
    content: str = Field(min_length=1, max_length=12000)


class ChatRequest(BaseModel):
    initData: str = Field(min_length=1, max_length=10000)
    messages: list[Message] = Field(min_length=1, max_length=50)


def validate_telegram_init_data(init_data: str) -> dict:
    # parse_qsl hace la decodificación de URL una sola vez.
    pairs = parse_qsl(init_data, keep_blank_values=True)
    data = dict(pairs)
    received_hash = data.pop("hash", None)
    if not received_hash:
        raise HTTPException(status_code=401, detail="Missing Telegram initData hash")

    auth_date = data.get("auth_date")
    try:
        age = time.time() - int(auth_date) if auth_date else float("inf")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Telegram auth_date")

    if age < -300 or age > TELEGRAM_INITDATA_MAX_AGE:
        raise HTTPException(status_code=401, detail="Expired Telegram initData")

    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(data.items()))
    secret_key = hmac.new(b"WebAppData", TELEGRAM_BOT_TOKEN.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise HTTPException(status_code=401, detail="Invalid Telegram initData")

    return data


def clean_messages(messages: list[Message]) -> list[dict]:
    cleaned = []
    for message in messages:
        if message.role not in {"user", "assistant"}:
            continue
        content = message.content.strip()
        if content:
            cleaned.append({"role": message.role, "content": content})
    if not cleaned or cleaned[-1]["role"] != "user":
        raise HTTPException(status_code=400, detail="The last message must be from the user")
    return cleaned[-30:]


async def stream_nemotron(messages: list[dict]):
    try:
        response = await client.chat.completions.create(
            model=NVIDIA_MODEL,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, *messages],
            max_tokens=1200,
            temperature=0.5,
            stream=True,
        )

        async for chunk in response:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta.content
            if delta:
                yield f"data: {json.dumps({'type': 'delta', 'content': delta}, ensure_ascii=False)}\n\n"

        yield "data: {\"type\":\"done\"}\n\n"
    except Exception as exc:
        yield f"data: {json.dumps({'type': 'error', 'message': str(exc)}, ensure_ascii=False)}\n\n"


@app.on_event("startup")
async def startup():
    await telegram_bot.app.initialize()
    await telegram_bot.app.start()

    if RENDER_EXTERNAL_URL:
        webhook_url = f"{RENDER_EXTERNAL_URL}{WEBHOOK_PATH}"
        await telegram_bot.app.bot.set_webhook(
            url=webhook_url,
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES,
        )
        telegram_bot.logging.info("Telegram webhook configurado: %s", webhook_url)
    else:
        telegram_bot.logging.info("RENDER_EXTERNAL_URL no definido; webhook no configurado")


@app.on_event("shutdown")
async def shutdown():
    try:
        if RENDER_EXTERNAL_URL:
            await telegram_bot.app.bot.delete_webhook(drop_pending_updates=False)
        await telegram_bot.app.stop()
        await telegram_bot.app.shutdown()
    except Exception:
        telegram_bot.logging.exception("Error cerrando el bot")


@app.get("/health")
async def health():
    webhook = f"{RENDER_EXTERNAL_URL}{WEBHOOK_PATH}" if RENDER_EXTERNAL_URL else None
    return {
        "status": "ok",
        "model": NVIDIA_MODEL,
        "streaming": True,
        "telegram_webhook": webhook,
    }


@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    try:
        payload = await request.json()
        update = Update.de_json(payload, telegram_bot.app.bot)
        await telegram_bot.app.process_update(update)
        return {"ok": True}
    except Exception:
        telegram_bot.logging.exception("Error procesando webhook de Telegram")
        raise HTTPException(status_code=500, detail="Telegram update processing failed")


@app.post("/chat")
async def chat(request: ChatRequest):
    validate_telegram_init_data(request.initData)
    messages = clean_messages(request.messages)
    return StreamingResponse(
        stream_nemotron(messages),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
