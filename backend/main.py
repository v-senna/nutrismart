from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
import json
import re
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

from database import engine, get_db, Base
from models import User, HealthProfile, NutritionalPlan, WeightLog, DietaryPreferences, MealLog
from schemas import (
    UserCreate, UserResponse, UserLogin,
    HealthProfileCreate, HealthProfileResponse,
    DietaryPreferencesCreate,
    WeightLogCreate, WeightLogResponse,
    MealLogCreate, MealLogResponse,
    SearchSupermarketsRequest, QuoteShoppingListRequest
)
from engine import (
    calculate_tmb,
    calculate_tdee,
    get_bmi_classification,
    generate_nutritional_plan,
    generate_weight_projection,
    calculate_water_recommendation,
    recalculate_remaining_meals_for_today
)
from ai_utils import extract_text_from_pdf, extract_text_from_excel, parse_diet_info, search_supermarkets_ai, quote_shopping_list_ai
from fastapi import UploadFile, File

# Criar tabelas se não existirem
Base.metadata.create_all(bind=engine)

app = FastAPI(title="NutriSmart API")

# Configurar CORS para o frontend (Next.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DEBUG: Capturador Global de Erros ---
import traceback
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_msg = f"Erro Crítico: {str(exc)}\n{traceback.format_exc()}"
    print(error_msg)
    return JSONResponse(
        status_code=500,
        content={"detail": error_msg}
    )

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def clean_cpf(cpf: str) -> str:
    """Remove formatação do CPF, retorna apenas dígitos."""
    return re.sub(r'\D', '', cpf)

# --- Endpoints de Autenticação ---

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Verificar e-mail duplicado
    db_user_email = db.query(User).filter(User.email == user.email).first()
    if db_user_email:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    # Verificar CPF duplicado (comparando apenas dígitos)
    cpf_clean = clean_cpf(user.cpf)
    all_users = db.query(User).all()
    for u in all_users:
        if clean_cpf(u.cpf) == cpf_clean:
            raise HTTPException(status_code=400, detail="CPF já cadastrado")

    new_user = User(
        email=user.email,
        password_hash=user.password,
        name=user.name,
        cpf=cpf_clean,  # Salvar sempre sem formatação
        phone=user.phone
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Usuário criado com sucesso", "user_id": new_user.id}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Suporte a login por CPF (apenas dígitos) ou e-mail
    username = form_data.username.strip()
    cpf_clean = re.sub(r'\D', '', username)

    user = None
    # Tentar CPF primeiro se o campo parece ser CPF (só dígitos após limpeza)
    if cpf_clean and len(cpf_clean) == 11:
        all_users = db.query(User).all()
        for u in all_users:
            if clean_cpf(u.cpf) == cpf_clean:
                user = u
                break

    # Fallback para e-mail
    if not user:
        user = db.query(User).filter(User.email == username).first()

    if not user or user.password_hash != form_data.password:
        raise HTTPException(status_code=401, detail="CPF/E-mail ou senha incorretos")

    # Token = CPF limpo do usuário para identificação
    return {"access_token": user.cpf, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Token pode ser CPF ou e-mail (compatibilidade)
    cpf_clean = re.sub(r'\D', '', token)

    user = None
    if len(cpf_clean) == 11:
        all_users = db.query(User).all()
        for u in all_users:
            if clean_cpf(u.cpf) == cpf_clean:
                user = u
                break

    # Fallback e-mail para sessões antigas
    if not user:
        user = db.query(User).filter(User.email == token).first()

    if not user:
        raise HTTPException(status_code=401, detail="Token inválido")
    return user

@app.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email, "name": current_user.name}

# --- Endpoints de Perfil e Plano ---

@app.post("/profile")
def create_profile(profile: HealthProfileCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    import traceback
    try:
        db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).delete()
        db_profile = HealthProfile(**profile.model_dump(), user_id=current_user.id)
        db.add(db_profile)
        db.commit()
        return {"message": "Profile updated successfully"}
    except Exception as e:
        db.rollback()
        error_msg = f"Erro no Profile: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/profile")
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).first()
    return profile or {}

