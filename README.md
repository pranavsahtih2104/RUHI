# RUHI — Personal AI System

A futuristic personal AI system that understands intent, remembers context, reasons through complex tasks, and helps you get things done.

---

## 🚀 Quick Start

### 1. Start the Frontend Website
```bash
cd Ruhi-web
npm run dev
```
👉 Open **[http://localhost:5173](http://localhost:5173)** in your browser for the full interactive website.

### 2. Start the Backend API (in a separate terminal)
```bash
cd Ruhi-web
source ../.venv/bin/activate
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
👉 Backend API Docs are at **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**.