// URL direta do backend FastAPI
// CORS está configurado no backend para aceitar localhost:3000
export const API_URL = "/api";

export const fetchApi = async (endpoint: string, options: RequestInit = {}) => {
  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  let response: Response;
  try {
    response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers,
    });
  } catch (networkErr) {
    throw new Error(
      "Não foi possível conectar ao servidor. Verifique se o backend está rodando (porta 8001)."
    );
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Erro ${response.status}: ${response.statusText}`);
  }

  return response.json();
};
