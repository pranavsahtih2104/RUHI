# RUHI — Personal AI System

> **An AI that grows with you.**  
> A futuristic personal AI system that understands intent, remembers context, reasons through complex tasks, and coordinates actions across your digital life.

---

## 🌌 Overview

**RUHI** is not another generic ChatGPT clone. Traditional AI functions as an isolated single-turn chatbot: you open a tab, ask a question, copy text, and do all the actual work manually.

RUHI is architected as an **intelligent layer** between you and your digital environment:

```text
Traditional AI:
User ──► Question ──► AI ──► Static Text Answer

RUHI Personal AI:
User ──► Intent ──► RUHI Understands ──► Context/Memory ──► Reasoning ──► Tools ──► Guarded Actions ──► Result
```

---

## 🏛️ Project Architecture

The web codebase is structured with clear separation between the presentation tier, backend API gateway, and decoupled AI orchestrators:

```text
Ruhi-web/
├── backend/                        # FastAPI AI Backend Service
│   ├── config/
│   │   └── settings.py             # Environment variables & model configuration
│   ├── models/
│   │   └── schemas.py              # Pydantic data schemas (Chat, Health, Memory)
│   ├── services/
│   │   ├── llm/
│   │   │   ├── base.py             # Abstract BaseLLMService interface (provider decoupling)
│   │   │   └── gemini_service.py   # Gemini 2.5 Flash implementation & system persona
│   │   ├── memory/
│   │   │   └── session_memory.py   # Active sliding-window session manager
│   │   └── tools/
│   │       └── registry.py         # Extensible tool registry for desktop execution
│   ├── main.py                     # FastAPI application endpoints
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                       # Vite + React Modern Web Application
│   ├── src/
│   │   ├── assets/                 # Brand emblems, vector icons
│   │   ├── components/
│   │   │   ├── Navbar.jsx          # Glassmorphic floating navigation
│   │   │   ├── Hero.jsx            # Cinematic hero with dynamic canvas orb
│   │   │   ├── RuhiCoreOrb.jsx     # Interactive multi-layered canvas particle core
│   │   │   ├── WhatIsRuhi.jsx      # Interactive 3-branch system architecture
│   │   │   ├── WhyRuhi.jsx         # Paradigm comparison (Tool vs Personal System)
│   │   │   ├── Capabilities.jsx    # Categorized capabilities with status badges
│   │   │   ├── HowItWorks.jsx      # Interactive 9-stage cognitive pipeline
│   │   │   ├── Personality.jsx     # Ethos & demeanor principles
│   │   │   ├── TryRuhiChat.jsx     # Signature chat console with Gemini integration
│   │   │   ├── MemoryConcept.jsx   # Short-term context vs Long-term memory visualizer
│   │   │   ├── DesktopRuhi.jsx     # Installed desktop workflow simulation & permissions
│   │   │   ├── ComparisonMatrix.jsx# Web vs Desktop capability breakdown
│   │   │   ├── PrivacySecurity.jsx # Zero-compromise security posture & controls
│   │   │   ├── InstallModal.jsx    # Desktop installer modal & permission setup
│   │   │   └── Footer.jsx          # Brand identity, links, and copyright
│   │   ├── services/
│   │   │   └── api.js              # REST client for backend communication
│   │   ├── styles/
│   │   │   ├── index.css           # Design tokens, typography, dark space palette
│   │   │   ├── components.css      # Component cards, glassmorphism, animations
│   │   │   └── chat.css            # RUHI console aesthetics & markdown styling
│   │   ├── App.jsx                 # Master application layout
│   │   └── main.jsx
│   ├── index.html                  # SEO tags & Google Fonts (Outfit, Space Grotesk, Inter)
│   ├── package.json
│   └── vite.config.js
│
├── docs/
│   └── ARCHITECTURE.md             # Deep architectural design document
└── README.md
```

---

## ⚡ Key Features

1. **Cinematic Futuristic Aesthetics**:
   - Deep space palette (`#05070c`, `#080b12`, `#00f2fe`, `#7928ca`)
   - Custom dynamic HTML5 Canvas particle & energy core (`RuhiCoreOrb`)
   - Frosted glassmorphism with subtle ambient glows
   - High-contrast accessible typography (Outfit, Space Grotesk, Inter, Fira Code)

2. **Live AI Chat Experience**:
   - Direct connection to Google Gemini 2.5 Flash via FastAPI backend
   - Multi-turn conversation context retention within active session
   - Clean markdown parsing, lists, and code blocks with one-click copy
   - Calm, non-fabricated thinking indicator wave
   - Context reset action and suggestion chips for first-time discovery

3. **Transparent Capability Matrix**:
   - Clear badges for **Available now**, **Coming soon**, and **Desktop-only**
   - No fabricated capabilities or misleading claims

4. **Desktop Simulation & Permission Engine**:
   - Interactive local workflow demonstrations (Project launch, file search, build pipelines)
   - Granular permission control toggles (Files, Apps, Mic, Automation)

5. **Decoupled AI Engine**:
   - Abstract `BaseLLMService` ensures RUHI can seamlessly switch between Gemini, Claude, GPT-4o, or local Ollama weights without rewriting core system logic.

---

## 🚀 Quick Start Guide

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)
- Google Gemini API Key

### 1. Configure Environment Variables
Create a `.env` file in `Ruhi-web/backend/` or project root:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
MAX_SESSION_HISTORY=30
```

### 2. Start the Backend API Server
```bash
# From workspace root
source .venv/bin/activate
cd Ruhi-web
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
Backend API will be live at: `http://127.0.0.1:8000` (Docs at `/docs`)

### 3. Start the Frontend Development Server
In a separate terminal:
```bash
cd Ruhi-web/frontend
npm run dev
```
Frontend will be live at: `http://localhost:5173`

---

## 🔒 Security & Privacy Posture

- **Zero Secret Leakage**: API keys and tokens reside exclusively on the server side.
- **Explicit Authorization**: Desktop capabilities operate under a sandbox model with required user permissions.
- **Session Purging**: Users can reset session context at any time.

---

## 🗺️ Roadmap & Next Steps

- [x] Stage 1: Landing page + cinematic branding
- [x] Stage 2: Interactive RUHI architecture & 9-stage pipeline
- [x] Stage 3: Live web chat console with session memory
- [x] Stage 4: Backend AI integration with Gemini 2.5 Flash & provider abstraction
- [x] Stage 5: Desktop simulation & permission engine
- [ ] Stage 6: Electron / Tauri desktop runtime wrapper
- [ ] Stage 7: Local SQLite / Chroma vector memory store
- [ ] Stage 8: Local voice activation daemon
