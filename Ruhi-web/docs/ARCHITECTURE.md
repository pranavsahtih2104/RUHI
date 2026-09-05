# RUHI System Architecture & Design Decisions

This document details the architectural decisions, design patterns, and engineering rationale behind the **RUHI Personal AI System**.

---

## 1. Core Architectural Philosophy

RUHI is designed as an **AI System built around an LLM**, rather than simply an LLM wrapper.

```text
               ┌─────────────────────────────────────────┐
               │            RUHI Personal AI             │
               └────────────────────┬────────────────────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          │                         │                         │
          ▼                         ▼                         ▼
┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│     Cognitive     │     │    Continuity     │     │     Execution     │
│  Reasoning Layer  │     │   Memory Layer    │     │    Tools Layer    │
└─────────┬─────────┘     └─────────┬─────────┘     └─────────┬─────────┘
          │                         │                         │
          ▼                         ▼                         ▼
   LLM Abstraction          Session / Vector DB       Sandboxed Registry
  (Gemini, Claude,...)      (Sliding + Long Term)     (Files, Apps, Shell)
```

### Key Principles:
1. **Provider Agnosticism**: The cognitive layer does not depend on proprietary LLM idiosyncrasies. An abstract base service (`BaseLLMService`) normalizes input formats, system prompts, and responses.
2. **Context Continuity**: Memory is structured as multi-tiered storage — short-term sliding conversational history for rapid in-session inference, and future long-term vector/relational databases for personal guidelines.
3. **Execution Guardrails**: The tool registry decouples action declarations from execution. On the web, tools return structured plans and metadata; on the desktop runtime, actions run only after explicit permission checks.

---

## 2. Decoupled AI Interface

Located in `backend/services/llm/`:
- `base.py`: Declares `generate_response(history, new_message, system_instruction)` and provider metadata methods.
- `gemini_service.py`: Implements the Gemini 2.5 Flash / 2.0 integration using the official `google-genai` SDK.

If a developer wants to add Anthropic Claude or a local Ollama model, they simply implement a new class extending `BaseLLMService` without touching any API routing or frontend code.

---

## 3. Session & Memory Strategy

Located in `backend/services/memory/session_memory.py`:
- Each client maintains a unique session identifier (`ruhi_sess_*`).
- Conversation turns are tracked in a sliding window (default: 30 turns) with automatic background expiration for idle sessions.
- Clear hooks are provided for future persistence:
  ```python
  # Future persistent memory interface:
  # def persist_memory_fact(user_id, fact_text, embedding)
  # def retrieve_relevant_context(user_id, query_embedding, top_k=5)
  ```

---

## 4. Safety & The Permission Engine

In desktop environments, personal AI systems must not possess silent, unrestricted OS access.
RUHI's permission architecture implements:
- **Explicit Scoping**: File access is restricted to user-whitelisted folders.
- **Auditable Telemetry**: All spawned processes log command line arguments, PIDs, and exit codes.
- **Instant Revocation**: Permission toggles dynamically disable tool execution at runtime.
