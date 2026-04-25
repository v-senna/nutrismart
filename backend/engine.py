import json
import random
from datetime import datetime, timedelta


def calculate_tmb(gender: str, weight: float, height: float, age: int) -> float:
    base = (10 * weight) + (6.25 * height) - (5 * age)
    if gender.upper() == 'M':
        return round(base + 5, 1)
    return round(base - 161, 1)


def calculate_tdee(tmb: float, activity_level: str) -> float:
    multipliers = {
        "Sedentário": 1.2,
        "Leve": 1.375,
        "Moderado": 1.55,
        "Intenso": 1.725,
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
    return weight * 35  # 35 ml por kg


def _distribute_macros(total_calories: float, protein_g: float, fat_g: float, weight: float):
    """Distribui macros totais em gramas a partir do TDEE e fatores por kg."""
    p_g  = round(protein_g * weight)
    f_g  = round(fat_g * weight)
    p_kcal = p_g * 4
    f_kcal = f_g * 9
    c_kcal = max(0, total_calories - p_kcal - f_kcal)
    c_g   = round(c_kcal / 4)
    return p_g, c_g, f_g


def generate_nutritional_plan(goal: str, tdee: float, weight: float = 70.0,
                               meals_per_day: int = 4, first_meal_time: str = "07:00"):
    # ---------- Macros por objetivo ----------
    if goal == "Emagrecimento":
        target_calories = round(tdee - 500)
        protein_g_per_kg, fat_g_per_kg = 2.0, 0.8
    elif goal in ("Hipertrofia", "Ganho de Massa Muscular"):
        target_calories = round(tdee + 300)
        protein_g_per_kg, fat_g_per_kg = 2.2, 1.0
    else:  # Manutenção
        target_calories = round(tdee)
        protein_g_per_kg, fat_g_per_kg = 1.8, 1.0

    total_protein, total_carbs, total_fats = _distribute_macros(
        target_calories, protein_g_per_kg, fat_g_per_kg, weight
    )

    # ---------- Distribuição de refeições por horário ----------
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
    total_share = sum(m["macro_share"] for m in selected)

    # Calcular horários a partir do first_meal_time
    try:
        base_h, base_m = map(int, first_meal_time.split(":"))
    except Exception:
        base_h, base_m = 7, 0

    def get_dynamic_suggestion(label, p, c, f):
        if "Café da Manhã" in label:
            ovos = max(1, round(p / 6))
            pao = max(1, round((c * 0.6) / 12))
            fruta = max(1, round((c * 0.4) / 15))
            return f"Ovos mexidos ({ovos} und) + pão integral ({pao} fatias) + {fruta} porção(ões) de fruta"
        elif "Lanche da Manhã" in label:
            fruta = max(1, round(c / 15))
            castanhas = max(10, round(f / 0.5))
            return f"{fruta} porção(ões) de fruta + castanhas ({castanhas}g)"
        elif "Almoço" in label:
            frango = max(50, round(p / 0.3))
            arroz = max(30, round((c * 0.7) / 0.28))
            feijao = max(20, round((c * 0.3) / 0.14))
            return f"Frango grelhado ({frango}g) + arroz integral ({arroz}g) + feijão ({feijao}g) + salada à vontade"
        elif "Lanche da Tarde" in label:
            iogurte = max(100, round(p / 0.1))
            aveia = max(10, round(c / 0.6))
            return f"Iogurte grego ({iogurte}g) + aveia ({aveia}g) ou fruta"
        elif "Jantar" in label:
            carne = max(50, round(p / 0.3))
            batata = max(50, round(c / 0.2))
            return f"Peixe/Frango grelhado ({carne}g) + legumes refogados + batata doce ({batata}g)"
        else:
            iogurte = max(100, round(p / 0.1))
            fruta = max(1, round(c / 15))
            return f"Caseína ou iogurte grego ({iogurte}g) + {fruta} porção(ões) de fruta"

    meals = []
    for tmpl in selected:
        share = tmpl["macro_share"] / total_share
        cal   = round(target_calories * share)
        prot  = round(total_protein   * share)
        carbs = round(total_carbs     * share)
        fat   = round(total_fats      * share)

        meal_h = (base_h + tmpl["offset_hours"]) % 24
        time_str = f"{meal_h:02d}:{base_m:02d}"

        meals.append({
            "time":          time_str,
            "label":         tmpl["label"],
            "suggestion":    get_dynamic_suggestion(tmpl["label"], prot, carbs, fat),
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
    recommendations = "|||".join(tips[:8])

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
    rate = -0.5 if goal == "Emagrecimento" else (0.3 if "Ganho" in goal else 0)
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
    return json.dumps(generate_weight_projection(profile.weight, profile.goal, 12))
