from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
import json
import os
import re

from database import engine, get_db, Base
from models import User, HealthProfile, NutritionalPlan, WeightLog, DietaryPreferences
from schemas import UserCreate, UserLogin, HealthProfileCreate, WeightLogCreate, WeightLogResponse, DietaryPreferencesCreate
from engine import (
    calculate_tmb,
    calculate_tdee,
    get_bmi_classification,
    generate_nutritional_plan,
    generate_weight_projection,
    calculate_water_recommendation
)

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
    db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).delete()
    db_profile = HealthProfile(**profile.dict(), user_id=current_user.id)
    db.add(db_profile)
    db.commit()
    return {"message": "Profile saved"}

@app.get("/profile")
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).first()
    return profile or {}

@app.post("/preferences")
def create_preferences(prefs: DietaryPreferencesCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(DietaryPreferences).filter(DietaryPreferences.user_id == current_user.id).delete()
    db_prefs = DietaryPreferences(**prefs.dict(), user_id=current_user.id)
    db.add(db_prefs)
    db.commit()
    return {"message": "Preferences saved"}

@app.get("/preferences")
def get_preferences(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    prefs = db.query(DietaryPreferences).filter(DietaryPreferences.user_id == current_user.id).first()
    return prefs or {}

@app.post("/generate-plan")
def generate_plan(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Health profile missing")

    db.query(NutritionalPlan).filter(NutritionalPlan.user_id == current_user.id).delete()

    tmb = calculate_tmb(profile.gender, profile.weight, profile.height, profile.age)
    tdee = calculate_tdee(tmb, profile.activity_level)
    bmi = round(profile.weight / ((profile.height / 100) ** 2), 1)
    bmi_class = get_bmi_classification(bmi, profile.age)
    water = calculate_water_recommendation(profile.weight)

    plan_data = generate_nutritional_plan(
        profile.goals,
        tdee,
        weight=profile.weight,
        meals_per_day=profile.meals_per_day or 4,
        first_meal_time=profile.first_meal_time or "07:00"
    )
    duration_weeks = profile.project_duration_months * 4
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
            tmb = calculate_tmb(profile.gender, profile.weight, profile.height, profile.age)
            tdee = calculate_tdee(tmb, profile.activity_level)
            bmi = round(profile.weight / ((profile.height / 100) ** 2), 1)
            bmi_class = get_bmi_classification(bmi, profile.age)
            water = calculate_water_recommendation(profile.weight)

            duration_weeks = (profile.project_duration_months or 12) * 4
            new_projection = generate_weight_projection(profile.weight, profile.goals, duration_weeks)

            plan.tmb = tmb
            plan.tdee = tdee
            plan.imc = bmi
            plan.imc_classification = bmi_class
            plan.water_recommendation = water
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
