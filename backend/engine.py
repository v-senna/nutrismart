import json
import random
from datetime import datetime, timedelta


def calculate_tmb(gender: str, weight: float, height: float, age: int) -> float:
    # Fórmula de Mifflin-St Jeor (Padrão ouro na nutrição moderna)
    base = (10 * weight) + (6.25 * height) - (5 * age)
    # Garantir que gender seja string e não None
    gender_str = str(gender or "M").upper()
    if gender_str == 'M':
        return round(base + 5, 1)
    return round(base - 161, 1)


def calculate_tdee(tmb: float, activity_level: str) -> float:
    if not tmb: return 0
    multipliers = {
        "Sedentário": 1.2,       # Pouco ou nenhum exercício
        "Leve": 1.375,           # Exercício leve 1-3 dias/semana
        "Moderado": 1.55,        # Exercício moderado 3-5 dias/semana
        "Intenso": 1.725,        # Exercício pesado 6-7 dias/semana
        "Atleta": 1.9            # Exercício muito pesado ou trabalho físico
    }
    return round(tmb * multipliers.get(activity_level, 1.2), 1)


def get_bmi_classification(bmi: float, age: int) -> str:
    if age >= 60:
        if bmi < 22: return "Baixo peso (< 22 kg/m²) — Idoso"
        if bmi <= 27: return "Peso adequado (22–27 kg/m²) — Idoso"
        return "Sobrepeso (> 27 kg/m²) — Idoso"
    if bmi < 18.5: return "Abaixo do peso"
    if bmi < 25:   return "Peso normal"
    if bmi < 30:   return "Sobrepeso"
    if bmi < 35:   return "Obesidade Grau I"
    if bmi < 40:   return "Obesidade Grau II"
    return "Obesidade Grau III (Mórbida)"


def calculate_water_recommendation(weight: float) -> float:
    if not weight: return 2000.0 # Default fallback
    return weight * 35  # 35 ml por kg


def _distribute_macros(total_calories: float, goal: str, weight: float):
    """
    Distribui macros com base em diretrizes nutricionais clínicas.
    Proteína: 1.8g a 2.4g/kg dependendo do objetivo.
    Gordura: 20% a 30% das calorias totais.
    Carboidratos: O restante das calorias.
    """
    if goal == "Emagrecimento":
        p_g_kg = 2.2 # Preservar massa magra no déficit
        f_pct = 0.25 # 25% de gordura
    elif goal in ("Hipertrofia", "Ganho de Massa Muscular"):
        p_g_kg = 2.0 # Suficiente para síntese proteica no superávit
        f_pct = 0.25 # 25% de gordura
    else: # Manutenção
        p_g_kg = 1.8
        f_pct = 0.30 # 30% de gordura

    p_g = round(p_g_kg * weight)
    p_kcal = p_g * 4
    
    f_kcal = total_calories * f_pct
    f_g = round(f_kcal / 9)
    
    c_kcal = max(0, total_calories - p_kcal - (f_g * 9))
    c_g = round(c_kcal / 4)
    
    return p_g, c_g, f_g