@app.post("/preferences")
def create_preferences(prefs: DietaryPreferencesCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(DietaryPreferences).filter(DietaryPreferences.user_id == current_user.id).delete()
    db_prefs = DietaryPreferences(**prefs.model_dump(), user_id=current_user.id)
    db.add(db_prefs)
    db.commit()
    return {"message": "Preferences saved"}

@app.get("/preferences")
def get_preferences(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    prefs = db.query(DietaryPreferences).filter(DietaryPreferences.user_id == current_user.id).first()
    return prefs or {}

@app.post("/generate-plan")
def generate_plan(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    import traceback
    try:
        profile = db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).first()
        if not profile:
            raise HTTPException(status_code=400, detail="Health profile missing")

        db.query(NutritionalPlan).filter(NutritionalPlan.user_id == current_user.id).delete()

        tmb = calculate_tmb(profile.gender, profile.weight or 70, profile.height or 170, profile.age or 25)
        tdee = calculate_tdee(tmb, profile.activity_level)
        
        # Prevenção de divisão por zero ou valores nulos
        weight_val = profile.weight or 70.0
        height_val = profile.height or 170.0
        if height_val <= 0: height_val = 170.0
        
        bmi = round(weight_val / ((height_val / 100) ** 2), 1)
        bmi_class = get_bmi_classification(bmi, profile.age or 30)
        water = calculate_water_recommendation(weight_val)

        plan_data = generate_nutritional_plan(
            profile.goals,
            tdee,
            weight=profile.weight,
            meals_per_day=profile.meals_per_day or 4,
            first_meal_time=profile.first_meal_time or "07:00",
            meal_times=profile.meal_times,
            target_calories_override=profile.imported_calories,
            target_protein_override=profile.imported_protein,
            target_carbs_override=profile.imported_carbs,
            target_fats_override=profile.imported_fats,
            imported_meals_data=profile.imported_meals,
            imported_tips=profile.imported_tips,
            is_custom_diet=profile.is_custom_diet
        )
        duration_weeks = (profile.project_duration_months or 12) * 4
        projection = generate_weight_projection(profile.weight, profile.goals, duration_weeks)

        db_plan = NutritionalPlan(
            user_id=current_user.id,
            tmb=tmb,
            tdee=tdee,
            imc=bmi,
            imc_classification=bmi_class,
            water_recommendation=water,
            target_calories=plan_data["calories_target"],
            target_protein=plan_data["protein_target"],
            target_carbs=plan_data["carbs_target"],
            target_fats=plan_data["fats_target"],
            meals_json=json.dumps(plan_data["meals"]),
            recommendations_text=plan_data["recommendations"],
            projection_data=json.dumps(projection)
        )
        db.add(db_plan)
        db.commit()
        return {"message": "Plan generated successfully"}
    except Exception as e:
        db.rollback()
        error_msg = f"Erro no Generate Plan: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/import-diet")
async def import_diet(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    print(f"--- Iniciando import-diet: Arquivo={file.filename}, Usuário={current_user.email} ---")
    content = await file.read()
    print(f"--- Arquivo lido: {len(content)} bytes ---")
    filename = file.filename.lower()
    
    try:
        if filename.endswith(".pdf"):
            print("--- Extraindo texto de PDF ---")
            text = extract_text_from_pdf(content)
        elif filename.endswith((".xlsx", ".xls")):
            print("--- Extraindo texto de Excel ---")
            text = extract_text_from_excel(content)
        else:
            print(f"--- Formato não suportado: {filename} ---")
            raise HTTPException(status_code=400, detail="Formato de arquivo não suportado. Use PDF ou Excel.")
        
        if not text or len(text.strip()) == 0:
            print("--- Texto extraído está vazio ---")
            raise HTTPException(status_code=400, detail="Não foi possível extrair texto do arquivo. Verifique se o arquivo não está protegido ou corrompido.")

        print(f"--- Texto extraído ({len(text)} caracteres). Analisando... ---")
        print(f"DEBUG - Texto bruto extraído:\n{text[:1000]}...") # Logar primeiros 1000 chars
        
        # Buscar perfil do usuário para ajudar a IA a preencher quantidades vazias
        user_profile = db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).first()
        profile_dict = user_profile.__dict__ if user_profile else None
        
        extracted_data = parse_diet_info(text, user_profile=profile_dict)
        print(f"DEBUG - Dados estruturados pela IA: {json.dumps(extracted_data, indent=2, ensure_ascii=False)}")
        print("--- Análise concluída com sucesso ---")
        return extracted_data
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"--- ERRO CRÍTICO EM IMPORT-DIET: {str(e)} ---")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")

