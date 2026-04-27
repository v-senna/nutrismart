"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { fetchApi } from "@/lib/api";
import Link from "next/link";
import styles from "./register.module.css";
import { Leaf, Loader2, ArrowRight, AlertCircle, CheckCircle2, XCircle } from "lucide-react";

// ─── Máscaras ───────────────────────────────────────────────
function formatCPF(v: string) {
  const d = v.replace(/\D/g, "").slice(0, 11);
  return d
    .replace(/(\d{3})(\d)/, "$1.$2")
    .replace(/(\d{3})(\d)/, "$1.$2")
    .replace(/(\d{3})(\d{1,2})$/, "$1-$2");
}

function formatPhone(v: string) {
  const d = v.replace(/\D/g, "").slice(0, 11);
  if (d.length <= 10) {
    return d
      .replace(/(\d{2})(\d)/, "($1) $2")
      .replace(/(\d{4})(\d)/, "$1-$2");
  }
  return d
    .replace(/(\d{2})(\d)/, "($1) $2")
    .replace(/(\d{5})(\d)/, "$1-$2");
}

// ─── Validações ──────────────────────────────────────────────
function isValidCPF(cpf: string) {
  const d = cpf.replace(/\D/g, "");
  if (d.length !== 11 || /^(\d)\1+$/.test(d)) return false;
  let sum = 0;
  for (let i = 0; i < 9; i++) sum += parseInt(d[i]) * (10 - i);
  let r = (sum * 10) % 11;
  if (r === 10 || r === 11) r = 0;
  if (r !== parseInt(d[9])) return false;
  sum = 0;
  for (let i = 0; i < 10; i++) sum += parseInt(d[i]) * (11 - i);
  r = (sum * 10) % 11;
  if (r === 10 || r === 11) r = 0;
  return r === parseInt(d[10]);
}

function isValidEmail(email: string) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// ─── Toast ───────────────────────────────────────────────────
type ToastType = "success" | "error" | "info";
interface Toast {
  id: number;
  message: string;
  type: ToastType;
}

let toastId = 0;

function ToastContainer({ toasts, remove }: { toasts: Toast[]; remove: (id: number) => void }) {
  return (
    <div className={styles.toastContainer}>
      {toasts.map((t) => (
        <div key={t.id} className={`${styles.toast} ${styles[`toast_${t.type}`]}`}>
          {t.type === "success" && <CheckCircle2 className="w-5 h-5 flex-shrink-0" />}
          {t.type === "error" && <XCircle className="w-5 h-5 flex-shrink-0" />}
          {t.type === "info" && <AlertCircle className="w-5 h-5 flex-shrink-0" />}
          <span>{t.message}</span>
          <button className={styles.toastClose} onClick={() => remove(t.id)}>✕</button>
        </div>
      ))}
    </div>
  );
}

