import re
import io
import os
import json
import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente do .env
load_dotenv()

# Configurar Gemini (O usuário deve fornecer a chave no ambiente)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Validação: tratar chaves placeholder como None
if GEMINI_API_KEY:
    _key_lower = GEMINI_API_KEY.lower()
    if "aqui" in _key_lower or "cole" in _key_lower or len(GEMINI_API_KEY) < 20:
        print(f"⚠️ GEMINI_API_KEY parece ser um placeholder ('{GEMINI_API_KEY[:15]}...'). IA desabilitada.")
        GEMINI_API_KEY = None


def _call_gemini(prompt: str) -> str:
    """Chama a API REST do Gemini diretamente (sem SDK pesado)."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]

# --- Dados de fallback para supermercados por região ---
SUPERMARKETS_BY_REGION = {
    "são paulo": [
        {"name": "Extra", "url": "https://www.extra.com.br"},
        {"name": "Pão de Açúcar", "url": "https://www.paodeacucar.com"},
        {"name": "Carrefour", "url": "https://www.carrefour.com.br"},
        {"name": "Assaí Atacadista", "url": "https://www.assai.com.br"},
        {"name": "Atacadão", "url": "https://www.atacadao.com.br"},
    ],
    "rio de janeiro": [
        {"name": "Supermercados Guanabara", "url": "https://www.supermercadosguanabara.com.br"},
        {"name": "Mundial", "url": "https://www.supermercadosmundial.com.br"},
        {"name": "Extra", "url": "https://www.extra.com.br"},
        {"name": "Prezunic", "url": "https://www.prezunic.com.br"},
        {"name": "Assaí Atacadista", "url": "https://www.assai.com.br"},
    ],
    "araras": [
        {"name": "Copacabana Supermercados", "url": "https://www.copacabanasupermercados.com.br"},
        {"name": "Savegnago", "url": "https://www.savegnago.com.br"},
        {"name": "Pão de Açúcar", "url": "https://www.paodeacucar.com"},
        {"name": "Atacadão", "url": "https://www.atacadao.com.br"},
        {"name": "Assaí Atacadista", "url": "https://www.assai.com.br"},
    ],
    "campinas": [
        {"name": "Dalben Supermercados", "url": "https://www.dalben.com.br"},
        {"name": "Tenda Atacado", "url": "https://www.tendaatacado.com.br"},
        {"name": "Carrefour", "url": "https://www.carrefour.com.br"},
        {"name": "Atacadão", "url": "https://www.atacadao.com.br"},
        {"name": "Savegnago", "url": "https://www.savegnago.com.br"},
    ],
    "belo horizonte": [
        {"name": "BH Supermercados", "url": "https://www.bhsupermercados.com.br"},
        {"name": "Super Nosso", "url": "https://www.supernosso.com.br"},
        {"name": "Verdemar", "url": "https://www.verdemar.com.br"},
        {"name": "EPA Supermercados", "url": "https://www.epasupermercados.com.br"},
        {"name": "Carrefour", "url": "https://www.carrefour.com.br"},
    ],
    "curitiba": [
        {"name": "Condor Super Center", "url": "https://www.condor.com.br"},
        {"name": "Muffato", "url": "https://www.supermuffato.com.br"},
        {"name": "Carrefour", "url": "https://www.carrefour.com.br"},
        {"name": "Atacadão", "url": "https://www.atacadao.com.br"},
        {"name": "Festval", "url": "https://www.festval.com.br"},
    ],
}

# Fallback genérico
DEFAULT_SUPERMARKETS = [
    {"name": "Carrefour", "url": "https://www.carrefour.com.br"},
    {"name": "Extra", "url": "https://www.extra.com.br"},
    {"name": "Atacadão", "url": "https://www.atacadao.com.br"},
    {"name": "Assaí Atacadista", "url": "https://www.assai.com.br"},
    {"name": "Pão de Açúcar", "url": "https://www.paodeacucar.com"},
]

# --- Preços médios de alimentos brasileiros (fallback) ---
AVERAGE_PRICES = {
    # Grãos e cereais
    "arroz": 27.0, "arroz 5kg": 27.0, "arroz integral": 12.0, "arroz 1kg": 6.50,
    "feijão": 8.0, "feijão 1kg": 8.0, "feijão carioca": 8.0, "feijão preto": 9.0,
    "macarrão": 4.50, "macarrão 500g": 4.50, "macarrão integral": 6.00,
    "aveia": 7.50, "aveia 500g": 7.50, "granola": 12.0,
    # Proteínas
    "frango": 19.0, "peito de frango": 19.0, "frango kg": 19.0, "filé de frango": 22.0,
    "carne bovina": 42.0, "patinho": 42.0, "alcatra": 50.0, "coxão mole": 45.0,
    "carne moída": 32.0, "acém": 35.0,
    "ovo": 22.0, "ovos": 22.0, "ovo 30 unidades": 22.0, "ovo cartela": 22.0,
    "ovo 12 unidades": 10.0, "ovo dúzia": 10.0,
    "peixe": 35.0, "tilápia": 30.0, "salmão": 70.0,
    "linguiça": 18.0, "salsicha": 8.0,
    # Laticínios
    "leite": 6.50, "leite 1l": 6.50, "leite integral": 6.50, "leite desnatado": 6.80,
    "queijo mussarela": 42.0, "queijo": 42.0, "queijo prato": 48.0,
    "iogurte": 7.0, "iogurte natural": 5.50, "iogurte grego": 8.0,
    "manteiga": 12.0, "margarina": 6.50, "requeijão": 9.0,
    "cream cheese": 10.0, "whey protein": 120.0,
    # Frutas
    "banana": 5.0, "banana kg": 5.0, "maçã": 12.0, "laranja": 5.50,
    "morango": 10.0, "uva": 14.0, "manga": 6.0, "mamão": 7.0,
    "abacaxi": 6.0, "melancia": 12.0, "limão": 5.0,
    # Verduras e legumes
    "tomate": 8.0, "cebola": 5.0, "alface": 3.50, "batata": 6.0,
    "cenoura": 5.0, "brócolis": 7.0, "abobrinha": 5.50,
    "batata doce": 7.0, "mandioca": 6.0, "espinafre": 5.0,
    # Óleos e temperos
    "azeite": 28.0, "azeite 500ml": 28.0, "óleo de soja": 8.50,
    "sal": 3.0, "açúcar": 5.50, "açúcar 1kg": 5.50, "café": 18.0,
    # Pães e padaria
    "pão de forma": 8.50, "pão francês": 16.0, "pão integral": 10.0,
    "torrada": 6.0, "bolo": 12.0,
    # Outros
    "pasta de amendoim": 18.0, "castanha": 45.0, "mel": 22.0,
    "atum": 8.0, "sardinha": 6.0, "molho de tomate": 4.0,
    "maionese": 7.0, "ketchup": 8.0, "mostarda": 6.0,
}

def _find_best_price(item_name: str) -> float:
    """Encontra o melhor preço correspondente no dicionário de preços médios."""
    item_lower = item_name.lower().strip()

    # Busca exata
    if item_lower in AVERAGE_PRICES:
        return AVERAGE_PRICES[item_lower]

    # Busca parcial: verificar se alguma chave está contida no item
    for key, price in AVERAGE_PRICES.items():
        if key in item_lower or item_lower in key:
            return price

    # Busca por palavras-chave
    words = item_lower.split()
    for word in words:
        if len(word) >= 4:  # Ignorar palavras muito curtas
            for key, price in AVERAGE_PRICES.items():
                if word in key:
                    return price

    # Preço genérico estimado
    return 12.0


def extract_text_from_pdf(file_content):
    try:
        from pypdf import PdfReader  # lazy import — evita bundle pesado
        reader = PdfReader(io.BytesIO(file_content))
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""

def search_supermarkets_ai(region: str):
    if not GEMINI_API_KEY:
        # Fallback inteligente: buscar por região conhecida
        region_lower = region.lower().strip()
        for key, markets in SUPERMARKETS_BY_REGION.items():
            if key in region_lower or region_lower in key:
                return markets
        return DEFAULT_SUPERMARKETS
        
    try:
        prompt = f"""
        O usuário quer saber os principais supermercados online ou físicos na região de "{region}" no Brasil.
        Por favor, forneça uma lista com até 5 supermercados reais que atendem essa região, incluindo o nome e a provável URL do site deles.
        Responda APENAS com um JSON no formato:
        [
          {{"name": "Nome do Supermercado", "url": "https://url-do-mercado.com.br"}}
        ]
        """
        text = _call_gemini(prompt).strip()
        if text.startswith("```json"):
            text = text[7:-3]
        elif text.startswith("```"):
            text = text[3:-3]
        return json.loads(text.strip())
    except Exception as e:
        print(f"Erro ao buscar supermercados: {e}")
        # Em caso de erro, retornar fallback por região
        region_lower = region.lower().strip()
        for key, markets in SUPERMARKETS_BY_REGION.items():
            if key in region_lower or region_lower in key:
                return markets
        return DEFAULT_SUPERMARKETS

def quote_shopping_list_ai(items: list, supermarket: str, region: str):
    if not GEMINI_API_KEY:
        # Fallback com preços realistas brasileiros
        return [{"item": item, "price": _find_best_price(item)} for item in items]
        
    try:
        items_str = "\n".join([f"- {i}" for i in items])
        prompt = f"""
        Atue como um Agente de Cotação de Supermercado.
        Preciso de uma estimativa de preço atualizada (em Reais R$) para os seguintes itens, 
        com base no supermercado "{supermarket}" na região de "{region}".
        Como você é uma IA, se não tiver acesso em tempo real ao site do supermercado, 
        faça uma ESTIMATIVA REALISTA E ATUALIZADA baseada no custo de vida da região e no perfil desse supermercado.
        
        Itens:
        {items_str}
        
        Responda APENAS com um JSON no formato:
        [
          {{"item": "Nome do item", "price": 12.50}}
        ]
        """
        text = _call_gemini(prompt).strip()
        if text.startswith("```json"):
            text = text[7:-3]
        elif text.startswith("```"):
            text = text[3:-3]
        return json.loads(text.strip())
    except Exception as e:
        print(f"Erro ao cotar supermercados: {e}")
        # Em caso de erro, retornar preços estimados
        return [{"item": item, "price": _find_best_price(item)} for item in items]

def extract_text_from_excel(file_content):
    try:
        import pandas as pd  # lazy import — evita bundle pesado
        df = pd.read_excel(io.BytesIO(file_content))
        return df.to_string()
    except Exception as e:
        print(f"Excel extraction error: {e}")
        return ""

def parse_diet_info(text, user_profile=None):
    """
    Tenta extrair informações usando IA (Gemini) com fallback para Regex.
    """
    if GEMINI_API_KEY:
        try:
            print("Tentando extrair informações com Gemini...")
            return parse_diet_info_ai(text, user_profile)
        except Exception as e:
            print(f"Erro na IA (Gemini): {e}. Usando fallback para Regex.")
            return parse_diet_info_regex(text)
    else:
        print("GEMINI_API_KEY não configurada. Usando Regex.")
        return parse_diet_info_regex(text)

def parse_diet_info_ai(text, user_profile=None):
    
    profile_context = ""
    if user_profile:
        profile_context = f"\nO usuário tem o seguinte perfil conhecido: Peso: {user_profile.get('weight', 'Não informado')}kg, Idade: {user_profile.get('age', 'Não informada')}, Objetivo: {user_profile.get('goals', 'Não informado')}. USE ESTAS INFORMAÇÕES COMO BASE PARA OS CÁLCULOS SE NECESSÁRIO.\n"
    
    prompt = f"""
    Analise o texto abaixo, que é uma dieta ou plano nutricional, e extraia as informações de forma estruturada em JSON.{profile_context}
    
    DIRETRIZES CRÍTICAS:
    1. REFEIÇÕES vs DICAS: Diferencie rigorosamente o que são REFEIÇÕES de DICAS/CONSELHOS genéricos.
    2. CONTEÚDO DA REFEIÇÃO E QUANTIDADES (MUITO IMPORTANTE): No campo 'suggestion', liste todos os alimentos com suas respectivas **QUANTIDADES EXATAS**. Exemplo: "150g de Frango Grelhado + 100g de Arroz Integral + 1 Colher de sopa de Azeite". NUNCA retorne um alimento sem quantidade. Se o texto original não tiver quantidade, ESTIME com base no perfil do usuário e inclua.
    3. DICAS E RECOMENDAÇÕES: Extraia separadamente TODAS as dicas, conselhos, orientações e observações gerais (ex: "beba água", "evite doces") no campo 'recommendations'. Elas serão unidas às dicas do nosso próprio sistema.
    4. PERFIL: Identifique idade, peso (kg), altura (cm), sexo (M/F) e objetivo (Emagrecimento, Ganho de Massa Muscular ou Manutenção).
    5. HORÁRIOS: Tente encontrar o horário (HH:MM) para cada refeição. Se não tiver, deduza um horário apropriado.
    6. MACROS: Se houver um resumo de calorias totais, proteína, carboidratos e gorduras, extraia-os. Se não houver, tente somar/estimar as calorias.

    Responda APENAS com o JSON no formato:
    {{
      "profile": {{
        "age": int or null,
        "weight": float or null,
        "height": float or null,
        "gender": "M" or "F" or null,
        "goals": "Emagrecimento" or "Ganho de Massa Muscular" or "Manutenção" or null
      }},
      "meals": [
        {{
          "label": "Nome da Refeição (ex: Almoço)",
          "suggestion": "Lista de alimentos e quantidades EXATAS (ex: 150g de Frango + 100g de Arroz)",
          "time": "HH:MM",
          "calories": int or null
        }}
      ],
      "recommendations": [string],
      "total_calories": float or null,
      "total_protein": float or null,
      "total_carbs": float or null,
      "total_fats": float or null,
      "restrictions": [string],
      "allergies": "texto de alergias ou vazio"
    }}

    TEXTO PARA ANÁLISE:
    {text}
    """
    
    response_text = _call_gemini(prompt).strip()
    
    # Limpar possíveis blocos de código markdown
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0].strip()
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0].strip()
        
    data = json.loads(response_text)
    
    # Garantir estrutura mínima e tipos corretos
    if "profile" not in data: data["profile"] = {}
    if "meals" not in data: data["meals"] = []
    if "recommendations" not in data: data["recommendations"] = []
    
    # Normalizar objetivos para os nomes usados no sistema
    if data["profile"].get("goals"):
        g = data["profile"]["goals"].lower()
        if "emagrec" in g or "perda" in g or "perder" in g: data["profile"]["goals"] = "Emagrecimento"
        elif "ganho" in g or "hipertrofia" in g or "massa" in g: data["profile"]["goals"] = "Ganho de Massa Muscular"
        else: data["profile"]["goals"] = "Manutenção"

    return data

def parse_diet_info_regex(text):
    """
    Tenta extrair informações do perfil e das refeições do texto.
    """
    info = {
        "profile": {
            "age": None,
            "weight": None,
            "height": None,
            "gender": None,
            "goals": None,
            "activity_level": None
        },
        "meals": [],
        "total_calories": None,
        "total_protein": None,
        "total_carbs": None,
        "total_fats": None,
        "restrictions": [],
        "allergies": ""
    }

    # Heurísticas para Perfil
    age_match = re.search(r'(?:idade|anos|age)[\s:]+(\d+)', text, re.IGNORECASE)
    if age_match: info["profile"]["age"] = int(age_match.group(1))

    weight_match = re.search(r'(?:peso|weight|kg)[\s:]+(\d+[,.]?\d*)', text, re.IGNORECASE)
    if weight_match: info["profile"]["weight"] = float(weight_match.group(1).replace(',', '.'))

    height_match = re.search(r'(?:altura|height|cm)[\s:]+(\d+[,.]?\d*)', text, re.IGNORECASE)
    if height_match: 
        val = float(height_match.group(1).replace(',', '.'))
        if val < 3: val *= 100 # Converter metros para cm
        info["profile"]["height"] = val

    if re.search(r'\b(masculino|homem|male|M)\b', text, re.IGNORECASE): info["profile"]["gender"] = "M"
    elif re.search(r'\b(feminino|mulher|female|F)\b', text, re.IGNORECASE): info["profile"]["gender"] = "F"

    if re.search(r'\b(emagrecer|perder peso|weight loss|deficit)\b', text, re.IGNORECASE): info["profile"]["goals"] = "Emagrecimento"
    elif re.search(r'\b(ganhar massa|hipertrofia|muscle gain|bulk)\b', text, re.IGNORECASE): info["profile"]["goals"] = "Ganho de Massa Muscular"

    # Heurísticas para Restrições e Alergias
    restrictions = []
    if re.search(r'\b(lactose|leite)\b', text, re.IGNORECASE): restrictions.append("Lactose")
    if re.search(r'\b(glúten|trigo)\b', text, re.IGNORECASE): restrictions.append("Glúten")
    if re.search(r'\b(açúcar|doce)\b', text, re.IGNORECASE): restrictions.append("Açúcar")
    info["restrictions"] = restrictions

    allergies_match = re.search(r'(?:alergias|alergia)[\s:]+(.*?)(?=\.|\n|$)', text, re.IGNORECASE)
    info["allergies"] = allergies_match.group(1).strip() if allergies_match else ""

    # Extração de calorias totais e macros (se houver um resumo)
    total_kcal_match = re.search(r'(?:total|valor energético|calorias totais|kcal)[\s:]*(\d+[,.]?\d*)[\s]*(?:kcal|calorias)?', text, re.IGNORECASE)
    if total_kcal_match:
        info["total_calories"] = float(total_kcal_match.group(1).replace(',', '.'))
        
    prot_match = re.search(r'(?:prote[íi]na(?:s)?)[\s:]*(\d+[,.]?\d*)[\s]*(?:g|gramas)', text, re.IGNORECASE)
    if prot_match: info["total_protein"] = float(prot_match.group(1).replace(',', '.'))

    carbs_match = re.search(r'(?:carboidrato(?:s)?|carbs|cho)[\s:]*(\d+[,.]?\d*)[\s]*(?:g|gramas)', text, re.IGNORECASE)
    if carbs_match: info["total_carbs"] = float(carbs_match.group(1).replace(',', '.'))

    fat_match = re.search(r'(?:gordura(?:s)?|lip[íi]dios|fats|lip)[\s:]*(\d+[,.]?\d*)[\s]*(?:g|gramas)', text, re.IGNORECASE)
    if fat_match: info["total_fats"] = float(fat_match.group(1).replace(',', '.'))

    # Heurística Dinâmica para Refeições
    # Em vez de padrões fixos, vamos buscar por marcadores e segmentar o texto
    meal_markers = [
        r'(?:Café da Manhã|Desjejum|Breakfast|Refeição\s*0?1|M1|R1)',
        r'(?:Lanche da Manhã|Colação|Refeição\s*0?2|M2|R2)',
        r'(?:Almoço|Lunch|Refeição\s*0?3|M3|R3)',
        r'(?:Lanche da Tarde|Merenda|Refeição\s*0?4|M4|R4)',
        r'(?:Jantar|Dinner|Refeição\s*0?5|M5|R5)',
        r'(?:Ceia|Lanche da Noite|Refeição\s*0?6|M6|R6)',
        r'(?:Refeição\s*0?7|M7|R7)',
        r'(?:Refeição\s*0?8|M8|R8)',
        r'(?:Refeição\s*0?9|M9|R9)',
        r'(?:Refeição\s*10|M10|R10)'
    ]
    
    # Encontrar todas as ocorrências de marcadores e suas posições
    found_markers = []
    for pattern in meal_markers:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            found_markers.append({
                "start": m.start(),
                "label": m.group(0).strip(),
                "end": m.end()
            })
    
    # Ordenar por posição no texto
    found_markers.sort(key=lambda x: x["start"])
    
    detected_meals = []
    base_time = 7 # Início padrão 07:00
    
    for i in range(len(found_markers)):
        current = found_markers[i]
        # O conteúdo vai do fim do marcador atual até o início do próximo (ou fim do texto)
        next_start = found_markers[i+1]["start"] if i+1 < len(found_markers) else len(text)
        content = text[current["end"]:next_start].strip()
        
        # 1. Tentar quebrar por novas linhas
        # 2. Se houver muitos hífens na mesma linha, quebrar por hífens também
        raw_lines = content.split('\n')
        content_lines = []
        for rl in raw_lines:
            if ' - ' in rl or ' -' in rl:
                # Quebra itens na mesma linha (ex: "- ovo - pão" -> ["ovo", "pão"])
                content_lines.extend(re.split(r'\s*-\s*', rl))
            else:
                content_lines.append(rl)

        # Limpar e filtrar linhas
        meal_lines = []
        for line in content_lines:
            line = line.strip()
            if not line: continue
            if len(meal_lines) >= 8: break # Aumentado para 8 itens
            if any(x in line.lower() for x in ['página', 'nutricionista', 'paciente', 'data:']): continue
            
            # Remover marcadores iniciais (bullets, hífens), mas preservar números que fazem parte de quantidades (ex: 150g)
            # A regex abaixo remove símbolos e números seguidos de ponto/parêntese (ex: "1.", "1)")
            clean_line = re.sub(r'^[-\.\*•\s]+', '', line).strip()
            clean_line = re.sub(r'^\d+[\.]\s*', '', clean_line).strip() 
            
            if clean_line:
                lower_line = clean_line.lower()
                # Heurística para identificar se é uma dica/recomendação em vez de comida
                is_tip = any(x in lower_line for x in [
                    'evite', 'prefira', 'beba', 'mastigue', 'cuidado', 'lembre-se', 
                    'importante', 'dica', 'observação', 'obs:', 'atenção'
                ]) and not any(x in lower_line for x in [
                    'g ', 'g)', 'g,', 'ml', 'colher', 'fatia', 'unidade', 'und', 
                    'xícara', 'scoop', 'filé', 'bife', 'copo', 'concha', 'escumadeira'
                ])
                
                if is_tip:
                    if "recommendations" not in info: info["recommendations"] = []
                    info["recommendations"].append(clean_line)
                else:
                    meal_lines.append(clean_line)
        
        suggestion = " + ".join(meal_lines) if meal_lines else "Ver documento"
        
        # Tentar achar o horário no conteúdo
        time_match = re.search(r'(\d{1,2}[:h]\d{2})', content)
        time_str = time_match.group(1).replace('h', ':') if time_match else None
        
        if time_str and i == 0:
            try: base_time = int(time_str.split(':')[0])
            except: pass

        # Tentar achar calorias da refeição
        kcal = None
        kcal_match = re.search(r'(\d+)[\s]*(?:kcal|cal|calorias)', content, re.IGNORECASE)
        if kcal_match:
            try:
                kcal = int(kcal_match.group(1))
            except:
                kcal = None

        detected_meals.append({
            "label": current["label"],
            "suggestion": suggestion[:200], # Aumentado para 200 caracteres
            "time": time_str,
            "calories": kcal,
            "full_text": content[:500]
        })

    # Se não tiver horário em algumas, distribuir conforme a ordem
    for i, m in enumerate(detected_meals):
        if not m["time"]:
            h = (base_time + (i * 3)) % 24 # Intervalo de 3h se não especificado
            m["time"] = f"{h:02d}:00"

    info["meals"] = detected_meals
    
    # Se não encontrou calorias totais, mas encontrou por refeição, soma elas
    if not info["total_calories"] and any(m["calories"] for m in detected_meals):
        info["total_calories"] = sum(m["calories"] for m in detected_meals if m["calories"])

    return info
