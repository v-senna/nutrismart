from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
import bcrypt
import jwt
from datetime import datetime, timedelta

import models, schemas, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="NutriSmart API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "my_super_secret_key_for_nutrismart_app_dev_only"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user

@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_cpf = db.query(models.User).filter(models.User.cpf == user.cpf).first()
    if db_cpf:
        raise HTTPException(status_code=400, detail="CPF already registered")

    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        name=user.name,
        email=user.email,
        cpf=user.cpf,
        phone=user.phone,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(db_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me")
def get_me(current_user: models.User = Depends(get_current_user)):
    """Retorna apenas o nome do usuário autenticado — sem dados sensíveis."""
    return {"name": current_user.name}

@app.get("/profile")
def get_profile(current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    profile = db.query(models.HealthProfile).filter(models.HealthProfile.user_id == current_user.id).first()
    return profile or {}

@app.post("/profile", response_model=schemas.HealthProfileCreate)
def create_or_update_profile(profile: schemas.HealthProfileCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    db_profile = db.query(models.HealthProfile).filter(models.HealthProfile.user_id == current_user.id).first()
    if db_profile:
        for key, value in profile.model_dump().items():
            setattr(db_profile, key, value)
    else:
        db_profile = models.HealthProfile(**profile.model_dump(), user_id=current_user.id)
        db.add(db_profile)
    db.commit()
    return profile

@app.get("/preferences")
def get_preferences(current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    prefs = db.query(models.DietaryPreferences).filter(models.DietaryPreferences.user_id == current_user.id).first()
    return prefs

@app.post("/preferences", response_model=schemas.DietaryPreferencesCreate)
def create_or_update_preferences(prefs: schemas.DietaryPreferencesCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    db_prefs = db.query(models.DietaryPreferences).filter(models.DietaryPreferences.user_id == current_user.id).first()
    if db_prefs:
        for key, value in prefs.model_dump().items():
            setattr(db_prefs, key, value)
    else:
        db_prefs = models.DietaryPreferences(**prefs.model_dump(), user_id=current_user.id)
        db.add(db_prefs)
    db.commit()
    return prefs

from engine import calculate_plan, recalculate_projection_with_logs

@app.post("/generate-plan", response_model=schemas.NutritionalPlanResponse)
def generate_plan(current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    profile = db.query(models.HealthProfile).filter(models.HealthProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Health profile missing")
        
    plan_data = calculate_plan(profile)
    
    db_plan = db.query(models.NutritionalPlan).filter(models.NutritionalPlan.user_id == current_user.id).first()
    if db_plan:
        for key, value in plan_data.items():
            setattr(db_plan, key, value)
    else:
        db_plan = models.NutritionalPlan(**plan_data, user_id=current_user.id)
        db.add(db_plan)
        
    db.commit()
    db.refresh(db_plan)
    return db_plan

@app.get("/my-plan", response_model=schemas.NutritionalPlanResponse)
def get_my_plan(current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    plan = db.query(models.NutritionalPlan).filter(models.NutritionalPlan.user_id == current_user.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

@app.post("/weight-log", response_model=schemas.WeightLogResponse)
def add_weight_log(
    log_data: schemas.WeightLogCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    profile = db.query(models.HealthProfile).filter(models.HealthProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Health profile missing")

    new_log = models.WeightLog(
        user_id=current_user.id,
        weight=log_data.weight,
        note=log_data.note
    )
    db.add(new_log)
    
    # Atualizar o peso atual no perfil de saúde para que futuras projeções partam daqui
    profile.weight = log_data.weight
    db.commit()

    # Recalcular métricas do plano (TMB, macros, etc) com o novo peso
    plan_data = calculate_plan(profile)
    
    # Recalcular projeção com todos os logs injetados
    all_logs = db.query(models.WeightLog).filter(models.WeightLog.user_id == current_user.id).order_by(models.WeightLog.logged_at).all()
    new_projection = recalculate_projection_with_logs(profile, all_logs)
    
    # Atualizar o plano existente
    db_plan = db.query(models.NutritionalPlan).filter(models.NutritionalPlan.user_id == current_user.id).first()
    if db_plan:
        # Atualizar métricas nutricionais
        db_plan.tmb = plan_data["tmb"]
        db_plan.tdee = plan_data["tdee"]
        db_plan.imc = plan_data["imc"]
        db_plan.target_calories = plan_data["target_calories"]
        db_plan.target_protein = plan_data["target_protein"]
        db_plan.target_carbs = plan_data["target_carbs"]
        db_plan.target_fats = plan_data["target_fats"]
        db_plan.water_recommendation = plan_data["water_recommendation"]
        db_plan.meals_json = plan_data["meals_json"]
        # Atualizar a projeção
        db_plan.projection_data = new_projection
        db.commit()

    logs_out = [{"id": l.id, "weight": l.weight, "logged_at": l.logged_at.isoformat(), "note": l.note} for l in all_logs]
    return {"message": "Peso registrado com sucesso!", "new_projection": new_projection, "logs": logs_out}

@app.get("/weight-logs")
def get_weight_logs(current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    logs = db.query(models.WeightLog).filter(models.WeightLog.user_id == current_user.id).order_by(models.WeightLog.logged_at.desc()).all()
    return [{"id": l.id, "weight": l.weight, "logged_at": l.logged_at.isoformat(), "note": l.note} for l in logs]

