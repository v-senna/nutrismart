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
    df = pd.read_excel(io.BytesIO(file_content))
    return df.to_string()

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
        "meals": []
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

    # Heurísticas para Refeições
    # Procura por horários e nomes de refeições comuns
    meal_patterns = [
        r'(Café da Manhã|Desjejum|Breakfast)[\s:]+(.*?)(?=(?:Lanche|Almoço|Jantar|Ceia|$))',
        r'(Lanche da Manhã|Colação)[\s:]+(.*?)(?=(?:Almoço|Lanche|Jantar|Ceia|$))',
        r'(Almoço|Lunch)[\s:]+(.*?)(?=(?:Lanche|Jantar|Ceia|$))',
        r'(Lanche da Tarde|Merenda)[\s:]+(.*?)(?=(?:Jantar|Ceia|$))',
        r'(Jantar|Dinner)[\s:]+(.*?)(?=(?:Ceia|Lanche|$))',
        r'(Ceia)[\s:]+(.*?)(?=$)'
    ]

    for pattern in meal_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            label = match.group(1).strip()
            content = match.group(2).strip()
            
            # Tentar achar o horário no conteúdo ou perto da label
            time_match = re.search(r'(\d{1,2}[:h]\d{2})', content + " " + label)
            time_str = time_match.group(1).replace('h', ':') if time_match else "00:00"
            
            info["meals"].append({
                "label": label,
                "suggestion": content.split('\n')[0][:100], # Primeira linha como sugestão
                "time": time_str,
                "full_text": content
            })

    return info
