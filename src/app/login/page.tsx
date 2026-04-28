"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { fetchApi } from "@/lib/api";
import Link from "next/link";
import styles from "./login.module.css";
import { Leaf, Loader2, LogIn, AlertCircle, IdCard } from "lucide-react";
import ThemeToggle from "@/components/ThemeToggle";

export default function LoginPage() {
  const [cpf, setCpf] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Identificar se é CPF (apenas dígitos) ou E-mail
    const identifier = cpf.trim();
    const isEmail = identifier.includes("@");
    const cleanIdentifier = isEmail ? identifier : identifier.replace(/\D/g, "");

    if (!isEmail && cleanIdentifier.length !== 11) {
      setError("Digite um CPF válido (11 dígitos) ou um e-mail.");
      return;
    }
    
    setError("");
    setLoading(true);

    try {
      const formData = new URLSearchParams();
      formData.append("username", cleanIdentifier);
      formData.append("password", password);

      const data = await fetchApi("/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData.toString(),
      });

      if (data.access_token) {
        localStorage.setItem("token", data.access_token);
        router.push("/dashboard");
      }
    } catch (err: any) {
      setError(err.message === "Unauthorized" ? "CPF/E-mail ou senha incorretos." : err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.vintageContainer}>
      <div className={styles.vintageCard}>
        <div className={styles.logoArea}>
          <Leaf className={styles.logoIcon} />
          <h1 className={styles.vintageTitle}>NutriSmart</h1>
        </div>
        <p className={styles.vintageSubtitle}>Acesse com seu CPF ou E-mail</p>

        {error && (
          <div className={styles.errorMessage}>
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleLogin}>
          <div className={styles.vintageInputGroup}>
            <label className={styles.vintageLabel} htmlFor="identifier">
              <IdCard className="w-4 h-4 inline mr-1" />
              Identificação
            </label>
            <input
              id="identifier"
              type="text"
              className={styles.vintageInput}
              value={cpf}
              onChange={(e) => setCpf(e.target.value)}
              placeholder="CPF ou E-mail"
              required
            />
          </div>

          <div className={styles.vintageInputGroup}>
            <label className={styles.vintageLabel} htmlFor="password">Senha</label>
            <input
              id="password"
              type="password"
              className={styles.vintageInput}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          <button type="submit" className={styles.vintageButton} disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Entrando...
              </>
            ) : (
              <>
                <LogIn className="w-5 h-5" />
                Entrar
              </>
            )}
          </button>
        </form>

        <p className={styles.loginText}>
          Ainda não tem conta? <Link href="/register" className={styles.loginLink}>Cadastre-se</Link>
        </p>
      </div>
      <ThemeToggle />
    </div>
  );
}