// ────────────────────────────────────────────────────────────
export default function RegisterPage() {
  const [formData, setFormData] = useState({
    name: "",
    cpf: "",
    email: "",
    phone: "",
    password: "",
  });
  const [emailTouched, setEmailTouched] = useState(false);
  const [cpfTouched, setCpfTouched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const router = useRouter();

  const addToast = (message: string, type: ToastType = "info") => {
    const id = ++toastId;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => removeToast(id), 5000);
  };

  const removeToast = (id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { id, value } = e.target;
    if (id === "cpf") {
      setFormData({ ...formData, cpf: formatCPF(value) });
    } else if (id === "phone") {
      setFormData({ ...formData, phone: formatPhone(value) });
    } else {
      setFormData({ ...formData, [id]: value });
    }
  };

  // Validação de e-mail em tempo real
  useEffect(() => {
    if (!emailTouched || !formData.email) return;
    if (!isValidEmail(formData.email)) {
      addToast("E-mail inválido. Ex: nome@dominio.com", "error");
    }
  }, [formData.email, emailTouched]);

  // Validação de CPF em tempo real
  useEffect(() => {
    const digits = formData.cpf.replace(/\D/g, "");
    if (!cpfTouched || digits.length < 11) return;
    if (!isValidCPF(formData.cpf)) {
      addToast("CPF inválido. Verifique os números digitados.", "error");
    }
  }, [formData.cpf, cpfTouched]);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validações finais
    if (!isValidCPF(formData.cpf)) {
      addToast("CPF inválido. Verifique os números digitados.", "error");
      return;
    }
    if (!isValidEmail(formData.email)) {
      addToast("E-mail inválido. Corrija antes de continuar.", "error");
      return;
    }
    if (formData.password.length < 6) {
      addToast("A senha precisa ter no mínimo 6 caracteres.", "error");
      return;
    }

    setLoading(true);

    try {
      await fetchApi("/register", {
        method: "POST",
        body: JSON.stringify({
          ...formData,
          cpf: formData.cpf.replace(/\D/g, ""),
        }),
      });

      addToast("Conta criada! Fazendo login automático...", "success");

      const loginFormData = new URLSearchParams();
      loginFormData.append("username", formData.cpf.replace(/\D/g, ""));
      loginFormData.append("password", formData.password);

      const loginData = await fetchApi("/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: loginFormData.toString(),
      });

      if (loginData.access_token) {
        localStorage.setItem("token", loginData.access_token);
        router.push("/onboarding");
      }
    } catch (err: any) {
      addToast(err.message || "Erro ao criar conta. Tente novamente.", "error");
    } finally {
      setLoading(false);
    }
  };

  const emailIsInvalid = emailTouched && formData.email.length > 0 && !isValidEmail(formData.email);
  const cpfIsInvalid = cpfTouched && formData.cpf.replace(/\D/g, "").length === 11 && !isValidCPF(formData.cpf);

  return (
    <div className={styles.vintageContainer}>
      <ToastContainer toasts={toasts} remove={removeToast} />
      <div className={styles.vintageCard}>
        <h1 className={styles.vintageTitle}>
          <Leaf className="w-8 h-8 text-[#6a7356]" />
          Criar Conta
        </h1>
        <p className={styles.vintageSubtitle}>
          Junte-se ao NutriSmart para planos personalizados de nutrição.
        </p>

        <form onSubmit={handleRegister}>
          <div className={styles.vintageInputGroup}>
            <label className={styles.vintageLabel} htmlFor="name">Nome Completo</label>
            <input id="name" type="text" className={styles.vintageInput} value={formData.name} onChange={handleChange} placeholder="João da Silva" required />
          </div>

          <div className={styles.rowGrid}>
            <div className={styles.vintageInputGroup}>
              <label className={styles.vintageLabel} htmlFor="cpf">CPF</label>
              <input
                id="cpf"
                type="text"
                inputMode="numeric"
                className={`${styles.vintageInput} ${cpfIsInvalid ? styles.inputError : ""}`}
                value={formData.cpf}
                onChange={handleChange}
                onBlur={() => setCpfTouched(true)}
                placeholder="000.000.000-00"
                required
              />
              {cpfIsInvalid && <span className={styles.fieldError}>CPF inválido</span>}
            </div>

            <div className={styles.vintageInputGroup}>
              <label className={styles.vintageLabel} htmlFor="phone">Telefone</label>
              <input
                id="phone"
                type="text"
                inputMode="numeric"
                className={styles.vintageInput}
                value={formData.phone}
                onChange={handleChange}
                placeholder="(11) 90000-0000"
                required
              />
            </div>
          </div>

          <div className={styles.vintageInputGroup}>
            <label className={styles.vintageLabel} htmlFor="email">E-mail</label>
            <input
              id="email"
              type="email"
              className={`${styles.vintageInput} ${emailIsInvalid ? styles.inputError : ""}`}
              value={formData.email}
              onChange={handleChange}
              onBlur={() => setEmailTouched(true)}
              placeholder="seu@email.com"
              required
            />
            {emailIsInvalid && <span className={styles.fieldError}>E-mail inválido</span>}
          </div>

          <div className={styles.vintageInputGroup}>
            <label className={styles.vintageLabel} htmlFor="password">Senha</label>
            <input
              id="password"
              type="password"
              className={styles.vintageInput}
              value={formData.password}
              onChange={handleChange}
              placeholder="Mínimo 6 caracteres"
              minLength={6}
              required
            />
          </div>

          <button type="submit" className={styles.vintageButton} disabled={loading}>
            {loading ? (
              <><Loader2 className="w-5 h-5 animate-spin" /> Criando Conta...</>
            ) : (
              <>Começar Minha Jornada <ArrowRight className="w-5 h-5" /></>
            )}
          </button>
        </form>

        <p className={styles.loginText}>
          Já tem uma conta? <Link href="/login" className={styles.loginLink}>Entrar com CPF</Link>
        </p>
      </div>
    </div>
  );
}
