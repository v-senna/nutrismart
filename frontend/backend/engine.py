def calculate_tmb(weight: float, height: float, age: int, gender: str) -> float:
    # Mifflin-St Jeor Equation
    base = (10 * weight) + (6.25 * height) - (5 * age)
    if gender.upper() == 'M':
        return base + 5
    else:
        return base - 161

def get_bmi_classification(bmi: float, age: int) -> str:
    """Classificação de IMC atualizada (OPAS para idosos, OMS para adultos/crianças)."""
    if age >= 60:
        # Padrão OPAS/SBC para Idosos
        if bmi < 22: return "Baixo peso (< 22 kg/m²) — Idoso"
        if bmi <= 27: return "Peso adequado (22–27 kg/m²) — Idoso"
        return "Sobrepeso (> 27 kg/m²) — Idoso"
    elif age >= 2 and age < 20:
        # OMS Escore-Z simplificado (2–19 anos)
        if bmi < 13.5: return "Magreza Acentuada (Escore-Z < -3) — OMS Infantil"
        if bmi < 15.5: return "Magreza (Escore-Z entre -3 e -2) — OMS Infantil"
        if bmi < 22:   return "Peso Normal (Escore-Z entre -2 e +1) — OMS Infantil"
        if bmi < 26:   return "Sobrepeso (Escore-Z entre +1 e +2) — OMS Infantil"
        if bmi < 30:   return "Obesidade (Escore-Z entre +2 e +3) — OMS Infantil"
        return "Obesidade Grave (Escore-Z > +3) — OMS Infantil"
    else:
        # Tabela OMS / ABESO (Adulto)
        if bmi < 18.5: return "Abaixo do peso"
        if bmi < 25: return "Peso normal"
        if bmi < 30: return "Sobrepeso"
        if bmi < 35: return "Obesidade Grau I"
        if bmi < 40: return "Obesidade Grau II"
        return "Obesidade Grau III (Mórbida)"

def get_tdee(tmb: float, activity_level: str) -> float:
    multipliers = {
        "Sedentário": 1.2,
        "Leve": 1.375,
        "Moderado": 1.55,
        "Intenso": 1.725,
    }
    return tmb * multipliers.get(activity_level, 1.2)

