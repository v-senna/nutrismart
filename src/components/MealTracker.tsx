import React, { useState, useEffect } from 'react';
import { fetchApi } from '@/lib/api';
import { CheckCircle2, XCircle, Clock, Check, X } from 'lucide-react';
import styles from './MealTracker.module.css';

interface Meal {
  label: string;
  time: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  suggestion: string;
}

interface MealLog {
  id: number;
  meal_name: string;
  scheduled_time: string;
  status: string;
  evaluation?: string;
  logged_at: string;
}

export default function MealTracker({ meals, onUpdate }: { meals: Meal[], onUpdate: () => void }) {
  const [logs, setLogs] = useState<MealLog[]>([]);
  const [pendingMeal, setPendingMeal] = useState<Meal | null>(null);
  const [step, setStep] = useState<'ask' | 'evaluate'>('ask');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchLogs();
  }, [meals]);

  const fetchLogs = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) return;
      const data = await fetchApi("/meal-logs", {
        headers: { Authorization: `Bearer ${token}` }
      });
      setLogs(data || []);
      checkPendingMeals(data || [], meals);
    } catch (e) {
      console.error("Error fetching meal logs", e);
    }
  };

  const checkPendingMeals = (currentLogs: MealLog[], currentMeals: Meal[]) => {
    const now = new Date();
    const currentMinutes = now.getHours() * 60 + now.getMinutes();
    
    // Check if any meal time has passed and not logged today
    const todayStr = now.toISOString().split('T')[0];
    const todayLogs = currentLogs.filter(l => l.logged_at.startsWith(todayStr));

    let toAsk: Meal | null = null;
    for (const m of currentMeals) {
      const [h, min] = m.time.split(':').map(Number);
      const mealMinutes = h * 60 + min;
      
      // If meal time has passed (give a 10 min grace period)
      if (currentMinutes > mealMinutes + 10) {
        // Check if logged
        const hasLogged = todayLogs.some(l => l.meal_name === m.label);
        if (!hasLogged) {
          toAsk = m;
        }
      }
    }
    
    setPendingMeal(toAsk);
    setStep('ask');
  };

  const handleSkip = async () => {
    if (!pendingMeal) return;
    await submitLog('skipped');
  };

  const handleEaten = () => {
    setStep('evaluate');
  };

  const submitLog = async (status: string, evaluation?: string) => {
    if (!pendingMeal) return;
    setSubmitting(true);
    try {
      const token = localStorage.getItem("token");
      await fetchApi("/meal-log", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          meal_name: pendingMeal.label,
          scheduled_time: pendingMeal.time,
          status,
          evaluation
        }),
      });
      setPendingMeal(null);
      await fetchLogs();
      onUpdate(); // Trigger parent refresh to get updated plan if skipped
    } catch (e) {
      console.error(e);
      alert("Erro ao salvar o log.");
    } finally {
      setSubmitting(false);
    }
  };

  if (!pendingMeal && logs.length === 0) return null;

  return (
    <div className={styles.container}>
      {pendingMeal && (
        <div className={styles.modalOverlay}>
          <div className={styles.modalContent}>
            {step === 'ask' && (
              <>
                <h3 className={styles.title}>
                  <Clock className={styles.icon} />
                  Hora da verdade!
                </h3>
                <p>Você fez o seu <strong>{pendingMeal.label}</strong> das {pendingMeal.time}?</p>
                
                <div className={styles.buttons}>
                  <button className={styles.btnYes} onClick={handleEaten} disabled={submitting}>
                    <Check className={styles.btnIcon} /> Sim, eu comi!
                  </button>
                  <button className={styles.btnNo} onClick={handleSkip} disabled={submitting}>
                    <X className={styles.btnIcon} /> Não, pulei.
                  </button>
                </div>
                <p className={styles.hint}>
                  Se você pulou, recalcularermos suas próximas refeições para bater a meta de hoje!
                </p>
              </>
            )}

            {step === 'evaluate' && (
              <>
                <h3 className={styles.title}>O que achou da refeição?</h3>
                <p>Avalie como foi sua refeição para nos ajudar a melhorar seu plano no futuro.</p>
                <div className={styles.evalButtons}>
                  <button className={styles.btnEvalGood} onClick={() => submitLog('eaten', 'good')} disabled={submitting}>
                    😋 Muito Boa
                  </button>
                  <button className={styles.btnEvalRegular} onClick={() => submitLog('eaten', 'regular')} disabled={submitting}>
                    😐 Regular
                  </button>
                  <button className={styles.btnEvalBad} onClick={() => submitLog('eaten', 'bad')} disabled={submitting}>
                    🤢 Ruim
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {logs.length > 0 && (
        <div className={styles.historyContainer}>
          <h3 className={styles.historyTitle}>Histórico de Refeições</h3>
          <div className={styles.logList}>
            {logs.slice(0, 10).map(log => (
              <div key={log.id} className={styles.logItem}>
                <div className={styles.logMain}>
                  {log.status === 'eaten' ? <CheckCircle2 size={18} color="var(--primary)" /> : <XCircle size={18} color="var(--error)" />}
                  <span className={styles.logName}>{log.meal_name} ({log.scheduled_time})</span>
                </div>
                <div className={styles.logMeta}>
                  {log.status === 'eaten' && log.evaluation && (
                    <span className={styles.evalTag} data-eval={log.evaluation}>
                      {log.evaluation === 'good' ? 'Boa' : log.evaluation === 'regular' ? 'Regular' : 'Ruim'}
                    </span>
                  )}
                  <span className={styles.logDate}>{new Date(log.logged_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
