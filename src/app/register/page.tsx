"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { fetchApi } from "@/lib/api";
import Link from "next/link";
import styles from "./register.module.css";

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
    <div className={styles.container}>
      <div className={`glass-card ${styles.registerCard}`}>
        <h1 className="text-center mb-2 text-3xl font-bold">✨ Criar Conta</h1>
        <p className="text-center mb-8 text-gray-400">Junte-se ao NutriSmart para planos personalizados.</p>

        {error && <div className={styles.errorMessage}>{error}</div>}

        <form onSubmit={handleRegister}>
          <div className="input-group">
            <label className="input-label" htmlFor="name">Nome Completo</label>
            <input id="name" type="text" className="input-field" value={formData.name} onChange={handleChange} placeholder="João da Silva" required />
          </div>

          <div className={styles.rowGrid}>
            <div className="input-group">
              <label className="input-label" htmlFor="cpf">CPF</label>
              <input id="cpf" type="text" className="input-field" value={formData.cpf} onChange={handleChange} placeholder="000.000.000-00" required />
            </div>

            <div className="input-group">
              <label className="input-label" htmlFor="phone">Telefone</label>
              <input id="phone" type="text" className="input-field" value={formData.phone} onChange={handleChange} placeholder="(11) 90000-0000" required />
            </div>
          </div>

          <div className="input-group">
            <label className="input-label" htmlFor="email">E-mail</label>
            <input id="email" type="email" className="input-field" value={formData.email} onChange={handleChange} placeholder="seu@email.com" required />
          </div>

          <div className="input-group">
            <label className="input-label" htmlFor="password">Senha</label>
            <input id="password" type="password" className="input-field" value={formData.password} onChange={handleChange} placeholder="••••••••" required />
          </div>

          <button type="submit" className={`btn btn-primary w-full mt-4`} disabled={loading} style={{ width: '100%' }}>
            {loading ? "⌛ Criando Conta..." : "🚀 Começar Minha Jornada"}
          </button>
        </form>

        <p className="text-center mt-6 text-sm">
          Já tem uma conta? <Link href="/login" className={styles.loginLink}>Entrar</Link>
        </p>
      </div>
    </div>
  );
}
