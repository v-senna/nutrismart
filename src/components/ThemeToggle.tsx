"use client";
import { useEffect, useState } from "react";
import { Sun, Moon } from "lucide-react";

interface ThemeToggleProps {
  inline?: boolean;
}

export default function ThemeToggle({ inline }: ThemeToggleProps) {
  const [dark, setDark] = useState<boolean>(() => {
    if (typeof window === "undefined") return true;
    const saved = localStorage.getItem("theme");
    return saved ? saved === "dark" : true;
  });

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", dark ? "dark" : "light");
  }, [dark]);

  const toggle = () => {
    const next = !dark;
    setDark(next);
    document.documentElement.setAttribute("data-theme", next ? "dark" : "light");
    localStorage.setItem("theme", next ? "dark" : "light");
  };

  if (inline) {
    return (
      <button
        onClick={toggle}
        title={dark ? "Ativar Modo Claro" : "Ativar Modo Escuro"}
        style={{
          background: "var(--card-bg)",
          border: "1px solid var(--card-border)",
          color: "var(--primary)",
          borderRadius: "10px",
          padding: "0.4rem",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          cursor: "pointer",
          transition: "all 0.2s",
          boxShadow: "0 2px 10px rgba(0, 0, 0, 0.1)",
          flexShrink: 0,
        }}
        onMouseEnter={e => (e.currentTarget.style.transform = "scale(1.05)")}
        onMouseLeave={e => (e.currentTarget.style.transform = "scale(1)")}
      >
        {dark ? <Sun size={20} /> : <Moon size={20} />}
      </button>
    );
  }

  return (
    <button
      onClick={toggle}
      title={dark ? "Ativar Modo Claro" : "Ativar Modo Escuro"}
      style={{
        position: "fixed",
        bottom: "1.5rem",
        right: "1.5rem",
        zIndex: 9999,
        width: "48px",
        height: "48px",
        borderRadius: "50%",
        border: "2px solid var(--primary)",
        background: "var(--card-bg)",
        color: "var(--primary)",
        fontSize: "1.4rem",
        cursor: "pointer",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        boxShadow: "0 0 18px var(--primary)",
        transition: "all 0.3s ease",
        backdropFilter: "blur(10px)",
      }}
      onMouseEnter={e => (e.currentTarget.style.transform = "scale(1.15)")}
      onMouseLeave={e => (e.currentTarget.style.transform = "scale(1)")}
    >
      {dark ? <Sun size={24} /> : <Moon size={24} />}
    </button>
  );
}
