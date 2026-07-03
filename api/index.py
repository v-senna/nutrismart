import sys
import os

# Adiciona o diretório 'backend' ao path para que os imports funcionem na Vercel
backend_path = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.append(backend_path)

from main import app as fastapi_app

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
    await fastapi_app(scope, receive, send)

# Mangum adapta o app ASGI para o formato de função serverless da AWS Lambda
from mangum import Mangum
handler = Mangum(app, lifespan="off")
