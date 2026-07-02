from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text, JSON, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    cpf = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default='paciente')  # paciente, nutricionista, admin
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    health_profile = relationship("HealthProfile", back_populates="user", uselist=False)
    preferences = relationship("DietaryPreferences", back_populates="user", uselist=False)
    plans = relationship("NutritionalPlan", back_populates="user")
    weight_logs = relationship("WeightLog", back_populates="user", order_by="WeightLog.logged_at")
    meal_logs = relationship("MealLog", back_populates="user", order_by="MealLog.logged_at")


class HealthProfile(Base):
    __tablename__ = "health_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    age = Column(Integer)
    gender = Column(String)  # M, F, etc
    weight = Column(Float)   # em kg
    height = Column(Float)   # em cm
    target_weight = Column(Float, nullable=True) # em kg
    activity_level = Column(String) # sedentario, leve, moderado, intenso
    workout_days = Column(Integer)
    workout_duration = Column(Integer) # em minutos
    workout_intensity = Column(String)
    goals = Column(String) # emagrecimento, hipertrofia, manutencao
    meals_per_day = Column(Integer, default=4)
    project_duration_months = Column(Integer, default=12)
    first_meal_time = Column(String, default="08:00")
    meal_times = Column(JSON, nullable=True) # Ex: ["08:00", "12:00", "16:00", "20:00"]
    imported_calories = Column(Float, nullable=True)
    imported_protein = Column(Float, nullable=True)
    imported_carbs = Column(Float, nullable=True)
    imported_fats = Column(Float, nullable=True)
    imported_meals = Column(Text, nullable=True) # JSON com os textos das refeições importadas
    imported_tips = Column(Text, nullable=True) # JSON com as dicas importadas
    is_custom_diet = Column(Boolean, default=False)

    user = relationship("User", back_populates="health_profile")


class DietaryPreferences(Base):
    __tablename__ = "dietary_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    restrictions = Column(JSON) # e.g. ["lactose", "gluten"]
    allergies = Column(JSON)
    excluded_foods = Column(Text)
    preferred_foods = Column(Text)
    medical_conditions = Column(Text)

    user = relationship("User", back_populates="preferences")


class NutritionalPlan(Base):
    __tablename__ = "nutritional_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    tmb = Column(Float)
    tdee = Column(Float)
    imc = Column(Float)
    target_calories = Column(Float)
    target_protein = Column(Float) # gramas
    target_carbs = Column(Float)   # gramas
    target_fats = Column(Float)    # gramas
    water_recommendation = Column(Float) # mL
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    recommendations_text = Column(Text) # Dicas e habitos para o usuario
    projection_data = Column(Text, nullable=True) # Dados do grafico em JSON string
    meals_json = Column(Text, nullable=True) # Dados estruturados das refeições
    imc_classification = Column(String, nullable=True) # Classificação HAS/OMS

    user = relationship("User", back_populates="plans")


class WeightLog(Base):
    __tablename__ = "weight_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    weight = Column(Float, nullable=False)  # kg
    logged_at = Column(DateTime(timezone=True), server_default=func.now())
    note = Column(String, nullable=True)

    user = relationship("User", back_populates="weight_logs")


class MealLog(Base):
    __tablename__ = "meal_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    meal_name = Column(String, nullable=False) # e.g. Cafe da manha
    scheduled_time = Column(String, nullable=False) # e.g. 08:00
    status = Column(String, nullable=False) # 'eaten' or 'skipped'
    evaluation = Column(String, nullable=True) # 'good', 'regular', 'bad'
    logged_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="meal_logs")


# --- Modelos do Sistema de Nutricionistas ---

class NutritionistProfile(Base):
    __tablename__ = 'nutritionist_profiles'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    crn = Column(String, nullable=False)  # Número do CRN
    specialty = Column(String, nullable=True)  # Ex: Esportiva, Clínica
    bio = Column(Text, nullable=True)

    user = relationship('User', backref='nutritionist_profile')


class NutritionistPatient(Base):
    __tablename__ = 'nutritionist_patients'

    id = Column(Integer, primary_key=True, index=True)
    nutritionist_id = Column(Integer, ForeignKey('users.id'))
    patient_id = Column(Integer, ForeignKey('users.id'))
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default='ativo')  # ativo, inativo
    notes = Column(Text, nullable=True)

    nutritionist = relationship('User', foreign_keys=[nutritionist_id], backref='my_patients')
    patient = relationship('User', foreign_keys=[patient_id], backref='my_nutritionists')


class PatientEvaluation(Base):
    __tablename__ = 'patient_evaluations'

    id = Column(Integer, primary_key=True, index=True)
    nutritionist_id = Column(Integer, ForeignKey('users.id'))
    patient_id = Column(Integer, ForeignKey('users.id'))
    weight = Column(Float)
    body_fat_pct = Column(Float, nullable=True)
    muscle_mass = Column(Float, nullable=True)
    waist_cm = Column(Float, nullable=True)
    hip_cm = Column(Float, nullable=True)
    arm_cm = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    evaluated_at = Column(DateTime(timezone=True), server_default=func.now())

    nutritionist = relationship('User', foreign_keys=[nutritionist_id])
    patient = relationship('User', foreign_keys=[patient_id])


class DietPrescription(Base):
    __tablename__ = 'diet_prescriptions'

    id = Column(Integer, primary_key=True, index=True)
    nutritionist_id = Column(Integer, ForeignKey('users.id'))
    patient_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String, nullable=False)
    target_calories = Column(Float)
    target_protein = Column(Float)
    target_carbs = Column(Float)
    target_fats = Column(Float)
    meals_json = Column(Text)  # JSON com detalhes das refeições
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    nutritionist = relationship('User', foreign_keys=[nutritionist_id])
    patient = relationship('User', foreign_keys=[patient_id])
