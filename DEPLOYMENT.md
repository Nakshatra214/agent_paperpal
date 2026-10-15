# Agent Paperpal — Deployment Guide

This guide covers deploying the **Agent Paperpal** application to production using:
- **Render** for the Python FastAPI backend
- **Vercel** for the React + Vite frontend
- **GitHub** for source code hosting

---

## 1. Environment Variables Overview

### Backend (Render & Local `.env`)

| Variable | Required | Secret? | Default Value | Description |
|---|---|---|---|---|
| `GEMINI_API_KEY` | **Yes** | **Yes** | — | Google Gemini API Key (from Google AI Studio). |
| `GOOGLE_API_KEY` | Optional | **Yes** | — | Alias for LiteLLM (automatically mapped from `GEMINI_API_KEY` if omitted). |
| `CORS_ORIGINS` | **Yes** (Prod) | No | `http://localhost:5173,http://localhost:3000` | Comma-separated list of allowed origins (e.g. `https://your-frontend.vercel.app,http://localhost:5173`). |
| `PORT` | Auto (Render) | No | `8000` | Injected automatically by Render. Application binds dynamically to `${PORT:-8000}`. |
| `GEMINI_MODEL` | Optional | No | `gemini-3.6-flash` | Gemini model for CrewAI pipeline and rule extraction. |
| `GEMINI_MAX_TOKENS` | Optional | No | `65536` | Max tokens per LLM completion (handles large manuscript JSON). |
| `GEMINI_THINKING_BUDGET` | Optional | No | `2048` | Thinking token budget (minimal reasoning effort to control token consumption; 0 disables). |
| `LLM_TIMEOUT` | Optional | No | `300` | Per-call timeout in seconds for agent calls. |
| `LLM_MAX_RETRIES` | Optional | No | `2` | Maximum retry attempts for failed LLM calls. |

### Frontend (Vercel & Local `.env`)

| Variable | Required | Secret? | Default Value | Description |
|---|---|---|---|---|
| `VITE_BACKEND_URL` | **Yes** (Prod) | No | `http://localhost:8000` | Base URL of deployed Render backend (e.g. `https://ppal-backend.onrender.com`). Trailing slashes are stripped automatically. |
| `VITE_PORT` | Optional | No | `5173` | Local Vite dev server port. |

> [!CAUTION]
> Never set `GEMINI_API_KEY` in frontend environment variables or client-side code. Only the backend communicates with the Gemini API.

---

## 2. Local Development Setup

### 2.1 Backend Local Setup

1. Open a terminal and navigate to `backend/`:
   ```bash
   cd backend
   python -m venv .venv
   ```
2. Activate the virtual environment:
   - **Windows (PowerShell):** `.\.venv\Scripts\Activate.ps1`
   - **macOS / Linux:** `source .venv/bin/activate`
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment:
   ```bash
   cp .env.example .env
   ```
   Edit `backend/.env` and replace `YOUR_GEMINI_API_KEY` with your actual Google AI Studio key.
5. Run the local backend:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   Verify at: `http://localhost:8000/health`

### 2.2 Frontend Local Setup

1. Open a separate terminal and navigate to `frontend/`:
   ```bash
   cd frontend
   npm install
   ```
2. (Optional) Create local `.env`:
   ```bash
   cp .env.example .env
   ```
3. Start the Vite dev server:
   ```bash
   npm run dev
   ```
   Open `http://localhost:5173` in your browser.

---

## 3. Render Deployment (FastAPI Backend)

The project includes both a `render.yaml` blueprint and a production-ready `backend/Dockerfile`. Docker deployment is recommended to ensure consistent Python 3.11 runtime and system libraries.

### Option A: Blueprint Deployment via `render.yaml` (Recommended)

1. Connect your GitHub repository to Render.
2. In the Render Dashboard, select **New +** > **Blueprint**.
3. Select your repository. Render will detect `render.yaml`.
4. In the service setup, configure the required environment variables:
   - `GEMINI_API_KEY`: Enter your Google AI Studio API key.
   - `CORS_ORIGINS`: Set to your Vercel URL (e.g., `https://your-frontend.vercel.app,http://localhost:5173`).
5. Click **Apply**.

### Option B: Manual Web Service Deployment

1. In Render Dashboard, click **New +** > **Web Service**.
2. Select your repository.
3. Configure the service settings:
   - **Name:** `ppal-backend` (or your choice)
   - **Region:** Ohio (US East) or closest to your users
   - **Root Directory:** `backend`
   - **Environment:**
     - **If using Docker (Recommended):**
       - Environment: `Docker`
       - Dockerfile Path: `Dockerfile`
       - Docker Context: `.` (relative to root directory `backend`)
     - **If using Native Python:**
       - Environment: `Python 3`
       - Build Command: `pip install -r requirements.txt`
       - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add Environment Variables under the **Environment** tab:
   - `GEMINI_API_KEY` = `YOUR_GEMINI_API_KEY` (Mark as Secret)
   - `CORS_ORIGINS` = `https://your-frontend.vercel.app,http://localhost:5173`
   - `GEMINI_MODEL` = `gemini-3.6-flash`
   - `GEMINI_MAX_TOKENS` = `65536`
   - `GEMINI_THINKING_BUDGET` = `2048`
   - `LLM_TIMEOUT` = `300`
   - `LLM_MAX_RETRIES` = `2`
