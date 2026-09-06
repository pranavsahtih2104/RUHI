# RUHI — Stage 2: Persistent Memory & PostgreSQL

> **An AI that grows with you.**  
> A personal AI system that understands intent, maintains context, reasons through complex challenges, and retains persistent memories across sessions.

---

## 🌌 1. What is RUHI?

**RUHI** is a personal AI system — not simply a chatbot or a wrapper around a single foundation model.

Traditional chatbots function as isolated, single-turn query boxes where context is lost as soon as the session ends.

RUHI is designed as an **intelligent cognitive layer** between you and your digital environment:

```text
                         RUHI
                          │
                     RUHI CORE
                          │
             ┌────────────┴────────────┐
             │                         │
        Conversation              Memory System
          Context                      │
                                      │
                         ┌────────────┴────────────┐
                         │                         │
                  Short-Term Memory        Long-Term Memory
                         │                         │
                    Current chat          Persistent storage
                    (PostgreSQL)             (PostgreSQL)
```

---

## 🏛️ 2. Architecture (Stage 2: Persistent Memory)

```text
                         RUHI WEB (React / Vite)
                                    │
            ┌───────────────────────┴───────────────────────┐
            ▼                                               ▼
   Chat History Sidebar                            Memory Management UI
 (Persistent Conversations)                       (Search, Edit, Delete)
            │                                               │
            └───────────────────────┬───────────────────────┘
                                    ▼
                          FastAPI REST / SSE API
                                    │
                                RUHI CORE
                                    │
      ┌─────────────────────────────┼─────────────────────────────┐
      ▼                             ▼                             ▼
Context Manager               Memory Service                LLM Service
(Sliding window + memory) (Explicit / Conservative extract) (BaseLLMProvider)
      │                             │                             │
      │                     Memory Repository                     │
      │                             │                             │
      └─────────────────────────────┼─────────────────────────────┘
                                    ▼
                         PostgreSQL (`ruhi-web`)
                             ┌──────┴──────┐
                             │             │
                       conversations    memories
                             │        (pgvector ready)
                          messages
```

---

## 🗄️ 3. PostgreSQL Database Schema

RUHI connects to your existing local PostgreSQL database (`ruhi-web`) on `localhost:5432`:

```text
PostgreSQL (ruhi-web)
├── users (id, email, name, created_at, updated_at)
├── conversations (id, user_id, title, created_at, updated_at)
├── messages (id, conversation_id, role, content, metadata_json, created_at)
└── memories (id, user_id, content, memory_type, importance, source, is_active, metadata_json, created_at, updated_at)
```

### Memory Types:
- `preference`: Enduring user preferences (e.g., *"I prefer dark mode and concise code"*)
- `project`: Project architectural knowledge (e.g., *"RUHI is my personal AI project"*)
- `goal`: Strategic objectives (e.g., *"My goal is to build an autonomous agent"*)
- `fact`: Static facts (e.g., *"My name is Pranav"*)
- `instruction`: Ongoing behavioral rules (e.g., *"Always format SQL in uppercase"*)
- `general`: Uncategorized persistent facts

---

## 🧠 4. How RUHI Memory Works

1. **Explicit Memory Commands**:
   - `"Remember that RUHI is my personal AI project."` -> RUHI stores the memory with high importance (8-10) and confirms: *"I'll remember that: RUHI is my personal AI project."*
   - `"Forget that I want desktop control."` -> RUHI soft-deletes/deactivates the matching memory.
   - `"What do you remember about me?"` -> RUHI queries and lists active persistent memories.

2. **Conservative Automatic Extraction**:
   - RUHI analyzes incoming conversational turns for strong enduring intent without saving ephemeral chatter (e.g., *"I drank coffee today"* is ignored).

3. **Selective Context Retrieval (No Dumping)**:
   - RUHI extracts query keywords and retrieves only the top 3-4 most relevant active memories.
   - Memories are formatted into system context (`[Active Persistent Context & Memories]`) for the LLM.

4. **Persistent Conversation Sessions**:
   - Every conversation and message is committed to PostgreSQL.
   - Conversations persist across backend restarts and browser refreshes.

---

## ⚙️ 5. Setup & Environment Configuration

### Prerequisites:
- PostgreSQL running locally on port `5432` with database `ruhi-web`
- Python 3.10+
- Node.js 18+

### Environment Variables (`.env`):
Create or update `.env` in the project root:

```env
# 1. PostgreSQL Connection
DATABASE_URL=postgresql://USERNAME:PASSWORD@localhost:5432/ruhi-web
DEFAULT_USER_ID=default_user

# 2. Intelligence Provider
RUHI_LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
GEMINI_FALLBACK_MODEL=gemini-2.0-flash

# 3. Memory & Context
MAX_SESSION_HISTORY=30
SESSION_EXPIRY_MINUTES=120

# 4. Frontend API
VITE_API_URL=http://127.0.0.1:8000/api
```

---

## 🚀 6. Running Migrations & Starting RUHI

### 1. Run Alembic Database Migrations:
```bash
# From project root:
alembic -c backend/alembic.ini upgrade head
```

### 2. Start the FastAPI Backend:
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Start the Frontend:
```bash
cd frontend
npm run dev
```
Open **http://localhost:5173** in your browser.

---

## 🧪 7. Running Tests

Run the full automated test suite (22 unit & integration tests):

```bash
python3 -m unittest discover -s backend/tests
```

---

## 🗺️ 8. Stage Progression & Roadmap

```text
CURRENT
RUHI Web v1
     ↓
THIS STAGE (COMPLETED)
Persistent Memory & PostgreSQL
     ↓
NEXT
Knowledge / RAG
     ↓
THEN
Real Desktop Tools
     ↓
THEN
Reasoning & Autonomous Planning
     ↓
THEN
RUHI Desktop & OS Automation
     ↓
THEN
Local Models & Custom RUHI Weights
```
