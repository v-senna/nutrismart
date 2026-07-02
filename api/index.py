import sys
import os
import traceback

# Adiciona o diretório 'backend' ao path para que os imports funcionem na Vercel
backend_path = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.append(backend_path)

try:
    from main import app as fastapi_app
    _import_error = None
except Exception as e:
    _import_error = f"{type(e).__name__}: {str(e)}\n\n{traceback.format_exc()}"
    fastapi_app = None

# ---------------------------------------------------------------------------
# Vercel routes /api/register → este handler, mas o scope["path"] chega como
# "/api/register". O FastAPI tem rotas definidas como "/register", então
# precisamos remover o prefixo "/api" antes de o FastAPI processar.
# ---------------------------------------------------------------------------

async def app(scope, receive, send):
    if scope["type"] in ("http", "websocket"):
        path = scope.get("path", "")
        if path.startswith("/api"):
            scope = dict(scope)
            scope["path"] = path[4:] or "/"
            scope["raw_path"] = scope["path"].encode()

    if _import_error:
        # Retorna o erro de import como JSON para diagnóstico
        if scope["type"] == "http":
            await receive()
            body = f'{{"error": "Import failed", "detail": {repr(_import_error)}}}'.encode()
            await send({"type": "http.response.start", "status": 500, "headers": [[b"content-type", b"application/json"]]})
            await send({"type": "http.response.body", "body": body})
        return

    await fastapi_app(scope, receive, send)

# Mangum adapta o app ASGI para o formato de função serverless da AWS Lambda
from mangum import Mangum
handler = Mangum(app, lifespan="off")
