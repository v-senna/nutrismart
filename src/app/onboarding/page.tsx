"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { fetchApi } from "@/lib/api";
import { ClipboardList, Ruler, Target, Salad, ArrowLeft, ArrowRight, Rocket, CheckCircle } from "lucide-react";
import styles from "./onboarding.module.css";
import ThemeToggle from "@/components/ThemeToggle";
import ImportDietModal from "@/components/ImportDietModal";
import { FileUp } from "lucide-react";

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showImportModal, setShowImportModal] = useState(false);

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
    first_meal_time: "08:00",
    meal_times: ["08:00", "12:00", "16:00", "20:00"]
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
          setProfile(prev => ({ 
            ...prev, 
            ...existingProfile,
            meal_times: existingProfile.meal_times || prev.meal_times 
          }));
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
    const { name, value } = e.target;
    
    if (name === "meals_per_day") {
      const count = Math.min(6, Math.max(1, Number(value)));
      const newTimes = [...profile.meal_times];
      if (count > newTimes.length) {
        for (let i = newTimes.length; i < count; i++) {
          const lastTime = newTimes[newTimes.length - 1] || "08:00";
          const [h, m] = lastTime.split(":").map(Number);
          newTimes.push(`${String((h + 3) % 24).padStart(2, '0')}:${String(m).padStart(2, '0')}`);
        }
      } else {
        newTimes.splice(count);
      }
      setProfile({ ...profile, meals_per_day: count, meal_times: newTimes });
    } else {
      setProfile({ ...profile, [name]: value });
    }
  };

  const handleMealTimeChange = (index: number, value: string) => {
    const newTimes = [...profile.meal_times];
    newTimes[index] = value;
    setProfile({ ...profile, meal_times: newTimes });
    if (index === 0) {
        setProfile(prev => ({ ...prev, first_meal_time: value, meal_times: newTimes }));
    }
  };
  
  const handlePrefsChange = (e: any) => {
    setPreferences({ ...preferences, [e.target.name]: e.target.value });
  };

  const handleImportSuccess = (data: any) => {
    // Fill Profile
    const newProfile = { ...profile };
    if (data.profile.age) newProfile.age = data.profile.age;
    if (data.profile.weight) newProfile.weight = data.profile.weight;
    if (data.profile.height) newProfile.height = data.profile.height;
    if (data.profile.gender) newProfile.gender = data.profile.gender;
    if (data.profile.goals) newProfile.goals = data.profile.goals;
    
    // Fill Meal Times if detected
    if (data.meals && data.meals.length > 0) {
      newProfile.meals_per_day = data.meals.length;
      newProfile.meal_times = data.meals.map((m: any) => m.time || "08:00");
    }
    
    setProfile(newProfile);
    
    // Step 2 is more relevant after import
    setStep(2);
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
          first_meal_time: profile.meal_times[0] || profile.first_meal_time
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
        <h1 className="text-center mb-2 text-2xl font-bold flex items-center justify-center gap-2">
          <ClipboardList className="text-primary" /> Configure seu Perfil
        </h1>
        
        <div className={styles.stepIndicator}>
          <div className={`${styles.step} ${step >= 1 ? styles.stepActive : ""}`}>
            <Ruler size={18} /> 1. Físico
          </div>
          <div className={`${styles.step} ${step >= 2 ? styles.stepActive : ""}`}>
            <Target size={18} /> 2. Objetivo
          </div>
          <div className={`${styles.step} ${step >= 3 ? styles.stepActive : ""}`}>
            <Salad size={18} /> 3. Restrições
          </div>
        </div>

        <div className="flex justify-end mb-4">
          <button 
            className="btn btn-primary flex items-center gap-2 text-xs py-2"
            onClick={() => setShowImportModal(true)}
            style={{ background: 'var(--secondary)', color: 'white' }}
          >
            <FileUp size={14} /> Importar de PDF/Excel
          </button>
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
                <label className="input-label">Nível de Atividade</label>
                <select className="input-field" name="activity_level" value={profile.activity_level} onChange={handleProfileChange}>
                  <option value="Sedentário">Sedentário (Sem exercício)</option>
                  <option value="Leve">Leve (1-2x semana)</option>
                  <option value="Moderado">Moderado (3-5x semana)</option>
                  <option value="Intenso">Intenso (6-7x semana)</option>
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
                  Emagrecimento
                </label>
                <label className={styles.radioLabel}>
                  <input type="radio" name="goals" value="Ganho de Massa Muscular" checked={profile.goals === "Ganho de Massa Muscular"} onChange={handleProfileChange} />
                  Ganho de Massa
                </label>
                <label className={styles.radioLabel}>
                  <input type="radio" name="goals" value="Manutenção" checked={profile.goals === "Manutenção"} onChange={handleProfileChange} />
                  Manutenção
                </label>
              </div>
            </div>
            
            <div className={styles.rowGrid}>
              <div className="input-group">
                <label className="input-label">Treinos por semana</label>
                <input type="number" className="input-field" name="workout_days" value={profile.workout_days} onChange={handleProfileChange} />
              </div>
              <div className="input-group">
                <label className="input-label">Refeições por dia (1-6)</label>
                <input type="number" className="input-field" name="meals_per_day" min="1" max="6" value={profile.meals_per_day} onChange={handleProfileChange} />
              </div>
            </div>

            <div className="input-group">
              <label className="input-label mb-2 block font-semibold text-primary">Horários das Refeições</label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3 bg-secondary/10 p-4 rounded-xl border border-primary/20">
                {profile.meal_times.map((time, idx) => (
                  <div key={idx} className="flex flex-col gap-1">
                    <label className="text-xs font-medium opacity-70">Refeição {idx + 1}</label>
                    <input 
                      type="time" 
                      className="input-field text-center" 
                      value={time} 
                      onChange={(e) => handleMealTimeChange(idx, e.target.value)} 
                    />
                  </div>
                ))}
              </div>
            </div>

            <div className={styles.rowGrid}>
              <div className="input-group">
                <label className="input-label">Duração do treino (Min)</label>
                <input type="number" className="input-field" name="workout_duration" value={profile.workout_duration} onChange={handleProfileChange} />
              </div>
              <div className="input-group">
                <label className="input-label">Duração do Plano (Meses)</label>
                <select className="input-field" name="project_duration_months" value={profile.project_duration_months} onChange={handleProfileChange}>
                  {[1, 2, 3, 4, 5, 6, 12].map(m => (
                    <option key={m} value={m}>{m} {m === 1 ? 'mês' : 'meses'}</option>
                  ))}
                </select>
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
          <button type="button" className={`btn ${styles.btnOutline} flex items-center gap-2`} onClick={prevStep} style={{ visibility: step === 1 ? 'hidden' : 'visible' }}>
            <ArrowLeft size={18} /> Voltar
          </button>
          
          {step < 3 ? (
            <button type="button" className="btn btn-primary flex items-center gap-2" onClick={nextStep}>
              Próximo <ArrowRight size={18} />
            </button>
          ) : (
            <button type="button" className="btn btn-primary flex items-center gap-2" onClick={submitData} disabled={loading}>
              {loading ? <><Rocket className="animate-bounce" size={18} /> Gerando...</> : <><CheckCircle size={18} /> Finalizar e Gerar Plano</>}
            </button>
          )}
        </div>
      </div>
      <ThemeToggle />
      {showImportModal && (
        <ImportDietModal 
          onClose={() => setShowImportModal(false)} 
          onImportSuccess={handleImportSuccess} 
        />
      )}
    </div>
  );
}