5. Click **Deploy Web Service**.
6. Once deployed, copy your Render service URL (e.g., `https://ppal-backend.onrender.com`).

---

## 4. Vercel Deployment (React + Vite Frontend)

The root repository contains `vercel.json` configured for Vite single-page applications.

### Deployment Steps:

1. Log in to [Vercel](https://vercel.com) and click **Add New...** > **Project**.
2. Import your GitHub repository (`agent-paperpal`).
3. Configure project settings:
   - **Framework Preset:** `Vite`
   - **Root Directory:** Edit and select `frontend` (or leave at `./` since `vercel.json` orchestrates build from root).
     - *If Root Directory is set to `frontend`:*
       - Build Command: `npm run build`
       - Output Directory: `dist`
       - Install Command: `npm install`
     - *If Root Directory is left at `./` (Root):*
       - `vercel.json` handles the build command (`cd frontend && npm install && npm run build`) and output directory (`frontend/dist`).
4. Set Environment Variables:
   - Name: `VITE_BACKEND_URL`
   - Value: `https://your-backend.onrender.com` (replace with your actual Render URL, without trailing slash)
   - Target Environments: Production, Preview, Development
5. Click **Deploy**.
6. Copy your production Vercel domain (e.g. `https://your-frontend.vercel.app`).
7. Return to Render and ensure `CORS_ORIGINS` includes your Vercel domain!

---

## 5. CORS Setup & Production Domain Sync

For security and browser compatibility:
1. When your Vercel deployment completes, note the domain: `https://<your-project>.vercel.app`.
2. Update `CORS_ORIGINS` in your Render Web Service Environment settings:
   ```text
   https://<your-project>.vercel.app,http://localhost:5173
   ```
3. Trigger a redeploy in Render or save changes so the new origin is active.
4. FastAPI validates that preflight (`OPTIONS`) and credentials requests from that domain are authorized.

---

## 6. Post-Deployment Verification

### Step 1: Verify Backend Health

Run from terminal or browser:
```bash
curl -i https://your-backend.onrender.com/health
```

Expected response (`HTTP 200 OK`):
```json
{
  "status": "ok",
  "version": "2.0.0",
  "service": "Agent Paperpal",
  "supported_journals": ["nature", "ieee", "springer", "apa", "acm", ...],
  "max_file_size_mb": 10,
  "supported_modes": ["standard", "semi_custom", "full_custom"],
  "system_info": { ... },
  "diagnostics": {
    "rules_folder_exists": true,
    "outputs_folder_writable": true,
    "active_docs": 0,
    "active_jobs": 0
  }
}
```

### Step 2: Verify Frontend

1. Open your Vercel URL in a browser: `https://your-frontend.vercel.app`.
2. Open Browser Developer Tools (`F12` > Console & Network tabs).
3. Ensure there are no CORS errors or connection errors.
4. Upload a test manuscript (`.docx` or `.pdf`).
5. Run the formatting pipeline.
6. Verify live progress indicators update and the transformed DOCX download works.

---

## 7. Common Deployment Issues & Troubleshooting

| Issue | Cause | Solution |
|---|---|---|
| **CORS Error: No 'Access-Control-Allow-Origin' header** | `CORS_ORIGINS` on Render does not match your Vercel domain. | Add exact Vercel URL (e.g., `https://your-app.vercel.app`) to Render `CORS_ORIGINS`. Do not include a trailing slash. |
| **API requests fail with 404 or connection refused** | `VITE_BACKEND_URL` is empty, incorrect, or pointing to `localhost`. | Set `VITE_BACKEND_URL=https://your-backend.onrender.com` in Vercel settings and trigger a **Redeploy** (environment variables in Vite are baked in at build time). |
| **Backend 500 error on pipeline start** | `GEMINI_API_KEY` is not set or invalid. | Verify `GEMINI_API_KEY` is saved in Render environment variables and is active in Google AI Studio. |
| **Render Web Service slow to respond initially** | Render Free Tier spins down web services after 15 minutes of inactivity. | First request after sleep may take 30–60 seconds for cold start. Subsequent requests respond immediately. |
| **Render build fails on Python version** | Render default native Python version mismatch with dependencies. | Use the Docker environment via `render.yaml` or set Docker runtime in Render dashboard. |
| **`rebuild-docx` fails or download times out** | Large manuscript processing exceeding request timeout. | Ensure `LLM_TIMEOUT=300` is configured on Render. |
