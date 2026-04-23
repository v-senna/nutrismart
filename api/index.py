import sys
import os

# Adiciona o diretório 'backend' ao path para que os imports funcionem na Vercel
backend_path = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.append(backend_path)

# Importa o app do FastAPI
from main import app

# Exporta como handler para a Vercel
# A Vercel espera que o objeto do app seja acessível
handler = app