@app.get("/my-plan")
def get_plan(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plan = db.query(NutritionalPlan).filter(NutritionalPlan.user_id == current_user.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

# --- Endpoints de Registro de Peso ---

@app.post("/weight-log", response_model=WeightLogResponse)
def log_weight(log: WeightLogCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 1. Salvar o novo log
    new_log = WeightLog(
        user_id=current_user.id,
        weight=log.weight,
        note=log.note,
        logged_at=datetime.utcnow()
    )
    db.add(new_log)
    db.flush()  # Garante que o novo log tem ID antes do commit

    # 2. Atualizar o peso no perfil de saúde para manter sincronizado
    profile = db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).first()
    if profile:
        profile.weight = log.weight

        # 3. Recalcular a projeção com base no novo peso real
        plan = db.query(NutritionalPlan).filter(NutritionalPlan.user_id == current_user.id).first()
        if plan:
            tmb = calculate_tmb(profile.gender, profile.weight or 70, profile.height or 170, profile.age or 25)
            tdee = calculate_tdee(tmb, profile.activity_level)
            
            # Prevenção de divisão por zero ou valores nulos
            weight_val = profile.weight or 70.0
            height_val = profile.height or 170.0
            if height_val <= 0: height_val = 170.0
            
            bmi = round(weight_val / ((height_val / 100) ** 2), 1)
            bmi_class = get_bmi_classification(bmi, profile.age or 30)
            water = calculate_water_recommendation(weight_val)

            duration_weeks = (profile.project_duration_months or 12) * 4
            new_projection = generate_weight_projection(profile.weight, profile.goals, duration_weeks)

            # Recalcular também as macros e as refeições
            plan_data = generate_nutritional_plan(
                profile.goals,
                tdee,
                weight=profile.weight,
                meals_per_day=profile.meals_per_day or 4,
                first_meal_time=profile.first_meal_time or "07:00",
                meal_times=profile.meal_times,
                target_calories_override=profile.imported_calories,
                target_protein_override=profile.imported_protein,
                target_carbs_override=profile.imported_carbs,
                target_fats_override=profile.imported_fats,
                imported_meals_data=profile.imported_meals,
                imported_tips=profile.imported_tips,
                is_custom_diet=profile.is_custom_diet
            )

            plan.tmb = tmb
            plan.tdee = tdee
            plan.imc = bmi
            plan.imc_classification = bmi_class
            plan.water_recommendation = water
            plan.target_calories = plan_data["calories_target"]
            plan.target_protein = plan_data["protein_target"]
            plan.target_carbs = plan_data["carbs_target"]
            plan.target_fats = plan_data["fats_target"]
            plan.meals_json = json.dumps(plan_data["meals"])
            plan.projection_data = json.dumps(new_projection)

    db.commit()

    # Buscar logs atualizados após o commit
    all_logs = db.query(WeightLog).filter(
        WeightLog.user_id == current_user.id
    ).order_by(WeightLog.logged_at.desc()).all()

    # Serializar logs manualmente para evitar erros de serialização
    logs_serialized = [
        {
            "id": l.id,
            "weight": l.weight,
            "note": l.note,
            "logged_at": l.logged_at.isoformat() if l.logged_at else None
        }
        for l in all_logs
    ]

    plan_after = db.query(NutritionalPlan).filter(NutritionalPlan.user_id == current_user.id).first()
    new_proj = plan_after.projection_data if plan_after else None

    return {
        "message": "Peso registrado e projeção atualizada!",
        "logs": logs_serialized,
        "new_projection": new_proj
    }

@app.get("/weight-logs")
def get_weight_logs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logs = db.query(WeightLog).filter(WeightLog.user_id == current_user.id).order_by(WeightLog.logged_at.desc()).all()
    return [
        {
            "id": l.id,
            "weight": l.weight,
            "note": l.note,
            "logged_at": l.logged_at.isoformat() if l.logged_at else None
        }
        for l in logs
    ]

# --- Endpoints de Refeições ---

@app.post("/meal-log", response_model=MealLogResponse)
def log_meal(log: MealLogCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 1. Salvar o log
    new_log = MealLog(
        user_id=current_user.id,
        meal_name=log.meal_name,
        scheduled_time=log.scheduled_time,
        status=log.status,
        evaluation=log.evaluation,
        logged_at=datetime.utcnow()
    )
    db.add(new_log)
    db.flush()

    # 2. Se pulou, recalcular refeições restantes do dia
    if log.status == "skipped":
        plan = db.query(NutritionalPlan).filter(NutritionalPlan.user_id == current_user.id).first()
        if plan and plan.meals_json:
            meals_list = json.loads(plan.meals_json)
            updated_meals = recalculate_remaining_meals_for_today(meals_list, log.meal_name)
            plan.meals_json = json.dumps(updated_meals)
            
    db.commit()
    db.refresh(new_log)
    
    return new_log

@app.get("/meal-logs", response_model=List[MealLogResponse])
def get_meal_logs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logs = db.query(MealLog).filter(MealLog.user_id == current_user.id).order_by(MealLog.logged_at.desc()).all()
    return logs

# --- Endpoints de Supermercado e Lista de Compras ---
@app.post("/search-supermarkets")
def search_supermarkets(req: SearchSupermarketsRequest, current_user: User = Depends(get_current_user)):
    results = search_supermarkets_ai(req.region)
    return results

@app.post("/quote-shopping-list")
def quote_shopping_list(req: QuoteShoppingListRequest, current_user: User = Depends(get_current_user)):
    results = quote_shopping_list_ai(req.items, req.supermarket, req.region)
    return results
