"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { fetchApi } from "@/lib/api";
import Link from "next/link";
import styles from "./login.module.css";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const data = await fetchApi("/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
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
    <div className={styles.container}>
      <div className={`glass-card ${styles.loginCard}`}>
        <h1 className="text-center mb-2 text-3xl font-bold">🍏 NutriSmart</h1>
        <p className="text-center mb-8 text-gray-400">Entre na sua conta para acessar seus dados</p>

        {error && <div className={styles.errorMessage}>{error}</div>}

        <form onSubmit={handleLogin}>
          <div className="input-group">
            <label className="input-label" htmlFor="email">E-mail</label>
            <input
              id="email"
              type="email"
              className="input-field"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="seu@email.com"
              required
            />
          </div>

          <div className="input-group">
            <label className="input-label" htmlFor="password">Senha</label>
            <input
              id="password"
              type="password"
              className="input-field"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          <button type="submit" className={`btn btn-primary w-full mt-4`} disabled={loading}>
            {loading ? "🔑 Entrando..." : "🔓 Entrar"}
          </button>
        </form>

        <p className="text-center mt-6 text-sm">
          Ainda não tem conta? <Link href="/register" className={styles.registerLink}>Cadastre-se</Link>
        </p>
      </div>
    </div>
  );
}
