"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { fetchApi } from "@/lib/api";
import Link from "next/link";
import styles from "./login.module.css";
import { Leaf, Loader2, LogIn, AlertCircle, IdCard } from "lucide-react";

function formatCPF(value: string) {
  const digits = value.replace(/\D/g, "").slice(0, 11);
  return digits
    .replace(/(\d{3})(\d)/, "$1.$2")
    .replace(/(\d{3})(\d)/, "$1.$2")
    .replace(/(\d{3})(\d{1,2})$/, "$1-$2");
}

export default function LoginPage() {
  const [cpf, setCpf] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleCpfChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCpf(formatCPF(e.target.value));
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    const cpfDigits = cpf.replace(/\D/g, "");
    if (cpfDigits.length !== 11) {
      setError("Digite um CPF válido com 11 dígitos.");
      return;
    }
    setError("");
    setLoading(true);

    try {
      const formData = new URLSearchParams();
      formData.append("username", cpfDigits);
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
      setError(err.message);
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
        <p className={styles.vintageSubtitle}>Entre com seu CPF para acessar sua conta</p>

        {error && (
          <div className={styles.errorMessage}>
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleLogin}>
          <div className={styles.vintageInputGroup}>
            <label className={styles.vintageLabel} htmlFor="cpf">
              <IdCard className="w-4 h-4 inline mr-1" />
              CPF
            </label>
            <input
              id="cpf"
              type="text"
              inputMode="numeric"
              className={styles.vintageInput}
              value={cpf}
              onChange={handleCpfChange}
              placeholder="000.000.000-00"
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
    </div>
  );
}
