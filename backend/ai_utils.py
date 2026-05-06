import re
import io
import pandas as pd
from pypdf import PdfReader

def extract_text_from_pdf(file_content):
    reader = PdfReader(io.BytesIO(file_content))
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_excel(file_content):
    try:
        df = pd.read_excel(io.BytesIO(file_content))
        return df.to_string()
    except Exception as e:
        print(f"Excel extraction error: {e}")
        return ""

def parse_diet_info(text):
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
        "total_calories": None
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

    # Heurísticas para Refeições
    # Procura por horários e nomes de refeições comuns
    meal_patterns = [
        r'(Café da Manhã|Desjejum|Breakfast|Refeição 1)[\s:]+(.*?)(?=(?:Lanche|Almoço|Jantar|Ceia|Refeição \d|$))',
        r'(Lanche da Manhã|Colação|Refeição 2)[\s:]+(.*?)(?=(?:Almoço|Lanche|Jantar|Ceia|Refeição \d|$))',
        r'(Almoço|Lunch|Refeição 3)[\s:]+(.*?)(?=(?:Lanche|Jantar|Ceia|Refeição \d|$))',
        r'(Lanche da Tarde|Merenda|Refeição 4)[\s:]+(.*?)(?=(?:Jantar|Ceia|Refeição \d|$))',
        r'(Jantar|Dinner|Refeição 5)[\s:]+(.*?)(?=(?:Ceia|Lanche|Refeição \d|$))',
        r'(Ceia|Refeição 6)[\s:]+(.*?)(?=$)'
    ]

    detected_meals = []
    base_time = 7 # Início padrão 07:00
    
    for pattern in meal_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
        for match in matches:
            label = match.group(1).strip()
            content = match.group(2).strip()
            
            # Tentar achar o horário no conteúdo ou perto da label
            time_match = re.search(r'(\d{1,2}[:h]\d{2})', content + " " + label)
            time_str = time_match.group(1).replace('h', ':') if time_match else None
            
            if time_str and label.lower().startswith(("café", "desjejum")):
                try: base_time = int(time_str.split(':')[0])
                except: pass

            # Tentar achar calorias da refeição
            # Procura por "X kcal" ou "X cal"
            kcal_match = re.search(r'(\d+)[\s]*(?:kcal|cal|calorias)', content, re.IGNORECASE)
            kcal = int(kcal_match.group(1)) if kcal_match else None
            
            # Limpar o conteúdo para pegar a sugestão principal
            lines = [l.strip() for l in content.split('\n') if l.strip() and 'kcal' not in l.lower() and 'prot' not in l.lower()]
            suggestion = " e ".join(lines[:2]) if lines else "Ver documento"

            detected_meals.append({
                "label": label,
                "suggestion": suggestion[:150],
                "time": time_str, # Mantém None se não achar, para distribuir depois
                "calories": kcal,
                "full_text": content
            })

    # Se não tiver horário em algumas, distribuir conforme a ordem
    for i, m in enumerate(detected_meals):
        if not m["time"]:
            h = (base_time + (i * 4)) % 24
            m["time"] = f"{h:02d}:00"

    info["meals"] = detected_meals
    
    # Se não encontrou calorias totais, mas encontrou por refeição, soma elas
    if not info["total_calories"] and any(m["calories"] for m in detected_meals):
        info["total_calories"] = sum(m["calories"] for m in detected_meals if m["calories"])

    return info
