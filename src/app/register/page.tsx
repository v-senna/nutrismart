"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { fetchApi } from "@/lib/api";
import Link from "next/link";
import styles from "./register.module.css";
import { Leaf, Loader2, ArrowRight, AlertCircle } from "lucide-react";

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    name: "",
    cpf: "",
    email: "",
    phone: "",
    password: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.id]: e.target.value });
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      // 1. Registrar usuário
      await fetchApi("/register", {
        method: "POST",
        body: JSON.stringify(formData),
      });
      
      // 2. Fazer login automático
      const loginFormData = new URLSearchParams();
      loginFormData.append("username", formData.email);
      loginFormData.append("password", formData.password);

      const loginData = await fetchApi("/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: loginFormData.toString(),
      });

      if (loginData.access_token) {
        localStorage.setItem("token", loginData.access_token);
        router.push("/onboarding"); // Redireciona para o Wizard de Saúde
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
        <h1 className={styles.vintageTitle}>
          <Leaf className="w-8 h-8 text-[#6a7356]" />
          Criar Conta
        </h1>
        <p className={styles.vintageSubtitle}>
          Junte-se ao NutriSmart para planos personalizados de nutrição.
        </p>

        {error && (
          <div className={styles.errorMessage}>
            <AlertCircle className="w-5 h-5" />
            {error}
          </div>
        )}

        <form onSubmit={handleRegister}>
          <div className={styles.vintageInputGroup}>
            <label className={styles.vintageLabel} htmlFor="name">Nome Completo</label>
            <input id="name" type="text" className={styles.vintageInput} value={formData.name} onChange={handleChange} placeholder="João da Silva" required />
          </div>

          <div className={styles.rowGrid}>
            <div className={styles.vintageInputGroup}>
              <label className={styles.vintageLabel} htmlFor="cpf">CPF</label>
              <input id="cpf" type="text" className={styles.vintageInput} value={formData.cpf} onChange={handleChange} placeholder="000.000.000-00" required />
            </div>

            <div className={styles.vintageInputGroup}>
              <label className={styles.vintageLabel} htmlFor="phone">Telefone</label>
              <input id="phone" type="text" className={styles.vintageInput} value={formData.phone} onChange={handleChange} placeholder="(11) 90000-0000" required />
            </div>
          </div>

          <div className={styles.vintageInputGroup}>
            <label className={styles.vintageLabel} htmlFor="email">E-mail</label>
            <input id="email" type="email" className={styles.vintageInput} value={formData.email} onChange={handleChange} placeholder="seu@email.com" required />
          </div>

          <div className={styles.vintageInputGroup}>
            <label className={styles.vintageLabel} htmlFor="password">Senha</label>
            <input id="password" type="password" className={styles.vintageInput} value={formData.password} onChange={handleChange} placeholder="••••••••" required />
          </div>

          <button type="submit" className={styles.vintageButton} disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Criando Conta...
              </>
            ) : (
              <>
                Começar Minha Jornada
                <ArrowRight className="w-5 h-5" />
              </>
            )}
          </button>
        </form>

        <p className={styles.loginText}>
          Já tem uma conta? <Link href="/login" className={styles.loginLink}>Entrar</Link>
        </p>
      </div>
    </div>
  );
}