def generate_nutritional_plan(goal: str, tdee: float, weight: float = 70.0,
                               meals_per_day: int = 4, first_meal_time: str = "07:00",
                               meal_times: any = None, target_calories_override: float = None,
                               target_protein_override: float = None,
                               target_carbs_override: float = None,
                               target_fats_override: float = None,
                               imported_meals_data: any = None,
                               imported_tips: any = None,
                               is_custom_diet: bool = False):
    # Garantir que weight não seja None
    weight = weight or 70.0
    tdee = tdee or 2000.0

    # Tratar meal_times se vier como string (JSON)
    if isinstance(meal_times, str):
        try:
            meal_times = json.loads(meal_times)
        except:
            meal_times = None
    # ---------- Cálculo de Calorias Alvo (Déficit/Superávit) ----------
    if target_calories_override:
        target_calories = round(target_calories_override)
    elif goal == "Emagrecimento":
        # Déficit moderado de 20% (mais seguro que fixo de 500)
        target_calories = round(tdee * 0.8)
        # Garantir que não fique abaixo da TMB por segurança
    elif goal in ("Hipertrofia", "Ganho de Massa Muscular"):
        # Superávit moderado de 10-15%
        target_calories = round(tdee * 1.1)
    else:
        target_calories = round(tdee)

    calc_protein, calc_carbs, calc_fats = _distribute_macros(target_calories, goal, weight)
    
    total_protein = round(target_protein_override) if target_protein_override else calc_protein
    total_carbs = round(target_carbs_override) if target_carbs_override else calc_carbs
    total_fats = round(target_fats_override) if target_fats_override else calc_fats


    # ---------- Distribuição de refeições por horário ----------
    meals = []

    if is_custom_diet and imported_meals_data:
        imported_list = []
        if isinstance(imported_meals_data, str):
            try: imported_list = json.loads(imported_meals_data)
            except: pass
        elif isinstance(imported_meals_data, list):
            imported_list = imported_meals_data
            
        if imported_list:
            for m in imported_list:
                meals.append({
                    "time": m.get("time", "08:00"),
                    "label": m.get("label", "Refeição"),
                    "suggestion": m.get("suggestion", ""),
                    "substitutions": "Mantenha a dieta conforme orientada.",
                    "calories": m.get("calories", 0),
                    "protein": m.get("protein", 0),
                    "carbs": m.get("carbs", 0),
                    "fat": m.get("fat", 0),
                })
    
    if not meals:
        MEAL_TEMPLATES = [
        {
            "label": "Café da Manhã",
            "offset_hours": 0,
            "suggestion": "Ovos mexidos (2 und) + pão integral (2 fatias) + 1 fruta",
            "substitutions": (
                "• Troca: tapioca com queijo branco + mamão\n"
                "• Troca: iogurte grego (170g) + granola (30g)\n"
                "• Troca: mingau de aveia (40g) + 1 banana"
            ),
            "macro_share": 0.22,
        },
        {
            "label": "Lanche da Manhã",
            "offset_hours": 3,
            "suggestion": "1 fruta + castanhas (25g)",
            "substitutions": (
                "• Troca: barra de proteína (20g prot)\n"
                "• Troca: 1 iogurte natural + mel\n"
                "• Troca: queijo cottage (100g) + torrada integral"
            ),
            "macro_share": 0.10,
        },
        {
            "label": "Almoço",
            "offset_hours": 4,
            "suggestion": "Frango grelhado (150g) + arroz integral (6 col) + feijão (4 col) + salada à vontade",
            "substitutions": (
                "• Troca de proteína: tilápia grelhada / carne bovina magra / atum\n"
                "• Troca de carboidrato: macarrão integral / mandioca / batata doce\n"
                "• Troca de leguminosa: lentilha / ervilha / grão-de-bico"
            ),
            "macro_share": 0.35,
        },
        {
            "label": "Lanche da Tarde",
            "offset_hours": 8,
            "suggestion": "Iogurte grego (170g) + aveia (30g) ou fruta",
            "substitutions": (
                "• Troca: shake de proteína (1 scoop + leite 200ml)\n"
                "• Troca: omelete de 2 ovos com legumes\n"
                "• Troca: torrada integral + pasta de amendoim (1 col)"
            ),
            "macro_share": 0.13,
        },
        {
            "label": "Jantar",
            "offset_hours": 11,
            "suggestion": "Peixe grelhado (150g) ou frango + legumes refogados + batata doce (100g)",
            "substitutions": (
                "• Troca: omelete proteico (3 ovos + queijo + legumes)\n"
                "• Troca: sopa de frango com legumes e macarrão integral\n"
                "• Troca: carne moída magra (150g) + purê de abóbora"
            ),
            "macro_share": 0.15,
        },
        {
            "label": "Ceia",
            "offset_hours": 14,
            "suggestion": "Caseína ou iogurte grego (200g) + 1 fruta de baixo índice glicêmico",
            "substitutions": (
                "• Troca: queijo cottage (150g) + nozes (20g)\n"
                "• Troca: leite morno (200ml) + mel\n"
                "• Troca: 2 claras cozidas + 1 fatia de pão integral"
            ),
            "macro_share": 0.05,
        },
    ]

    # Seleciona as templates corretas para o número de refeições
    if meals_per_day <= 3:
        selected = [MEAL_TEMPLATES[0], MEAL_TEMPLATES[2], MEAL_TEMPLATES[4]]
    elif meals_per_day == 4:
        selected = [MEAL_TEMPLATES[0], MEAL_TEMPLATES[2], MEAL_TEMPLATES[3], MEAL_TEMPLATES[4]]
    elif meals_per_day == 5:
        selected = [MEAL_TEMPLATES[0], MEAL_TEMPLATES[1], MEAL_TEMPLATES[2],
                    MEAL_TEMPLATES[3], MEAL_TEMPLATES[4]]
    else:
        selected = MEAL_TEMPLATES  # 6 refeições

    # Normalizar shares para somar 1
    total_share = sum(m["macro_share"] for m in selected) or 1

    # Calcular horários a partir do first_meal_time
    try:
        base_h, base_m = map(int, first_meal_time.split(":"))
    except Exception:
        base_h, base_m = 7, 0

    def get_dynamic_suggestion(label, p, c, f, goal):
        is_gain = goal in ("Hipertrofia", "Ganho de Massa Muscular")
        is_loss = goal == "Emagrecimento"
        
        if "Café da Manhã" in label:
            ovos = max(1, round(p / 6.5))
            if is_loss:
                pao = max(1, round((c * 0.4) / 12))
                return f"Ovos mexidos ({ovos} und) + pão integral ({pao} fatia) + Mamão com aveia (150g)"
            else:
                pao = max(2, round((c * 0.6) / 12))
                return f"Ovos mexidos ({ovos} und) + pão integral ({pao} fatias) + Suco de laranja natural (200ml)"
                
        elif "Lanche da Manhã" in label:
            if is_loss:
                return f"1 Maçã ou Pera + Castanhas do Pará (2 und)"
            else:
                granola = max(20, round(c / 0.6))
                return f"Iogurte Natural + Granola ({granola}g) + 1 Banana"
                
        elif "Almoço" in label:
            proteina_g = max(100, round(p / 0.25)) # Considerando ~25% de prot na carne cozida
            if is_loss:
                arroz = max(60, round((c * 0.5) / 0.25))
                return f"Frango ou Peixe grelhado ({proteina_g}g) + arroz integral ({arroz}g) + Brócolis e Cenoura (à vontade) + Azeite (1 col. chá)"
            else:
                arroz = max(150, round((c * 0.6) / 0.25))
                feijao = max(100, round((c * 0.3) / 0.14))
                return f"Carne bovina magra ({proteina_g}g) + arroz ({arroz}g) + feijão ({feijao}g) + Salada mista colorida"
                
        elif "Lanche da Tarde" in label:
            if is_loss:
                return f"Whey Protein (1 scoop) + 10 morangos ou 1 kiwi"
            else:
                pao = max(2, round((c * 0.5) / 12))
                frango_desfiado = max(50, round(p / 0.25))
                return f"Sanduíche de frango ({frango_desfiado}g) no pão integral ({pao} fatias) + Suco de uva integral (200ml)"
                
        elif "Jantar" in label:
            proteina_g = max(100, round(p / 0.25))
            if is_loss:
                return f"Omelete (3 ovos) com espinafre e tomate + Mix de folhas verdes + Azeite de Oliva"
            else:
                massa = max(100, round(c / 0.3))
                return f"Macarrão integral ({massa}g) com patinho moído ({proteina_g}g) + Molho de tomate natural e manjericão"
        else: # Ceia
            if is_loss:
                return f"Iogurte desnatado (200g) ou Mix de nozes (20g)"
            else:
                abacate = max(80, round(f / 0.15))
                return f"Abacate ({abacate}g) com Whey Protein ou Leite integral com mel"

    meals = []
    for i, tmpl in enumerate(selected):
        share = tmpl["macro_share"] / total_share
        
        # Usar horário definido pelo usuário se existir
        # Garantir que temos uma lista válida para acesso por índice
        safe_meal_times = meal_times if isinstance(meal_times, list) else []
        
        cal   = round(target_calories * share)
        prot  = round(total_protein   * share)
        carbs = round(total_carbs     * share)
        fat   = round(total_fats      * share)

        # Usar horário definido pelo usuário se existir, senão calcular
        if i < len(safe_meal_times) and safe_meal_times[i]:
            time_str = safe_meal_times[i]
        else:
            meal_h = (base_h + tmpl["offset_hours"]) % 24
            time_str = f"{meal_h:02d}:{base_m:02d}"

        # Tratar imported_meals_data
        imported_list = []
        if isinstance(imported_meals_data, str):
            try: imported_list = json.loads(imported_meals_data)
            except: pass
        elif isinstance(imported_meals_data, list):
            imported_list = imported_meals_data

        # Priorizar sugestão importada se houver e for válida
        suggestion = None
        imported_text = ""
        if i < len(imported_list) and isinstance(imported_list[i], dict) and imported_list[i].get("suggestion"):
            imported_text = imported_list[i]["suggestion"].strip()
            
        # Heurística para verificar se o texto importado é "fraco" (ex: "Similar ao almoço", ou template vazio "+ g de")
        is_weak_text = False
        lower_text = imported_text.lower()
        if not imported_text or len(imported_text) < 5:
            is_weak_text = True
        elif any(x in lower_text for x in ["similar ao", "igual ao", "mesmo do", "repetir"]):
            is_weak_text = True
        elif "+ g de" in lower_text or " g de " in lower_text:
            # Parece um template vazio sem números
            is_weak_text = True
            
        if imported_text and not is_weak_text:
            suggestion = imported_text
        else:
            # Se for fraco ou não existir, usa a inteligência interna do NutriSmart para gerar uma refeição completa
            dyn = get_dynamic_suggestion(tmpl["label"], prot, carbs, fat, goal)
            if "similar ao" in lower_text:
                suggestion = f"{dyn} (Substituindo '{imported_text}')"
            else:
                suggestion = dyn

        meals.append({
            "time":          time_str,
            "label":         tmpl["label"],
            "suggestion":    suggestion,
            "substitutions": tmpl["substitutions"],
            "calories":      cal,
            "protein":       prot,
            "carbs":         carbs,
            "fat":           fat,
        })


    # ---------- Dicas ----------
    tips = [
        "Beba pelo menos 35ml de água por quilo de peso corporal ao longo do dia.",
        "Tente dormir de 7 a 8 horas para garantir a recuperação muscular.",
        "Inclua uma fonte de proteína em todas as suas refeições principais.",
        "Pratos coloridos garantem maior variedade de micronutrientes.",
        "Evite ultraprocessados; prefira alimentos in natura ou minimamente processados.",
        "A musculação ajuda a queimar calorias mesmo em repouso.",
        "Mastigue devagar — a saciedade demora ~20 min para chegar ao cérebro.",
        "Planeje as refeições com antecedência para não furar a dieta na correria.",
        "Não risque o café da manhã — ele dá energia para o metabolismo acordar.",
        "Proteínas em todas as refeições ajudam a controlar a glicemia e a fome.",
    ]

    if goal == "Emagrecimento":
        tips.append("⚠️ ALERTA: Não reduza calorias drasticamente — pode causar efeito sanfona.")
        tips.append("💡 DICA: Fibras e proteínas aumentam a saciedade e facilitam o déficit.")
    elif goal in ("Ganho de Massa Muscular", "Hipertrofia"):
        tips.append("⚠️ ALERTA: Superávit calórico não significa comer besteiras. Foque em comida limpa.")
        tips.append("💡 DICA: O treino é o gatilho; a proteína é o tijolo para construir músculo.")

    random.shuffle(tips)
    selected_tips = tips[:8]

    # Mesclar com dicas importadas se houver
    if imported_tips:
        if isinstance(imported_tips, str):
            try: imported_tips = json.loads(imported_tips)
            except: pass
        
        if isinstance(imported_tips, list):
            # Limpar e filtrar dicas vazias
            clean_imported = [str(t).strip() for t in imported_tips if t and str(t).strip()]
            # Adicionar ao topo das recomendações (limitando a 5 para não poluir demais)
            selected_tips = clean_imported[:5] + selected_tips
            # Garantir que não passamos de 12 dicas no total
            selected_tips = selected_tips[:12]

    recommendations = "|||".join(selected_tips)

    return {
        "calories_target": target_calories,
        "protein_target":  total_protein,
        "carbs_target":    total_carbs,
        "fats_target":     total_fats,
        "meals":           meals,
        "recommendations": recommendations,
    }


