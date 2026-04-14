"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { fetchApi } from "@/lib/api";
import styles from "./onboarding.module.css";

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [profile, setProfile] = useState({
    age: 25,
    gender: "M",
    weight: 70,
    target_weight: 65,
    height: 175,
    activity_level: "Leve",
    workout_days: 3,
    workout_duration: 60,
    workout_intensity: "Moderada",
    goals: "Emagrecimento",
    meals_per_day: 4,
    project_duration_months: 3,
    first_meal_time: "08:00"
  });

  const [preferences, setPreferences] = useState({
    restrictions: "",
    allergies: "",
    excluded_foods: "",
    preferred_foods: "",
    medical_conditions: ""
  });

  useEffect(() => {
    const loadExistingData = async () => {
      const token = localStorage.getItem("token");
      if (!token) return;
      const headers = { Authorization: `Bearer ${token}` };
      
      try {
        const existingProfile = await fetchApi("/profile", { headers });
        if (Object.keys(existingProfile).length > 0) {
          setProfile(prev => ({ ...prev, ...existingProfile }));
        }

        const existingPrefs = await fetchApi("/preferences", { headers });
        if (Object.keys(existingPrefs).length > 0) {
          setPreferences({
            restrictions: existingPrefs.restrictions?.join(", ") || "",
            allergies: existingPrefs.allergies?.join(", ") || "",
            excluded_foods: existingPrefs.excluded_foods || "",
            preferred_foods: existingPrefs.preferred_foods || "",
            medical_conditions: existingPrefs.medical_conditions || ""
          });
        }
      } catch (err) {}
    };
    loadExistingData();
  }, []);

  const nextStep = () => setStep((s) => Math.min(s + 1, 3));
  const prevStep = () => setStep((s) => Math.max(s - 1, 1));

  const handleProfileChange = (e: any) => {
    setProfile({ ...profile, [e.target.name]: e.target.value });
  };
  
  const handlePrefsChange = (e: any) => {
    setPreferences({ ...preferences, [e.target.name]: e.target.value });
  };

  const submitData = async () => {
    setLoading(true);
    setError("");
    const token = localStorage.getItem("token");
    const headers = { Authorization: `Bearer ${token}` };

    try {
      // 1. Save Health Profile
      await fetchApi("/profile", {
        method: "POST",
        headers,
        body: JSON.stringify({
          ...profile,
          age: Number(profile.age),
          weight: Number(profile.weight),
          target_weight: Number(profile.target_weight),
          height: Number(profile.height),
          workout_days: Number(profile.workout_days),
          workout_duration: Number(profile.workout_duration),
          meals_per_day: Number(profile.meals_per_day),
          project_duration_months: Number(profile.project_duration_months),
          first_meal_time: profile.first_meal_time
        })
      });

      // 2. Save Dietary Preferences
      const prefsPayload = {
        restrictions: preferences.restrictions.split(",").map(i => i.trim()).filter(i => i),
        allergies: preferences.allergies.split(",").map(i => i.trim()).filter(i => i),
        excluded_foods: preferences.excluded_foods,
        preferred_foods: preferences.preferred_foods,
        medical_conditions: preferences.medical_conditions
      };
      
      await fetchApi("/preferences", {
        method: "POST",
        headers,
        body: JSON.stringify(prefsPayload)
      });

      // Gerar Plano Nutricional
      await fetchApi("/generate-plan", {
        method: "POST",
        headers
      });

      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={`glass-card ${styles.wizardCard}`}>
        <h1 className="text-center mb-2 text-2xl font-bold">Configure seu Perfil</h1>
        
        <div className={styles.stepIndicator}>
          <div className={`${styles.step} ${step >= 1 ? styles.stepActive : ""}`}>1. Físico</div>
          <div className={`${styles.step} ${step >= 2 ? styles.stepActive : ""}`}>2. Objetivo</div>
          <div className={`${styles.step} ${step >= 3 ? styles.stepActive : ""}`}>3. Restrições</div>
        </div>

        {error && <div className="text-center mb-4 text-red-500">{error}</div>}

        {step === 1 && (
          <div className="fade-in">
            <div className={styles.rowGrid}>
              <div className="input-group">
                <label className="input-label">Idade</label>
                <input type="number" className="input-field" name="age" value={profile.age} onChange={handleProfileChange} />
              </div>
              <div className="input-group">
                <label className="input-label">Sexo</label>
                <select className="input-field" name="gender" value={profile.gender} onChange={handleProfileChange}>
                  <option value="M">Masculino</option>
                  <option value="F">Feminino</option>
                </select>
              </div>
            </div>
            <div className={styles.rowGrid}>
              <div className="input-group">
                <label className="input-label">Peso (kg)</label>
                <input type="number" className="input-field" name="weight" value={profile.weight} onChange={handleProfileChange} />
              </div>
              <div className="input-group">
                <label className="input-label">Altura (cm)</label>
                <input type="number" className="input-field" name="height" value={profile.height} onChange={handleProfileChange} />
              </div>
            </div>
            <div className={styles.rowGrid}>
              <div className="input-group">
                <label className="input-label">Meta de Peso Desejada (kg)</label>
                <input type="number" className="input-field" name="target_weight" value={profile.target_weight} onChange={handleProfileChange} />
              </div>
              <div className="input-group">
                <label className="input-label">Nível de Atividade (Se o treino mudou, altere aqui)</label>
                <select className="input-field" name="activity_level" value={profile.activity_level} onChange={handleProfileChange}>
                  <option value="Sedentário">Sedentário (Sem exercício)</option>
                  <option value="Leve">Leve (1-2x semana / Diminuí o treino)</option>
                  <option value="Moderado">Moderado (3-5x semana / Treino constante)</option>
                  <option value="Intenso">Intenso (6-7x semana / Aumentei o treino)</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="fade-in">
            <div className="input-group">
              <label className="input-label">Qual o seu objetivo principal?</label>
              <div className={styles.radioGroup}>
                <label className={styles.radioLabel}>
                  <input type="radio" name="goals" value="Emagrecimento" checked={profile.goals === "Emagrecimento"} onChange={handleProfileChange} />
                  Emagrecimento (Déficit Calórico)
                </label>
                <label className={styles.radioLabel}>
                  <input type="radio" name="goals" value="Hipertrofia" checked={profile.goals === "Hipertrofia"} onChange={handleProfileChange} />
                  Ganho de Massa Muscular (Superávit Calórico)
                </label>
                <label className={styles.radioLabel}>
                  <input type="radio" name="goals" value="Manutenção" checked={profile.goals === "Manutenção"} onChange={handleProfileChange} />
                  Manutenção de Peso Saudável
                </label>
              </div>
            </div>
            
            <div className={styles.rowGrid}>
              <div className="input-group">
                <label className="input-label">Treinos por semana (Dias)</label>
                <input type="number" className="input-field" name="workout_days" value={profile.workout_days} onChange={handleProfileChange} />
              </div>
              <div className="input-group">
                <label className="input-label">Refeições por dia (1-6)</label>
                <input type="number" className="input-field" name="meals_per_day" min="1" max="6" value={profile.meals_per_day} onChange={handleProfileChange} />
              </div>
            </div>
            <div className={styles.rowGrid}>
              <div className="input-group">
                <label className="input-label">Duração média do treino (Minutos)</label>
                <input type="number" className="input-field" name="workout_duration" value={profile.workout_duration} onChange={handleProfileChange} />
              </div>
              <div className="input-group">
                <label className="input-label">Duração do Plano (Meses)</label>
                <select className="input-field" name="project_duration_months" value={profile.project_duration_months} onChange={handleProfileChange}>
                  {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map(m => (
                    <option key={m} value={m}>{m} {m === 1 ? 'mês' : 'meses'}</option>
                  ))}
                </select>
              </div>
            </div>
            <div className={styles.rowGrid}>
              <div className="input-group">
                <label className="input-label">Horário da 1ª Refeição</label>
                <input type="time" className="input-field" name="first_meal_time" value={profile.first_meal_time} onChange={handleProfileChange} />
              </div>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="fade-in">
            <div className="input-group">
              <label className="input-label">Condições de Saúde / Doenças Crônicas (ex: Diabetes, Hipertensão)</label>
              <input type="text" className="input-field" name="medical_conditions" value={preferences.medical_conditions} onChange={handlePrefsChange} placeholder="Nenhuma" />
            </div>
            <div className="input-group">
              <label className="input-label">Restrições (Separadas por vírgula)</label>
              <input type="text" className="input-field" name="restrictions" value={preferences.restrictions} onChange={handlePrefsChange} placeholder="Vegetariano, Sem Lactose, etc." />
            </div>
            <div className={styles.rowGrid}>
              <div className="input-group">
                <label className="input-label">Alimentos Preferidos</label>
                <input type="text" className="input-field" name="preferred_foods" value={preferences.preferred_foods} onChange={handlePrefsChange} placeholder="Ovos, Frango, Maçã..." />
              </div>
              <div className="input-group">
                <label className="input-label">Enjoado de algum alimento? (Não quer consumir)</label>
                <input type="text" className="input-field" name="excluded_foods" value={preferences.excluded_foods} onChange={handlePrefsChange} placeholder="Peixe, Batata Doce, ou algo que enjoou..." />
              </div>
            </div>
          </div>
        )}

        <div className={styles.buttonGroup}>
          <button type="button" className={`btn ${styles.btnOutline}`} onClick={prevStep} style={{ visibility: step === 1 ? 'hidden' : 'visible' }}>
            Voltar
          </button>
          
          {step < 3 ? (
            <button type="button" className="btn btn-primary" onClick={nextStep}>
              Próximo
            </button>
          ) : (
            <button type="button" className="btn btn-primary" onClick={submitData} disabled={loading}>
              {loading ? "Gerando..." : "Finalizar e Gerar Plano"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
