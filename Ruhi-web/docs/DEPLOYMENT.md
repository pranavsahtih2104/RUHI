# RUHI Full-Stack Deployment Guide

This guide walks you through deploying **RUHI** to production for free in just a few minutes using **Vercel** (for the frontend) and **Render.com** or **Railway** (for the FastAPI Python backend).

---

## 🏗️ Architecture Overview

```text
User Browser ──► Vercel (React Frontend: https://ruhi.vercel.app)
                      │
                      ▼ (REST API /api/chat)
                 Render / Railway (FastAPI Backend: https://ruhi-api.onrender.com)
                      │
                      ▼
                 Google Gemini 2.5 Flash API
```

---

## Step 1: Deploy the Backend (Render.com / Railway)

### Option A: Render.com (Recommended Free Hosting)
1. Go to [dashboard.render.com](https://dashboard.render.com) and sign in with GitHub.
2. Click **New +** ➔ **Web Service**.
3. Select your repository: `pranavsahtih2104/RUHI`.
4. Fill in the settings:
   - **Name**: `ruhi-backend`
   - **Region**: Closest to you (e.g., Oregon, Frankfurt, Singapore)
   - **Root Directory**: `Ruhi-web`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`
5. Under **Environment Variables**, add:
   - `GEMINI_API_KEY`: *(Paste your real Gemini API key)*
   - `GEMINI_MODEL`: `gemini-2.5-flash`
6. Click **Create Web Service**.
7. Once deployed, copy your backend URL (e.g., `https://ruhi-backend.onrender.com`).

---

### Option B: Railway.app
1. Go to [railway.app](https://railway.app) and sign in with GitHub.
2. Click **New Project** ➔ **Deploy from GitHub repo** ➔ Select `pranavsahtih2104/RUHI`.
3. In service settings, set **Root Directory** to `Ruhi-web` and **Custom Start Command** to:
   `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. Add variable: `GEMINI_API_KEY` = your key.
5. Generate a public domain under **Settings ➔ Networking**.

---

## Step 2: Deploy the Frontend on Vercel

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub.
2. Click **Add New...** ➔ **Project**.
3. Import your repository: `pranavsahtih2104/RUHI`.
4. In the configuration screen:
   - **Framework Preset**: `Vite` (automatically detected)
   - **Root Directory**: Leave as `./` (the included `vercel.json` will automatically build `Ruhi-web/frontend`).
   - Or click *Edit* next to Root Directory and choose `Ruhi-web/frontend`.
5. Under **Environment Variables**, add:
   - **Key**: `VITE_API_URL`
   - **Value**: Your backend URL from Step 1 (e.g., `https://ruhi-backend.onrender.com`)
6. Click **Deploy**.

Vercel will build and deploy your site in ~30 seconds, giving you a live URL like `https://ruhi-personal-ai.vercel.app`!

---

## Step 3: Verify Your Production Deployment

1. Visit your Vercel URL in your browser.
2. Check the hero section and click **Try RUHI**.
3. Send a message in the chat console or use a suggestion chip.
4. Verify the connection indicator displays `Connected // gemini-2.5-flash`.
5. Test the **Voice Input** button.

---

## 🔒 Security Checklist for Production
- [x] API keys reside solely in Render/Railway environment variables (never in frontend code or git).
- [x] CORS is enabled for Vercel domains.
- [x] SPA rewrites handle client-side routing.
