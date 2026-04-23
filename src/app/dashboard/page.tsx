"use client";

import { useState, useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import { fetchApi } from "@/lib/api";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { 
  FileText, 
  Settings, 
  LogOut, 
  TrendingUp, 
  BarChart4, 
  Dna, 
  Utensils, 
  RefreshCw, 
  AlertTriangle, 
  Lightbulb,
  ArrowLeft,
  ArrowRight,
  Hand,
  ChevronDown,
  ChevronUp,
  Bell,
  BellOff,
  Droplet
} from "lucide-react";
import styles from "./dashboard.module.css";

// ---------------------
// Helpers
// ---------------------
const DIAS_ABREV = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"];

function shortLabel(dateStr: string): string {
  // dateStr format can be "10/04 sexta-feira" OR "10/04" already short
  // Extract just DD/MM and weekday abbreviation
  const parts = dateStr.split(" ");
  const ddmm = parts[0]; // "10/04"

  // Parse date from dd/mm to get weekday
  if (ddmm && ddmm.includes("/")) {
    const [dd, mm] = ddmm.split("/").map(Number);
    const year = new Date().getFullYear();
    const d = new Date(year, mm - 1, dd);
    const weekday = DIAS_ABREV[d.getDay()];
    return `${dd}/${mm < 10 ? "0" + mm : mm} ${weekday}`;
  }
  return dateStr;
}

// ---------------------
// Component
// ---------------------
export default function DashboardPage() {
  const router = useRouter();
  const [plan, setPlan] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [viewMode, setViewMode] = useState<"day" | "week" | "month" | "year">("month");
  const [currentTipIndex, setCurrentTipIndex] = useState(0);
  const [direction, setDirection] = useState(1);
  const [isHovering, setIsHovering] = useState(false);
  const [progress, setProgress] = useState(0);

  // Weight Log state
  const [weightLogs, setWeightLogs] = useState<any[]>([]);
  const [newWeight, setNewWeight] = useState("");
  const [newNote, setNewNote] = useState("");
  const [logSubmitting, setLogSubmitting] = useState(false);
  const [logMessage, setLogMessage] = useState("");
  const [projectionData, setProjectionData] = useState<any[]>([]);
  const [userName, setUserName] = useState("");
  const [mealExpanded, setMealExpanded] = useState<Record<number, boolean>>({});

  const fetchData = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }
    try {
      // Buscar apenas o nome (sem dados sensíveis)
      const meData = await fetchApi("/me", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (meData?.name) setUserName(meData.name.split(" ")[0]);

      const data = await fetchApi("/my-plan", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setPlan(data);

      // Parse projection
      if (data.projection_data) {
        try {
          setProjectionData(JSON.parse(data.projection_data));
        } catch {}
      }

      // Fetch weight logs
      const logsData = await fetchApi("/weight-logs", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setWeightLogs(logsData || []);
    } catch (err: any) {
      if (err.message === "Plan not found" || err.message === "Health profile missing") {
        router.push("/onboarding");
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [router]);

  // Tips
  const tipsList = useMemo(() => {
    const defaultTips = [
      "Beba pelo menos 35ml de água por quilo de peso corporal.",
      "Tente dormir de 7 a 8 horas para garantir a recuperação muscular.",
      "Inclua uma fonte de proteína em todas as suas refeições principais.",
      "Pratos coloridos garantem uma maior variedade de micronutrientes.",
      "Evite ultraprocessados; prefira sempre alimentos descascados a desembalados.",
      "A musculação ajuda a queimar calorias mesmo em estado de repouso.",
    ];
    if (!plan || !plan.recommendations_text) return defaultTips;
    const fromBackend = plan.recommendations_text
      .replace(/💡 DICA.*:\n/, "")
      .split("|||")
      .map((t: string) => t.trim())
      .filter((t: string) => t.length > 0);
    return fromBackend.length > 0 ? fromBackend : defaultTips;
  }, [plan?.recommendations_text]);

  useEffect(() => {
    if (tipsList.length <= 1 || isHovering) return;
    const totalTime = 6000;
    const stepTime = 100;
    const totalSteps = totalTime / stepTime;
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          setDirection(1);
          setCurrentTipIndex((curr) => (curr + 1) % tipsList.length);
          return 0;
        }
        return prev + 100 / totalSteps;
      });
    }, stepTime);
    return () => clearInterval(interval);
  }, [tipsList, isHovering]);

  useEffect(() => {
    setCurrentTipIndex(0);
    setProgress(0);
  }, [plan?.id]);

  const nextTip = (e?: any) => {
    e?.stopPropagation();
    setDirection(1);
    setCurrentTipIndex((prev) => (prev + 1) % tipsList.length);
    setProgress(0);
  };
  const prevTip = (e?: any) => {
    e?.stopPropagation();
    setDirection(-1);
    setCurrentTipIndex((prev) => (prev - 1 + tipsList.length) % tipsList.length);
    setProgress(0);
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/login");
  };
  const handleRefazer = () => router.push("/onboarding");

  // Weight Log submit
  const handleWeightLog = async (e: React.FormEvent) => {
    e.preventDefault();
    const val = parseFloat(newWeight);
    if (!val || val < 20 || val > 300) {
      setLogMessage("Informe um peso válido (20–300 kg).");
      return;
    }
    setLogSubmitting(true);
    setLogMessage("");
    try {
      const token = localStorage.getItem("token");
      const res = await fetchApi("/weight-log", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ weight: val, note: newNote || null }),
      });
      setLogMessage(res.message || "Registrado!");
      setNewWeight("");
      setNewNote("");
      if (res.logs) setWeightLogs(res.logs.reverse());
      if (res.new_projection) {
        try {
          setProjectionData(JSON.parse(res.new_projection));
        } catch {}
      }
      fetchData(); // Atualiza métricas e plano com o novo peso
    } catch (err: any) {
      setLogMessage("Erro: " + err.message);
    } finally {
      setLogSubmitting(false);
    }
  };

  // Filter projection for chart
  const filteredData = useMemo(() => {
    if (!projectionData.length) return [];
    let filtered: any[] = [];
    if (viewMode === "day") {
      filtered = projectionData.slice(0, 30);
    } else if (viewMode === "week") {
      filtered = projectionData.filter((d: any) => d.day % 7 === 0);
    } else if (viewMode === "month") {
      filtered = projectionData.filter((d: any) => d.day % 30 === 0);
    } else {
      filtered = projectionData.filter((d: any) => d.day % 90 === 0);
    }
    return filtered.map((d: any) => ({
      ...d,
      label: shortLabel(d.date),
    }));
  }, [projectionData, viewMode]);

  if (loading)
    return (
      <div className={`${styles.container} text-center`}>
        Carregando seu plano pessoal...
      </div>
    );
  if (error)
    return (
      <div className={`${styles.container} text-center`}>Erro: {error}</div>
    );
  if (!plan) return null;

  let meals: any[] = [];
  try {
    if (plan.meals_json) meals = JSON.parse(plan.meals_json);
  } catch {}

  const hasRealData = filteredData.some((d) => d.real !== undefined);

  const [notificationsEnabled, setNotificationsEnabled] = useState(true);

  // Helper to find current/next meal
  const currentMealInfo = useMemo(() => {
    if (!meals.length || !notificationsEnabled) return null;
    const now = new Date();
    const currentHour = now.getHours();
    const currentMinute = now.getMinutes();
    const currentTimeMinutes = currentHour * 60 + currentMinute;

    let closest = meals[0];
    let minDiff = Infinity;

    meals.forEach(m => {
      const [h, min] = m.time.split(':').map(Number);
      const mealTimeMinutes = h * 60 + min;
      const diff = Math.abs(currentTimeMinutes - mealTimeMinutes);
      if (diff < minDiff) {
        minDiff = diff;
        closest = m;
      }
    });

    return { meal: closest, isTime: minDiff <= 45, diff: minDiff };
  }, [meals]);

  return (
    <div className={styles.container}>
      <div className="container">
        {/* Header */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "2rem",
            flexWrap: "wrap",
            gap: "1rem",
          }}
        >
          <div>
            <h1 style={{ fontSize: "1.875rem", fontWeight: "bold", margin: 0, display: "flex", alignItems: "center", gap: "0.5rem" }}>
              {userName ? <>Olá, {userName} <Hand className="text-primary" size={24} /></> : "Meu Plano Nutricional"}
            </h1>
            <p style={{ color: "var(--muted)", fontSize: "0.875rem" }}>
              Evolução e metas personalizadas
            </p>
          </div>
          <div style={{ display: "flex", gap: "1rem" }} className="print-hide">
            <button
              onClick={() => window.print()}
              className="btn flex items-center gap-2"
              style={{
                background: "var(--card-bg)",
                border: "1px solid var(--card-border)",
                color: "var(--foreground)",
                fontWeight: "bold",
              }}
            >
              <FileText size={18} /> Exportar em PDF
            </button>
            <button
              onClick={handleRefazer}
              className="btn flex items-center gap-2"
              style={{
                background: "var(--primary)",
                color: "var(--primary-foreground)",
                fontWeight: "bold",
              }}
            >
              <Settings size={18} /> Refazer / Ajustar Plano
            </button>
            <button
              onClick={() => setNotificationsEnabled(!notificationsEnabled)}
              className="btn flex items-center gap-2"
              style={{
                background: notificationsEnabled ? "rgba(16, 185, 129, 0.1)" : "rgba(239, 68, 68, 0.1)",
                border: `1px solid ${notificationsEnabled ? "var(--primary)" : "var(--error)"}`,
                color: notificationsEnabled ? "var(--primary)" : "var(--error)",
                fontWeight: "bold"
              }}
            >
              {notificationsEnabled ? <Bell size={18} /> : <BellOff size={18} />}
              {notificationsEnabled ? "Alertas: ON" : "Alertas: OFF"}
            </button>
            <button
              onClick={handleLogout}
              className="btn flex items-center gap-2"
              style={{
                background: "transparent",
                border: "1px solid var(--primary)",
                color: "var(--primary)",
              }}
            >
              <LogOut size={18} /> Sair
            </button>
          </div>
        </div>

        {/* Smart Notifications */}
        <div style={{ marginBottom: "2rem", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "1rem" }}>
          {currentMealInfo && currentMealInfo.isTime && (
            <div className="glass-card" style={{ 
              padding: "1rem", 
              border: "2px solid var(--primary)", 
              background: "rgba(16, 185, 129, 0.05)",
              display: "flex",
              gap: "1rem",
              alignItems: "center"
            }}>
              <div style={{ 
                width: "80px", 
                height: "80px", 
                borderRadius: "12px", 
                overflow: "hidden",
                flexShrink: 0
              }}>
                <img 
                  src={
                    currentMealInfo.meal.label.toUpperCase().includes("CAFÉ") ? "/images/cafe.png" :
                    currentMealInfo.meal.label.toUpperCase().includes("ALMOÇO") ? "/images/almoco.png" :
                    currentMealInfo.meal.label.toUpperCase().includes("JANTAR") ? "/images/jantar.png" :
                    "/images/lanche.png"
                  } 
                  style={{ width: "100%", height: "100%", objectFit: "cover" }}
                />
              </div>
              <div>
                <h3 style={{ fontSize: "0.9rem", color: "var(--primary)", margin: 0, display: "flex", alignItems: "center", gap: "0.4rem" }}>
                  <Bell size={16} /> HORA DE COMER! ({currentMealInfo.meal.time})
                </h3>
                <p style={{ fontWeight: "bold", fontSize: "1.1rem", margin: "0.2rem 0" }}>{currentMealInfo.meal.label}</p>
                <p style={{ fontSize: "0.85rem", color: "var(--muted)", margin: 0 }}>{currentMealInfo.meal.suggestion}</p>
              </div>
            </div>
          )}

          <div className="glass-card" style={{ 
            padding: "1rem", 
            border: "1px solid var(--secondary)", 
            background: "rgba(99, 102, 241, 0.05)",
            display: "flex",
            gap: "1rem",
            alignItems: "center"
          }}>
              <div style={{ 
                width: "50px", 
                height: "50px", 
                borderRadius: "50%", 
                background: "var(--secondary)", 
                display: "flex", 
                alignItems: "center", 
                justifyContent: "center",
                color: "white"
              }}>
                <Droplet size={24} />
              </div>
            <div>
              <h3 style={{ fontSize: "0.9rem", color: "var(--secondary)", margin: 0 }}>HIDRATAÇÃO</h3>
              <p style={{ fontWeight: "bold", fontSize: "1rem", margin: 0 }}>Beba 300ml de água agora</p>
              <p style={{ fontSize: "0.75rem", color: "var(--muted)", margin: 0 }}>Meta diária: {((plan.water_recommendation || 0)/1000).toFixed(1)}L</p>
            </div>
          </div>
        </div>

        {/* Evolution Graph */}
        {filteredData.length > 0 && (
          <div className="glass-card" style={{ marginBottom: "2rem" }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "1rem",
                flexWrap: "wrap",
                gap: "0.75rem",
              }}
            >
              <h2 style={{ fontSize: "1.25rem", color: "var(--primary)", margin: 0, display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <TrendingUp size={20} /> Evolução do Plano
              </h2>
              <div className={styles.tabs}>
                {(["day", "week", "month", "year"] as const).map((m) => (
                  <button
                    key={m}
                    className={`${styles.tab} ${viewMode === m ? styles.tabActive : ""}`}
                    onClick={() => setViewMode(m)}
                  >
                    {{ day: "Diário", week: "Semanal", month: "Mensal", year: "Anual" }[m]}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ width: "100%", height: 300 }}>
              <ResponsiveContainer>
                <LineChart
                  data={filteredData}
                  margin={{ top: 20, right: 30, left: 0, bottom: 30 }}
                >
                  <XAxis
                    dataKey="label"
                    stroke="var(--chart-axis)"
                    tick={{ fill: "var(--chart-axis)", fontSize: 11 }}
                    angle={-35}
                    textAnchor="end"
                    height={55}
                    interval="preserveStartEnd"
                  />
                  <YAxis
                    stroke="var(--chart-axis)"
                    tick={{ fill: "var(--chart-axis)", fontSize: 12 }}
                    domain={["dataMin - 2", "dataMax + 2"]}
                    tickFormatter={(v) => `${v}kg`}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "var(--tooltip-bg)",
                      borderColor: "var(--primary)",
                      borderRadius: "8px",
                      color: "var(--foreground)",
                    }}
                    labelStyle={{ color: "var(--foreground)", fontWeight: "bold", marginBottom: "4px" }}
                    formatter={(value: any, name: any) => {
                      const labels: Record<string, string> = {
                        weight: "Projeção (kg)",
                        real: "Peso Real (kg)",
                        trend: "Meta Ideal (kg)",
                      };
                      return [`${value} kg`, labels[name] || name];
                    }}
                  />
                  {hasRealData && <Legend wrapperStyle={{ paddingTop: "8px", fontSize: "0.8rem" }} />}
                  <Line
                    type="monotone"
                    dataKey="weight"
                    name="Projeção"
                    stroke="var(--primary)"
                    strokeWidth={2.5}
                    dot={viewMode !== "day" ? { r: 3, fill: "var(--primary)" } : false}
                    strokeDasharray={hasRealData ? "6 3" : undefined}
                  />
                  {hasRealData && (
                    <Line
                      type="monotone"
                      dataKey="real"
                      name="Peso Real"
                      stroke="#f97316"
                      strokeWidth={3}
                      dot={{ r: 5, fill: "#f97316", strokeWidth: 2, stroke: "#fff" }}
                      connectNulls={false}
                    />
                  )}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* --- Weight Log Panel --- */}
        <div className="glass-card" style={{ marginBottom: "2rem" }}>
          <h2 style={{ fontSize: "1.25rem", color: "var(--primary)", marginBottom: "1rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <BarChart4 size={20} /> Registrar Peso Atual
          </h2>
          <p style={{ color: "var(--muted)", fontSize: "0.85rem", marginBottom: "1rem" }}>
            Informe seu peso periodicamente para o sistema recalcular sua projeção com dados reais.
          </p>

          <form onSubmit={handleWeightLog} style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", alignItems: "flex-end" }}>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.35rem" }}>
              <label style={{ fontSize: "0.8rem", color: "var(--muted)" }}>Peso atual (kg) *</label>
              <input
                type="number"
                step="0.1"
                min="20"
                max="300"
                value={newWeight}
                onChange={(e) => setNewWeight(e.target.value)}
                placeholder="ex: 78.5"
                required
                style={{
                  background: "var(--input-bg)",
                  border: "1px solid var(--card-border)",
                  borderRadius: "8px",
                  color: "var(--foreground)",
                  padding: "0.6rem 0.9rem",
                  fontSize: "1rem",
                  width: "140px",
                }}
              />
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.35rem", flex: 1, minWidth: "180px" }}>
              <label style={{ fontSize: "0.8rem", color: "var(--muted)" }}>Observação (opcional)</label>
              <input
                type="text"
                value={newNote}
                onChange={(e) => setNewNote(e.target.value)}
                placeholder="ex: após treino, manhã em jejum..."
                style={{
                  background: "var(--input-bg)",
                  border: "1px solid var(--card-border)",
                  borderRadius: "8px",
                  color: "var(--foreground)",
                  padding: "0.6rem 0.9rem",
                  fontSize: "0.9rem",
                  width: "100%",
                }}
              />
            </div>
            <button
              type="submit"
              disabled={logSubmitting}
              style={{
                background: "var(--primary)",
                color: "var(--primary-foreground)",
                border: "none",
                borderRadius: "8px",
                padding: "0.65rem 1.5rem",
                fontWeight: "bold",
                cursor: logSubmitting ? "not-allowed" : "pointer",
                opacity: logSubmitting ? 0.7 : 1,
                transition: "all 0.2s",
              }}
            >
              {logSubmitting ? "Salvando..." : "Registrar Peso"}
            </button>
          </form>

          {logMessage && (
            <p
              style={{
                marginTop: "0.75rem",
                fontSize: "0.875rem",
                color: logMessage.startsWith("Erro") ? "#f87171" : "var(--primary)",
                fontWeight: "500",
              }}
            >
              {logMessage}
            </p>
          )}

          {/* History */}
          {weightLogs.length > 0 && (
            <div style={{ marginTop: "1.5rem" }}>
              <h3 style={{ fontSize: "0.95rem", color: "var(--muted)", marginBottom: "0.75rem" }}>
                Histórico de Peso
              </h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", maxHeight: "220px", overflowY: "auto" }}>
                {weightLogs.map((log: any, idx: number) => {
                  const dt = new Date(log.logged_at);
                  const dateStr = dt.toLocaleDateString("pt-BR", {
                    day: "2-digit",
                    month: "2-digit",
                    year: "numeric",
                  });
                  const timeStr = dt.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
                  return (
                    <div
                      key={log.id}
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        padding: "0.6rem 0.9rem",
                        background: idx === 0 ? "rgba(0,255,115,0.06)" : "var(--input-bg)",
                        borderRadius: "8px",
                        border: `1px solid ${idx === 0 ? "rgba(0,255,115,0.2)" : "var(--card-border)"}`,
                      }}
                    >
                      <div>
                        <span style={{ fontWeight: "700", fontSize: "1.1rem", color: idx === 0 ? "var(--primary)" : "var(--foreground)" }}>
                          {log.weight} kg
                        </span>
                        {log.note && (
                          <span style={{ marginLeft: "0.75rem", fontSize: "0.8rem", color: "var(--muted)", fontStyle: "italic" }}>
                            {log.note}
                          </span>
                        )}
                      </div>
                      <span style={{ fontSize: "0.78rem", color: "var(--muted)" }}>
                        {dateStr} às {timeStr}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Main Grid */}
        <div className={styles.dashboardGrid}>
          {/* Summary Column */}
          <div className="glass-card">
            <h2 style={{ fontSize: "1.25rem", marginBottom: "1rem", color: "var(--primary)", display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <Dna size={20} /> Resumo Biológico
            </h2>
            {[
              { label: "IMC", value: plan.imc },
              { label: "Classificação IMC", value: plan.imc_classification || "—" },
              { label: "Taxa Metabólica Basal", value: `${plan.tmb} kcal` },
              { label: "Gasto Diário (TDEE)", value: `${plan.tdee} kcal` },
              {
                label: "Água Recomendada",
                value: `${(plan.water_recommendation / 1000).toFixed(1)} Litros`,
              },
            ].map(({ label, value }) => {
              const isImcClass = label === "Classificação IMC";
              const isAlert = isImcClass && (String(value).includes("Desnutrição") || String(value).includes("Obesidade") || String(value).includes("Baixo peso") || String(value).includes("Magreza"));
              const isOk = isImcClass && (String(value).includes("Normal") || String(value).includes("Peso normal"));
              return (
                <div key={label} className={styles.statRow}>
                  <span className={styles.statLabel}>{label}</span>
                  <span
                    style={{
                      fontWeight: "bold",
                      color: isImcClass ? (isAlert ? "#f87171" : isOk ? "var(--primary)" : "#fbbf24") : undefined,
                      background: isImcClass ? (isAlert ? "rgba(248,113,113,0.1)" : isOk ? "rgba(0,255,115,0.1)" : "rgba(251,191,36,0.1)") : undefined,
                      padding: isImcClass ? "0.15rem 0.5rem" : undefined,
                      borderRadius: isImcClass ? "20px" : undefined,
                      fontSize: isImcClass ? "0.8rem" : undefined,
                    }}
                  >
                    {value}
                  </span>
                </div>
              );
            })}

            {/* Tips Carousel */}
            <div
              className={`glass-card ${styles.tipsCard} ${tipsList[currentTipIndex]?.startsWith("⚠️") ? styles.alertTip : ""}`}
              onMouseEnter={() => setIsHovering(true)}
              onMouseLeave={() => setIsHovering(false)}
              style={{
                padding: "1.25rem",
                marginTop: "1.5rem",
                background: tipsList[currentTipIndex]?.startsWith("⚠️") ? "rgba(248, 113, 113, 0.05)" : "rgba(0, 255, 115, 0.05)",
                border: tipsList[currentTipIndex]?.startsWith("⚠️") ? "1px solid rgba(248, 113, 113, 0.2)" : "1px solid rgba(0, 255, 115, 0.1)",
                minHeight: "260px",
                display: "flex",
                flexDirection: "column",
                cursor: "default",
                transition: "all 0.5s ease",
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: "0.4rem",
                  borderBottom: tipsList[currentTipIndex]?.startsWith("⚠️") ? "1px solid rgba(248, 113, 113, 0.2)" : "1px solid rgba(0, 255, 115, 0.2)",
                  paddingBottom: "0.4rem",
                }}
              >
                <h3 style={{ fontSize: "1rem", color: tipsList[currentTipIndex]?.startsWith("⚠️") ? "#f87171" : "var(--primary)", margin: 0, display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  {tipsList[currentTipIndex]?.startsWith("⚠️") ? <><AlertTriangle size={18} /> ALERTA DE SAÚDE</> : <><Lightbulb size={18} /> Dicas do Dia</>}{" "}
                  {isHovering && (
                    <span style={{ fontSize: "0.6rem", color: "#94a3b8", marginLeft: "0.5rem" }}>
                      (Pausado)
                    </span>
                  )}
                </h3>
                <div className={styles.carouselControls}>
                  <button className={styles.carouselBtn} onClick={prevTip} title="Anterior">
                    <ArrowLeft size={16} />
                  </button>
                  <button className={styles.carouselBtn} onClick={nextTip} title="Próximo">
                    <ArrowRight size={16} />
                  </button>
                </div>
              </div>
              <div className={styles.progressContainer}>
                <div className={styles.progressFiller} style={{ width: `${progress}%`, background: tipsList[currentTipIndex]?.startsWith("⚠️") ? "#f87171" : "var(--primary)" }} />
              </div>
              <div style={{ position: "relative", marginTop: "0.75rem", paddingBottom: "1.5rem" }}>
                {tipsList.map((tip: string, idx: number) => {
                  const isActive = idx === currentTipIndex;
                  const xPos = isActive ? 0 : direction > 0 ? 50 : -50;
                  const isAlert = tip.startsWith("⚠️");
                  return (
                    <p
                      key={idx}
                      className={isAlert ? styles.highRiskText : ""}
                      style={{
                        fontSize: isAlert ? "0.95rem" : "0.875rem",
                        lineHeight: "1.6",
                        position: isActive ? "relative" : "absolute",
                        top: 0,
                        left: 0,
                        width: "100%",
                        opacity: isActive ? 1 : 0,
                        transform: isActive ? "translateX(0)" : `translateX(${xPos}px)`,
                        transition: "all 0.6s cubic-bezier(0.16, 1, 0.3, 1)",
                        margin: 0,
                        pointerEvents: isActive ? "auto" : "none",
                        visibility: isActive || Math.abs(xPos) < 100 ? "visible" : "hidden",
                      }}
                    >
                      {tip}
                    </p>
                  );
                })}
              </div>
              <div className={styles.dotsContainer}>
                {tipsList.map((_: any, idx: number) => (
                  <div
                    key={idx}
                    className={`${styles.dot} ${idx === currentTipIndex ? styles.dotActive : ""}`}
                    onClick={() => {
                      setDirection(idx > currentTipIndex ? 1 : -1);
                      setCurrentTipIndex(idx);
                      setProgress(0);
                    }}
                    style={{ cursor: "pointer" }}
                  />
                ))}
              </div>
            </div>
          </div>

          {/* Meals Column */}
          <div className="glass-card">
            <h2 style={{ fontSize: "1.25rem", marginBottom: "1.5rem", color: "var(--primary)", display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <Utensils size={20} /> Planejamento de Refeições
            </h2>
            <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
              {meals.map((meal: any, idx: number) => {
                const mealLabel = meal.label.toUpperCase();
                const mealImages: Record<string, string> = {
                  "CAFÉ DA MANHÃ": "/images/cafe.png",
                  "ALMOÇO": "/images/almoco.png",
                  "JANTAR": "/images/jantar.png",
                  "LANCHE DA MANHÃ": "/images/lanche.png",
                  "LANCHE DA TARDE": "/images/lanche.png",
                  "CEIA": "/images/ceia.png",
                  "PRÉ-TREINO": "/images/pre_treino.png",
                  "PÓS-TREINO": "/images/lanche.png", // Reuse lanche as pos-treino quota was exhausted
                };
                const imageUrl = mealImages[mealLabel] || "/images/lanche.png";

                return (
                  <div
                    key={idx}
                    className={styles.mealCard}
                    style={{
                      background: "var(--meal-bg)",
                      padding: "0",
                      borderRadius: "16px",
                      border: "1px solid var(--card-border)",
                      overflow: "hidden",
                      transition: "transform 0.2s ease",
                    }}
                  >
                    {/* Imagem Figurativa */}
                    <div style={{ width: "100%", height: "140px", position: "relative" }}>
                      <img 
                        src={imageUrl} 
                        alt={meal.label} 
                        style={{ width: "100%", height: "100%", objectFit: "cover" }}
                      />
                      <div style={{ 
                        position: "absolute", 
                        bottom: "0", 
                        left: "0", 
                        right: "0", 
                        background: "linear-gradient(to top, rgba(0,0,0,0.8), transparent)", 
                        padding: "1rem",
                        color: "white"
                      }}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                          <span style={{ fontWeight: "bold", fontSize: "1.1rem", textTransform: "uppercase", letterSpacing: "1px" }}>
                            {meal.label}
                          </span>
                          <span style={{ background: "var(--primary)", color: "black", padding: "0.2rem 0.6rem", borderRadius: "6px", fontSize: "0.75rem", fontWeight: "bold" }}>
                            {meal.time}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div style={{ padding: "1.25rem" }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.75rem" }}>
                        <div style={{ fontSize: "0.95rem", color: "var(--foreground)", fontWeight: "500", lineHeight: "1.5" }}>
                          {meal.suggestion}
                        </div>
                        <button
                          onClick={() => setMealExpanded(prev => ({ ...prev, [idx]: !prev[idx] }))}
                          style={{
                            background: "transparent",
                            border: "1px solid var(--card-border)",
                            borderRadius: "8px",
                            color: "var(--muted)",
                            fontSize: "0.75rem",
                            padding: "0.25rem 0.5rem",
                            cursor: "pointer",
                            transition: "all 0.2s",
                            display: "flex",
                            alignItems: "center",
                            gap: "0.3rem",
                            flexShrink: 0,
                            marginLeft: "1rem"
                          }}
                        >
                          {mealExpanded[idx] ? <ChevronUp size={14} /> : <RefreshCw size={12} />}
                        </button>
                      </div>

                      {mealExpanded[idx] && (
                        <div
                          style={{
                            marginBottom: "1rem",
                            padding: "0.75rem",
                            background: "rgba(0,255,115,0.05)",
                            border: "1px solid rgba(0,255,115,0.2)",
                            borderRadius: "8px",
                            fontSize: "0.82rem",
                          }}
                        >
                          <span style={{ color: "var(--primary)", fontWeight: "600", display: "block", marginBottom: "0.25rem" }}>🔄 Sugestões de Troca:</span>
                          <div style={{ color: "var(--foreground)", lineHeight: "1.4" }}>
                            {meal.substitutions ? (
                              meal.substitutions.split('\n').map((line: string, i: number) => (
                                <div key={i}>{line}</div>
                              ))
                            ) : "Mantenha a proporção de macros com alimentos similares."}
                          </div>
                        </div>
                      )}

                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid var(--card-border)", paddingTop: "0.75rem" }}>
                        <div style={{ display: "flex", gap: "0.75rem", fontSize: "0.8rem", color: "var(--muted)" }}>
                          <span>{meal.calories} kcal</span>
                          <span>P: <strong>{meal.protein}g</strong></span>
                          <span>C: <strong>{meal.carbs}g</strong></span>
                          <span>G: <strong>{meal.fat}g</strong></span>
                        </div>
                        <div style={{ display: "flex", gap: "2px" }}>
                          {[...Array(3)].map((_, i) => (
                            <div key={i} style={{ width: "4px", height: "4px", borderRadius: "50%", background: i === 0 ? "var(--primary)" : "var(--card-border)" }} />
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Macro Goals */}
          <div className="glass-card" style={{ gridColumn: "span 2" }}>
            <h2 style={{ fontSize: "1.25rem", marginBottom: "0.5rem", color: "var(--primary)" }}>
              Meta Diária
            </h2>
            <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: "3rem", margin: "1rem 0", flexWrap: "wrap" }}>
              <p style={{ fontSize: "3rem", fontWeight: "bold", margin: 0 }}>
                {plan.target_calories}{" "}
                <span style={{ fontSize: "1.125rem", color: "var(--muted)" }}>kcal</span>
              </p>
              <div className={styles.macroGrid} style={{ flex: 1, gridTemplateColumns: "repeat(3, 1fr)", gap: "1rem" }}>
                <div className={styles.macroCard}>
                  <div style={{ fontSize: "0.875rem", color: "var(--muted)" }}>Proteínas</div>
                  <div className={styles.macroValue}>{plan.target_protein}g</div>
                  <div style={{ fontSize: "0.75rem", color: "var(--primary)" }}>{(plan.target_protein * 4).toFixed(0)} kcal</div>
                </div>
                <div className={styles.macroCard}>
                  <div style={{ fontSize: "0.875rem", color: "var(--muted)" }}>Carboidratos</div>
                  <div className={styles.macroValue}>{plan.target_carbs}g</div>
                  <div style={{ fontSize: "0.75rem", color: "var(--secondary)" }}>{(plan.target_carbs * 4).toFixed(0)} kcal</div>
                </div>
                <div className={styles.macroCard}>
                  <div style={{ fontSize: "0.875rem", color: "var(--muted)" }}>Gorduras</div>
                  <div className={styles.macroValue}>{plan.target_fats}g</div>
                  <div style={{ fontSize: "0.75rem", color: "var(--warning)" }}>{(plan.target_fats * 9).toFixed(0)} kcal</div>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
