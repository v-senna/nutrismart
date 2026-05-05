"use client";

import { useState } from "react";
import { fetchApi } from "@/lib/api";
import { Upload, X, FileText, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import styles from "./ImportDietModal.module.css";

interface ImportDietModalProps {
  onClose: () => void;
  onImportSuccess: (data: any) => void;
}

export default function ImportDietModal({ onClose, onImportSuccess }: ImportDietModalProps) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<any>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError("");
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError("");

    const formData = new FormData();
    formData.append("file", file);

    const token = localStorage.getItem("token");

    try {
      const response = await fetch("/api/import-diet", { // Note: using direct fetch because fetchApi might not handle FormData well if not configured
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Erro ao importar arquivo");
      }

      const data = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const confirmImport = () => {
    onImportSuccess(result);
    onClose();
  };

  return (
    <div className={styles.overlay}>
      <div className={`glass-card ${styles.modal}`}>
        <button className={styles.closeBtn} onClick={onClose}><X size={24} /></button>
        
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2 text-primary">
          <Upload size={24} /> Importar Dieta Existente
        </h2>

        {!result ? (
          <>
            <p className="text-sm text-muted mb-6">
              Envie um PDF ou Excel da sua dieta atual. Nossa IA vai extrair as informações para você não precisar digitar tudo.
            </p>

            <div className={styles.uploadZone}>
              <input type="file" id="diet-file" hidden accept=".pdf,.xlsx,.xls" onChange={handleFileChange} />
              <label htmlFor="diet-file" className={styles.fileLabel}>
                <FileText size={48} className={file ? "text-primary" : "text-muted"} />
                <span>{file ? file.name : "Clique para selecionar ou arraste o arquivo"}</span>
                <small>PDF, XLSX ou XLS (Max 5MB)</small>
              </label>
            </div>

            {error && <div className="text-red-500 text-sm mt-4 flex items-center gap-2"><AlertCircle size={16} /> {error}</div>}

            <button 
              className="btn btn-primary w-full mt-6 flex items-center justify-center gap-2"
              onClick={handleUpload}
              disabled={!file || loading}
            >
              {loading ? <><Loader2 className="animate-spin" size={20} /> Processando...</> : "Analisar Documento"}
            </button>
          </>
        ) : (
          <div className="fade-in">
            <div className="bg-primary/10 p-4 rounded-xl mb-6 border border-primary/20">
              <h3 className="font-bold flex items-center gap-2 text-primary mb-2">
                <CheckCircle size={18} /> Análise Concluída!
              </h3>
              <p className="text-sm">Encontramos as seguintes informações:</p>
              
              <ul className={styles.extractedList}>
                <li><strong>Idade:</strong> {result.profile.age || <span className="text-red-400">Não encontrado</span>}</li>
                <li><strong>Peso:</strong> {result.profile.weight ? `${result.profile.weight}kg` : <span className="text-red-400">Não encontrado</span>}</li>
                <li><strong>Meta:</strong> {result.profile.goals || <span className="text-red-400">Não encontrado</span>}</li>
                <li><strong>Refeições:</strong> {result.meals.length} detectadas</li>
              </ul>
            </div>

            <p className="text-sm text-muted mb-6">
              Os campos não encontrados ficarão em branco para você preencher manualmente no formulário.
            </p>

            <button 
              className="btn btn-primary w-full flex items-center justify-center gap-2"
              onClick={confirmImport}
            >
              Confirmar e Preencher Formulário
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
