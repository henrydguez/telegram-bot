# Mini App Streaming Backend

FastAPI backend for the Telegram Mini App. It keeps the NVIDIA API key server-side and streams Nemotron responses as Server-Sent Events (SSE).

## Endpoints

- `GET /health` — health check.
- `POST /chat` — authenticated Telegram Web App chat stream.

## Environment

Set `NVIDIA_API_KEY` and `BOT_TOKEN`. Optional values are documented in `.env.example`.

## Run locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

The production Mini App should point `API_URL` in `index.html` at the deployed HTTPS URL of this service.