def generate_weight_projection(weight: float, goal: str, duration_weeks: int):
    projection = []
    weight = weight or 70.0
    goal_str = str(goal or "Manutenção")
    rate = -0.5 if "Emagrecimento" in goal_str else (0.3 if "Ganho" in goal_str or "Hipertrofia" in goal_str else 0)
    now = datetime.now()
    for i in range(duration_weeks * 7):
        date = now + timedelta(days=i)
        projection.append({
            "day":    i,
            "date":   date.strftime("%d/%m"),
            "weight": round(weight + (rate / 7 * i), 2),
        })
    return projection


def recalculate_projection_with_logs(profile, weight_logs: list):
    duration_weeks = (profile.project_duration_months or 12) * 4
    return json.dumps(generate_weight_projection(profile.weight, profile.goals, duration_weeks))


def recalculate_remaining_meals_for_today(meals: list, missed_meal_name: str) -> list:
    """
    Se uma refeição foi pulada, redistribui as macros dela para as próximas refeições do dia.
    """
    missed_index = -1
    for i, m in enumerate(meals):
        if m["label"] == missed_meal_name:
            missed_index = i
            break
            
    if missed_index == -1 or missed_index == len(meals) - 1:
        # Refeição não encontrada ou é a última refeição do dia (não há para onde redistribuir hoje)
        return meals
        
    missed_meal = meals[missed_index]
    remaining_meals_count = len(meals) - 1 - missed_index
    
    extra_cal = missed_meal.get("calories", 0) / remaining_meals_count
    extra_prot = missed_meal.get("protein", 0) / remaining_meals_count
    extra_carbs = missed_meal.get("carbs", 0) / remaining_meals_count
    extra_fat = missed_meal.get("fat", 0) / remaining_meals_count
    
    # Zera a refeição perdida (opcional, ou podemos apenas deixá-la como estava, mas no plano já foi)
    # Vamos manter a refeição lá, mas redistribuir as macros nas próximas
    
    for i in range(missed_index + 1, len(meals)):
        meals[i]["calories"] = round(meals[i].get("calories", 0) + extra_cal)
        meals[i]["protein"] = round(meals[i].get("protein", 0) + extra_prot)
        meals[i]["carbs"] = round(meals[i].get("carbs", 0) + extra_carbs)
        meals[i]["fat"] = round(meals[i].get("fat", 0) + extra_fat)
        # Adiciona um aviso na sugestão informando que as quantidades devem aumentar
        meals[i]["suggestion"] = f"[RECALCULADO: +{round(extra_cal)} Kcal (+{round(extra_prot)}g Prot, +{round(extra_carbs)}g Carb)] {meals[i].get('suggestion', '')}"
        
    return meals