def calculate_plan(profile) -> dict:
    tmb = calculate_tmb(profile.weight, profile.height, profile.age, profile.gender)
    tdee = get_tdee(tmb, profile.activity_level)
    imc = profile.weight / ((profile.height / 100) ** 2)
    imc_class = get_bmi_classification(imc, profile.age)
    
    # Target Calories
    if profile.goals == "Emagrecimento":
        target_calories = tdee - 500
        protein = profile.weight * 2.2 # Mais proteína para conservar massa
        fat = profile.weight * 1.0
    elif profile.goals == "Hipertrofia" or profile.goals == "Ganho de Massa Muscular":
        target_calories = tdee + 300
        protein = profile.weight * 2.0
        fat = profile.weight * 1.0
    else: # Manutenção
        target_calories = tdee
        protein = profile.weight * 1.8
        fat = profile.weight * 1.0
        
    calories_from_protein = protein * 4
    calories_from_fat = fat * 9
    remaining_calories = target_calories - calories_from_protein - calories_from_fat
    carbs = remaining_calories / 4 if remaining_calories > 0 else 0
    
    water = profile.weight * 35 # ml
    
    import random
    
    # 1. Dicas Dinâmicas
    dicas_gerais = [
        "O sono é tão importante quanto o treino. Tente dormir entre 7 e 8 horas por noite.",
        "A consistência supera a perfeição. Fazer o básico bem feito todos os dias traz mais resultados.",
        "Não tenha medo dos carboidratos, eles são a principal fonte de energia para os seus treinos.",
        "Pratos coloridos garantem uma maior variedade de vitaminas e minerais.",
        "Mastigar os alimentos mais devagar ajuda na digestão e aumenta a saciedade.",
        "Tente tomar de 15 a 20 minutos de sol por dia para auxiliar nos níveis de Vitamina D.",
        "Beba água regularmente. A desidratação pode ser confundida com fome pelo cérebro.",
        "Substitua o sal por temperos naturais como ervas, limão e alho para reduzir o sódio.",
        "Inclua gorduras boas como azeite e castanhas para a saúde hormonal.",
        "Evite ultraprocessados: descasque mais e desembalar menos.",
        "A musculação acelera o metabolismo mesmo quando você está em repouso.",
        "Consuma fibras (frutas e grãos) para manter a saúde intestinal em dia.",
        "Planeje suas refeições no domingo para evitar escolhas ruins durante a semana.",
        "Use canela e gengibre para um leve estímulo termogênico natural.",
        "Evite distrações (celular/TV) ao comer para perceber melhor a saciedade.",
        "Cansaço pode ser desidratação; beba água antes de buscar um café extra.",
        "Prefira frutas inteiras ao suco para aproveitar todas as fibras.",
        "Sementes de chia e linhaça são excelentes fontes de ômega-3 vegetal.",
        "Vitamina C ajuda na absorção do ferro vegetal presente no feijão.",
        "Iogurte natural é um ótimo probiótico para a flora intestinal.",
        "O magnésio das sementes ajuda no relaxamento muscular e qualidade do sono.",
        "Faça refeições conscientes, focando totalmente no sabor e textura do alimento."
    ]
    
    # Send all tips for rotation
    tips_joined = "|||".join(dicas_gerais)
    
    # 2. Cardápios de Exemplo baseados em evidência
    meals_count = getattr(profile, 'meals_per_day', 4) or 4
    first_meal_str = getattr(profile, 'first_meal_time', '08:00') or '08:00'
    
    try:
        from datetime import datetime, timedelta
        start_time = datetime.strptime(first_meal_str, "%H:%M")
    except:
        start_time = datetime.strptime("08:00", "%H:%M")

    # Distribuição dinãmica: Janela de 14 horas
    window_hours = 14
    if meals_count > 1:
        interval = window_hours / (meals_count - 1)
    else:
        interval = 0

    MEAL_LABELS = {
        1: ["Almoço"],
        2: ["Café da Manhã", "Jantar"],
        3: ["Café da Manhã", "Almoço", "Jantar"],
        4: ["Café da Manhã", "Almoço", "Lanche da Tarde", "Jantar"],
        5: ["Café da Manhã", "Lanche da Manhã", "Almoço", "Jantar", "Ceia"],
        6: ["Café da Manhã", "Lanche da Manhã", "Almoço", "Lanche da Tarde", "Jantar", "Ceia"]
    }

    SUGGESTIONS = {
        "Café da Manhã": "2 ovos mexidos, 1 fatia de pão integral, 100g de frutas (mamão/morango).",
        "Lanche da Manhã": "1 unidade de iogurte natural desnatado com 1 colher de farelo de aveia.",
        "Almoço": "150g de filé de frango ou carne magra, 100g de arroz integral, 1 concha de feijão e salada verde à vontade.",
        "Lanche da Tarde": "1 fruta (maçã/banana) e 3 unidades de castanha-do-pará.",
        "Jantar": "120g de proteína grelhada (peixe/frango) com mix de legumes cozidos (brócolis, cenoura, abobrinha).",
        "Ceia": "1 xícara de chá de camomila e 2 torradas integrais leves.",
        "Lanche": "1 barra de cereal proteica ou 1 fruta com aveia."
    }

    SUBSTITUTIONS = {
        "Café da Manhã": "Para os ovos ➔ 2 Fatias de queijo branco, Cottage ou tofu.\nPara o pão/fruta ➔ Tapioca (2 colheres) ou Rap 10 integral.",
        "Lanche da Manhã": "Para o iogurte ➔ Shake com 1 dose de Whey Protein.\nPara a aveia ➔ Mix de castanhas (20g).",
        "Almoço": "Para a proteína ➔ Peixe (Tilápia/Salmão), ovos ou carne moída magra.\nPara o carbo ➔ Batata Doce (100g), mandioca ou macarrão integral.",
        "Lanche da Tarde": "Para a fruta/castanha ➔ Iogurte grego zero ou 2 fatias de queijo minas frescal com geleia sem açúcar.",
        "Jantar": "Para a proteína grelhada ➔ Omelete de 3 ovos com espinafre.\nPara os legumes ➔ Sopa de legumes desintoxicante.",
        "Ceia": "Para a ceia morna ➔ Abacate (50g) com chia ou 1 copo de leite desnatado.",
        "Lanche": "Para a barra ➔ Iogurte natural ou 1 punhado de amendoim sem sal."
    }
    
    labels = MEAL_LABELS.get(meals_count, MEAL_LABELS[4])
    cal_per_meal = target_calories / meals_count
    prot_per_meal = protein / meals_count
    fat_per_meal = fat / meals_count
    carb_per_meal = max(0, carbs / meals_count)
    
    # Structured Meals for Frontend
    meals_list = []
    for i, label in enumerate(labels):
        meal_time = start_time + timedelta(hours=i * interval)
        meals_list.append({
            "time": meal_time.strftime("%H:%M"),
            "label": label,
            "suggestion": SUGGESTIONS.get(label, "Sugestão nutritiva equilibrada com foco em proteínas e fibras."),
            "substitutions": SUBSTITUTIONS.get(label, "Trocar por outra fonte de proteína magra e carboidrato complexo similar."),
            "calories": round(cal_per_meal, 1),
            "protein": round(prot_per_meal, 1),
            "carbs": round(carb_per_meal, 1),
            "fat": round(fat_per_meal, 1)
        })
    
    # Textual Summary with Science-Based Health Alert
    alerts_and_tips = []
    
    # 1. Health Risk Alerts based on Meal Interval
    if interval > 4.0:
        if interval > 6.0:
             alerts_and_tips.append(
                "**ALERTA CRÍTICO DE RISCO**: Seu intervalo de " + str(round(interval, 1)) + "h entre refeições entra em 'Estado de Inanição'. "
                "Cientificamente, isso dispara o cortisol e silencia a queima de gordura, forçando o corpo a estocar tecido adiposo visceral "
                "como reserva de emergência e canibalizar massa muscular para obter glicose."
            )
        else:
            alerts_and_tips.append(
                "**ALERTA METABÓLICO**: O intervalo de " + str(round(interval, 1)) + "h excede o limite de eficiência. "
                "Estudos indicam que após 4h sem nutrientes, o metabolismo desacelera significativamente para poupar energia, "
                "facilitando o ganho de gordura na próxima refeição devido ao pico exagerado de insulina."
            )

    # 2. Smart Tips based on BMI - usando limiares corretos por faixa etária
    age_val = getattr(profile, 'age', 30) or 30
    imc_low = 22 if age_val >= 60 else (15.5 if age_val < 20 else 18.5)
    imc_high = 30

    if imc > imc_high:
        alerts_and_tips.append("**DICA DE SAÚDE**: Seu IMC indica sobrecarga articular. Priorize atividades de baixo impacto e foque no consumo de fibras para controle glicêmico.")
    elif imc < imc_low:
        if age_val >= 60:
            alerts_and_tips.append("**ALERTA - BAIXO PESO (OPAS)**: IMC abaixo de 22 em pessoas com mais de 60 anos indica risco de desnutrição e sarcopenia segundo a OPAS. Busque orientação médica e aumente o aporte proteico.")
        elif age_val < 20:
            alerts_and_tips.append("**DICA INFANTIL (OMS)**: IMC baixo para a faixa etária. Avalie com Escore-Z por um profissional de saúde para verificar estado nutricional adequado.")
        else:
            alerts_and_tips.append("**DICA DE PERFORMANCE**: Seu IMC atual sugere a necessidade de superavit proteico. Não pule refeições para evitar o catabolismo muscular.")
    
    # 3. Smart Tips based on Goals
    if profile.goals == "Emagrecimento":
        alerts_and_tips.append("**ESTRATÉGIA**: Beba 500ml de água antes das refeições principais. Isso pode aumentar o gasto calórico em repouso em até 30% nos 60 minutos seguintes.")
    elif profile.goals == "Hipertrofia" or profile.goals == "Ganho de Massa Muscular":
        alerts_and_tips.append("**ESTRATÉGIA**: A síntese proteica é otimizada com a ingestão a cada 4 horas. Seu intervalo atual é de " + str(round(interval, 1)) + "h.")

    # 4. Integrate with General Tips
    import random
    general_tips = tips_joined.split("|||")
    # Mix some random ones but prioritize the smart ones at the beginning
    random_general = random.sample(general_tips, min(len(general_tips), 10))
    final_tips_list = alerts_and_tips + random_general
    
    tips_and_menu = "|||".join(final_tips_list)

    
    from datetime import datetime, timedelta
    
    dias_semana_full = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]
    # Ajustar para o fuso horário do usuário (UTC-3)
    now_utc = datetime.utcnow()
    now_local = now_utc - timedelta(hours=3)
    start_date = now_local.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    import json
    projection_data = []
    
    rate = 0
    if hasattr(profile, 'target_weight') and profile.target_weight and profile.target_weight != profile.weight:
        diff = profile.target_weight - profile.weight
        
        rate = 0
        if profile.goals == "Emagrecimento" and diff < 0:
            rate = -0.8 / 7 
        elif (profile.goals == "Hipertrofia" or profile.goals == "Ganho de Massa Muscular") and diff > 0:
            rate = 0.5 / 7
            
        target = profile.target_weight
        
        if rate == 0:
            # Forçar uma tendência se o objetivo for definido, mesmo sem meta clara
            if profile.goals == "Hipertrofia" or profile.goals == "Ganho de Massa Muscular":
                rate = 0.5 / 7 # 500g por semana
            elif profile.goals == "Emagrecimento":
                rate = -0.7 / 7 # 700g por semana
                
        # Recalcular target se for inconsistente
        if rate > 0 and (target is None or target <= profile.weight):
            target = profile.weight + 5 # Sugere +5kg
        elif rate < 0 and (target is None or target >= profile.weight):
            target = profile.weight - 5 # Sugere -5kg

        # Ponto inicial (Amanhã)
        projection_data.append({
            "day": 0,
            "date": f"dia {start_date.strftime('%d/%m')} {dias_semana_full[start_date.weekday()]}",
            "weight": round(profile.weight, 1),
            "target": round(target, 1),
            "trend": round(profile.weight, 1)
        })
        
        # Calculamos para a duração escolhida pelo usuário
        duration_months = getattr(profile, 'project_duration_months', 12) or 12
        total_days = (duration_months * 30) - 1

        weeks_total = int(abs((target - profile.weight) / (rate * 7))) if rate != 0 else (duration_months * 4)
        days_to_target = weeks_total * 7 if weeks_total > 0 else 7 # Evitar zero
        
        for d in range(1, total_days + 1):
            current_date = start_date + timedelta(days=d)
            proj_w = profile.weight + (rate * d)
            
            # Trend ideal (reta até o alvo)
            if d <= days_to_target:
                ideal_trend = profile.weight + ((target - profile.weight) / days_to_target * d)
            else:
                ideal_trend = target
                
            # Só projetamos o 'weight' até atingir a meta, depois fica nulo ou constante
            current_proj = proj_w if (rate < 0 and proj_w > target) or (rate > 0 and proj_w < target) else target

            projection_data.append({
                "day": d,
                "date": f"dia {current_date.strftime('%d/%m')} {dias_semana_full[current_date.weekday()]}",
                "weight": round(current_proj, 1),
                "target": round(target, 1),
                "trend": round(ideal_trend, 1)
            })
    else:
        # Default rate based on goal if no target weight set or it's equal to current weight
        if profile.goals == "Hipertrofia" or profile.goals == "Ganho de Massa Muscular":
            rate = 0.5 / 7
        elif profile.goals == "Emagrecimento":
            rate = -0.7 / 7
        else:
            rate = 0

        duration_months = getattr(profile, 'project_duration_months', 12) or 12
        total_days = duration_months * 30
        for d in range(0, total_days):
            current_date = start_date + timedelta(days=d)
            proj_w = profile.weight + (rate * d)
            projection_data.append({
                "day": d,
                "date": f"dia {current_date.strftime('%d/%m')} {dias_semana_full[current_date.weekday()]}",
                "weight": round(proj_w, 1),
                "target": round(profile.weight, 1),
                "trend": round(proj_w, 1)
            })
    
    return {
        "tmb": round(tmb, 2),
        "tdee": round(tdee, 2),
        "imc": round(imc, 2),
        "imc_classification": imc_class,
        "target_calories": round(target_calories, 2),
        "target_protein": round(protein, 2),
        "target_fats": round(fat, 2),
        "target_carbs": round(carbs, 2),
        "water_recommendation": round(water, 2),
        "recommendations_text": tips_and_menu,
        "projection_data": json.dumps(projection_data),
        "meals_json": json.dumps(meals_list)
    }


