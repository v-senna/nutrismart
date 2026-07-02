from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    cpf: str
    email: EmailStr
    phone: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str = "paciente"

class HealthProfileCreate(BaseModel):
    age: int
    gender: str
    weight: float
    height: float
    target_weight: float
    activity_level: str
    workout_days: int
    workout_duration: int
    workout_intensity: str
    goals: str
    meals_per_day: int
    project_duration_months: int = 12
    first_meal_time: str = "08:00"
    meal_times: Optional[List[str]] = None
    imported_calories: Optional[float] = None
    imported_protein: Optional[float] = None
    imported_carbs: Optional[float] = None
    imported_fats: Optional[float] = None
    imported_meals: Optional[str] = None
    imported_tips: Optional[str] = None
    is_custom_diet: Optional[bool] = False

class HealthProfileResponse(BaseModel):
    id: int
    age: int
    weight: float
    height: float
    gender: str
    goals: str
    meals_per_day: int
    first_meal_time: str
    meal_times: Optional[List[str]] = None
    imported_calories: Optional[float] = None
    imported_protein: Optional[float] = None
    imported_carbs: Optional[float] = None
    imported_fats: Optional[float] = None
    imported_meals: Optional[str] = None
    imported_tips: Optional[str] = None
    is_custom_diet: Optional[bool] = False

    class Config:
        from_attributes = True

class DietaryPreferencesCreate(BaseModel):
    restrictions: List[str]
    allergies: List[str]
    excluded_foods: str
    preferred_foods: str
    medical_conditions: str

class NutritionalPlanResponse(BaseModel):
    id: int
    tmb: float
    tdee: float
    imc: float
    target_calories: float
    target_protein: float
    target_carbs: float
    target_fats: float
    water_recommendation: float
    recommendations_text: str
    projection_data: Optional[str] = None
    meals_json: Optional[str] = None
    imc_classification: Optional[str] = None
    
    class Config:
        from_attributes = True

class WeightLogCreate(BaseModel):
    weight: float
    note: Optional[str] = None

class WeightLogItem(BaseModel):
    id: int
    weight: float
    logged_at: datetime
    note: Optional[str] = None

    class Config:
        from_attributes = True

class WeightLogResponse(BaseModel):
    message: str
    new_projection: Optional[str] = None
    logs: Optional[List[Any]] = None

class MealLogCreate(BaseModel):
    meal_name: str
    scheduled_time: str
    status: str
    evaluation: Optional[str] = None

class MealLogResponse(MealLogCreate):
    id: int
    logged_at: datetime

    class Config:
        from_attributes = True

class SearchSupermarketsRequest(BaseModel):
    region: str

class QuoteShoppingListRequest(BaseModel):
    items: List[str]
    supermarket: str
    region: str

# --- Schemas do Sistema de Nutricionistas ---

class NutritionistRegister(BaseModel):
    """Schema para registro de nutricionista (usado pelo admin)."""
    name: str
    cpf: str
    email: EmailStr
    phone: str
    password: str
    crn: str
    specialty: Optional[str] = None
    bio: Optional[str] = None

class NutritionistProfileCreate(BaseModel):
    crn: str
    specialty: Optional[str] = None
    bio: Optional[str] = None

class NutritionistProfileResponse(BaseModel):
    id: int
    user_id: int
    crn: str
    specialty: Optional[str] = None
    bio: Optional[str] = None

    class Config:
        from_attributes = True

class NutritionistListItem(BaseModel):
    id: int
    name: str
    email: str
    crn: Optional[str] = None
    specialty: Optional[str] = None

class NutritionistPatientAssign(BaseModel):
    nutritionist_id: int
    patient_id: int
    notes: Optional[str] = None

class NutritionistPatientResponse(BaseModel):
    id: int
    nutritionist_id: int
    patient_id: int
    assigned_at: Optional[datetime] = None
    status: str = "ativo"
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class PatientSummary(BaseModel):
    id: int
    name: str
    email: str
    cpf: str
    assigned_at: Optional[datetime] = None
    status: str = "ativo"

class PatientDetailResponse(BaseModel):
    id: int
    name: str
    email: str
    cpf: str
    profile: Optional[Dict[str, Any]] = None
    plan: Optional[Dict[str, Any]] = None
    weight_logs: List[Dict[str, Any]] = []
    meal_logs: List[Dict[str, Any]] = []

class PatientEvaluationCreate(BaseModel):
    weight: float
    body_fat_pct: Optional[float] = None
    muscle_mass: Optional[float] = None
    waist_cm: Optional[float] = None
    hip_cm: Optional[float] = None
    arm_cm: Optional[float] = None
    notes: Optional[str] = None

class PatientEvaluationResponse(BaseModel):
    id: int
    nutritionist_id: int
    patient_id: int
    weight: float
    body_fat_pct: Optional[float] = None
    muscle_mass: Optional[float] = None
    waist_cm: Optional[float] = None
    hip_cm: Optional[float] = None
    arm_cm: Optional[float] = None
    notes: Optional[str] = None
    evaluated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DietPrescriptionCreate(BaseModel):
    title: str
    target_calories: float
    target_protein: float
    target_carbs: float
    target_fats: float
    meals_json: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool = True

class DietPrescriptionResponse(BaseModel):
    id: int
    nutritionist_id: int
    patient_id: int
    title: str
    target_calories: float
    target_protein: float
    target_carbs: float
    target_fats: float
    meals_json: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    is_active: bool = True

    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_patients: int = 0
    active_patients: int = 0
    evaluations_this_month: int = 0
    diets_active: int = 0
