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
