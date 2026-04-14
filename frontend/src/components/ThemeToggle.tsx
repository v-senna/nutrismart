"use client";
import { useEffect, useState } from "react";

export default function ThemeToggle() {
  const [dark, setDark] = useState(true);

  useEffect(() => {
    const saved = localStorage.getItem("theme");
    const isDark = saved ? saved === "dark" : true;
    setDark(isDark);
    document.documentElement.setAttribute("data-theme", isDark ? "dark" : "light");
  }, []);

  const toggle = () => {
    const next = !dark;
    setDark(next);
    document.documentElement.setAttribute("data-theme", next ? "dark" : "light");
    localStorage.setItem("theme", next ? "dark" : "light");
  };

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
      {dark ? "☀️" : "🌙"}
    </button>
  );
}
