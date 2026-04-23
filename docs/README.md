# NutriSmart 🍎

NutriSmart é uma aplicação completa de inteligência nutricional que gera planos alimentares personalizados, cálculos metabólicos e permite o acompanhamento contínuo do seu progresso em direção aos seus objetivos (emagrecimento, hipertrofia ou manutenção).

## 🚀 O que o projeto faz?

A plataforma NutriSmart permite:
- **Onboarding e Perfil de Saúde**: Coleta os dados físicos e objetivos do usuário, calculando Taxa Metabólica Basal (TMB), Gasto Diário (TDEE) e Índice de Massa Corporal (IMC) com base em diretrizes de saúde referenciadas (OMS, HAS).
- **Geração Inteligente de Plano**: Usa um algoritmo ("Engine" nutricional) para criar um plano focado em emagrecimento, hipertrofia ou manutenção de peso, garantindo a divisão exata de macronutrientes.
- **Cardápio e Trocas Inteligentes**: Oferece sugestões de cardápios com horários baseados na rotina do usuário e uma função de "Ver Trocas", permitindo substituições nutritivas com flexibilidade.
- **Dashboard e Evolução**: Exibe um gráfico que cruza métricas ideais com os pesos reais que o usuário registra com o passar do tempo.
- **Alertas de Saúde e Dicas Diárias**: Gera dicas dinâmicas no painel, inclusive considerando riscos à saúde baseados no tempo em que a pessoa passa sem comer ou na classificação crítica de seu IMC.

## 🛠️ Tecnologias Utilizadas

- **Frontend**: Next.js (React), TypeScript, Recharts (para gráficos), CSS puro com Glassmorphism design pattern.
- **Backend**: FastAPI (Python), uvicorn, SQLAlchemy com banco de dados SQLite.
- **Arquitetura**: Sistema modular, onde o backend gerencia a API REST e a lógica nutricional e o frontend gerencia o UI dinâmico.

---

## 💻 Como instalar e rodar localmente

### 1. Requisitos
- [Node.js](https://nodejs.org/en/) (Versão 18+ recomendada)
- [Python](https://www.python.org/downloads/) (Versão 3.9+ recomendada)
- Git

### 2. Clonando o Repositório
```bash
git clone https://github.com/v-senna/nutrismart.git
cd nutrismart
```

### 3. Executando o Backend (API)
Abra uma janela de terminal / prompt de comando.

```bash
# Entre na pasta do backend
cd backend

# Crie e ative um ambiente virtual (Windows)
python -m venv venv
venv\Scripts\activate

# Para Mac/Linux use:
# python3 -m venv venv
# source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Inicie o servidor FastAPI local
uvicorn main:app --reload --port 8001
```
Isso iniciará o back-end na URL: `http://localhost:8001`.

### 4. Executando o Frontend (Web App)
Abra **outra** janela de terminal, deixando o servidor do backend rodando na primeira.

```bash
# Entre na pasta do projeto e depois na pasta frontend
cd nutrismart/frontend

# Instale os pacotes npm
npm install

# Inicie o servidor de desenvolvimento
npm run dev
```
O frontend começará a rodar e você poderá acessar a aplicação em: `http://localhost:3001`.

---
Feito com 💚 para quem busca mais inteligência na nutrição.