def recalculate_projection_with_logs(profile, weight_logs: list) -> str:
    """Rebuild projection_data injecting real weigh-in logs.
    Each log contributes a 'real' data point alongside the original projection."""
    import json
    from datetime import datetime, timedelta

    dias_semana_full = ["domingo", "segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado"]
    
    # Ajustar para o fuso horário local (UTC-3)
    now_utc = datetime.utcnow()
    now_local = now_utc - timedelta(hours=3)
    # HOJE é o dia 0
    today_start = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Usar o peso inicial do perfil se não houver logs, ou o peso do perfil como o mais recente
    current_weight = profile.weight
    target_weight = getattr(profile, 'target_weight', None) or (current_weight - 5 if profile.goals == "Emagrecimento" else current_weight + 5)

    if profile.goals == "Emagrecimento":
        rate = -0.8 / 7
    elif profile.goals == "Hipertrofia" or profile.goals == "Ganho de Massa Muscular":
        rate = 0.5 / 7
    else:
        rate = 0.0

    duration_months = getattr(profile, 'project_duration_months', 12) or 12
    total_days = duration_months * 30
    
    # Se o objetivo for alcançado, a taxa vira 0 (manutenção)
    if (profile.goals == "Emagrecimento" and current_weight <= target_weight) or \
       ((profile.goals == "Hipertrofia" or profile.goals == "Ganho de Massa Muscular") and current_weight >= target_weight):
        rate = 0.0

    # Determinar quantos dias faltam para a meta a partir de HOJE
    if rate != 0:
        days_to_target = int(abs((target_weight - current_weight) / (rate * 7)) * 7)
    else:
        days_to_target = total_days

    # Mapear logs: encontrar o OFFSET de cada log em relação a HOJE
    log_by_day = {}
    for log in weight_logs:
        log_local = log.logged_at - timedelta(hours=3)
        log_date = log_local.replace(hour=0, minute=0, second=0, microsecond=0)
        # Offset em relação a hoje (pode ser negativo para logs passados)
        offset = (log_date - today_start).days
        log_by_day[offset] = round(log.weight, 1)

    projection_data = []
    
    # Mostrar um pouco do passado (-7 dias) e o futuro (total_days)
    for d in range(-7, total_days):
        current_date_obj = today_start + timedelta(days=d)
        
        # Tendência ideal (reta que liga o peso atual à meta futura)
        if d < 0:
            # No passado, projetamos para trás a partir do peso atual
            proj_w = current_weight - (rate * abs(d))
            ideal_trend = current_weight - (rate * abs(d))
        else:
            # No futuro, projetamos a partir do peso atual
            if d <= days_to_target:
                proj_w = current_weight + (rate * d)
                ideal_trend = current_weight + ((target_weight - current_weight) / max(1, days_to_target) * d)
            else:
                proj_w = target_weight
                ideal_trend = target_weight

        entry = {
            "day": d,
            "date": f"{current_date_obj.strftime('%d/%m')} {dias_semana_full[current_date_obj.weekday()]}",
            "weight": round(proj_w, 1),
            "target": round(target_weight, 1),
            "trend": round(ideal_trend, 1),
        }
        
        # Injetar peso real se existir log para esse dia
        if d in log_by_day:
            entry["real"] = log_by_day[d]
        elif d == 0:
            # No dia 0 (Hoje), o peso real é o peso atual do perfil
            entry["real"] = round(current_weight, 1)

        projection_data.append(entry)

    return json.dumps(projection_data)
