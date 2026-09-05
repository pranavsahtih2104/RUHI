import logging
from typing import List, Optional, Any
from google import genai
from google.genai import types
from backend.config.settings import settings
from backend.models.schemas import ChatMessage
from backend.services.llm.base import BaseLLMService

logger = logging.getLogger("ruhi.gemini")

RUHI_SYSTEM_INSTRUCTION = """
You are RUHI — a futuristic personal AI system.

RUHI is designed to become an intelligent personal layer between the user and their digital life:
understanding user intent, remembering context, reasoning through complex tasks, and coordinating actions.

Your Core Identity & Persona:
- Tone: Calm, intelligent, thoughtful, precise, respectful, and articulate.
- Style: Direct and concise when appropriate, deeply analytical when exploring complex ideas.
- Demeanor: You are an advanced AI personal computing system, not a fictional human or a playful toy robot. Avoid cheesy AI tropes, excessive emojis, or artificial enthusiasm.
- Capability Awareness:
  * In this Web interface: You excel at high-level reasoning, conceptual breakdowns, problem-solving, structured planning, coding, and natural multi-turn conversation.
  * You maintain conversation context during the current active session.
  * If the user asks about deep system tasks (such as opening local apps, executing terminal commands, browsing their private local hard drive files, or desktop automation), explain that those require the installed Desktop RUHI environment with explicit user permissions, while offering to plan, code, or draft the workflow right here in the web interface.

Formatting Guidelines:
- Use clean Markdown with clear headings, bullet points, and code blocks with syntax highlighting when relevant.
- Keep explanations structured and easy to read.
""".strip()


class GeminiService(BaseLLMService):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.DEFAULT_MODEL
        self.fallback_model = settings.FALLBACK_MODEL
        self._client: Optional[genai.Client] = None
        self._init_client()

    def _init_client(self):
        if self.api_key:
            try:
                self._client = genai.Client(api_key=self.api_key)
                logger.info(f"Gemini client initialized successfully with model: {self.model}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self._client = None
        else:
            logger.warning("No GEMINI_API_KEY provided. RUHI will run in simulated demo mode.")
            self._client = None

    def get_provider_name(self) -> str:
        return "Google Gemini"

    def get_model_name(self) -> str:
        return self.model

    async def generate_response(
        self,
        history: List[ChatMessage],
        new_message: str,
        system_instruction: Optional[str] = None,
        **kwargs
    ) -> str:
        sys_prompt = system_instruction or RUHI_SYSTEM_INSTRUCTION
        
        if not self._client:
            # Re-attempt initialization in case key was loaded late
            self.api_key = settings.GEMINI_API_KEY
            self._init_client()

        if not self._client:
            # Fallback simulated intelligent response if no API key is configured
            return self._generate_simulated_response(new_message, history)

        # Build contents from history
        contents = []
        for msg in history:
            role = "user" if msg.role == "user" else "model"
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg.content)]
                )
            )
        
        # Append current user prompt
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=new_message)]
            )
        )

        config = types.GenerateContentConfig(
            system_instruction=sys_prompt,
            temperature=0.7,
            top_p=0.95,
        )

        try:
            response = self._client.models.generate_content(
                model=self.model,
                contents=contents,
                config=config
            )
            if response and response.text:
                return response.text.strip()
            return "I received your message, but the response stream was empty. How else may I assist you?"
        except Exception as e:
            logger.warning(f"Error calling Gemini model {self.model}: {e}. Trying fallback model {self.fallback_model}...")
            try:
                response = self._client.models.generate_content(
                    model=self.fallback_model,
                    contents=contents,
                    config=config
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as fallback_error:
                logger.error(f"Fallback model failed: {fallback_error}")
                raise RuntimeError(f"RUHI AI Service error: {str(e)}")

    def _generate_simulated_response(self, prompt: str, history: List[ChatMessage]) -> str:
        p_lower = prompt.lower()
        
        # Check context
        name_mention = ""
        for msg in history:
            if "my name is " in msg.content.lower():
                parts = msg.content.lower().split("my name is ")
                if len(parts) > 1:
                    extracted_name = parts[1].split()[0].replace(".", "").capitalize()
                    name_mention = f" {extracted_name}"

        if "hello" in p_lower or "hi" in p_lower or "hey" in p_lower:
            return f"Hello{name_mention}. I am **RUHI**, your personal AI system. I am here to understand your goals, retain active session context, and assist your workflow. What are you working on today?"
        
        if "what is ruhi" in p_lower or "who are you" in p_lower:
            return (
                "**RUHI** is an intelligent personal AI system designed to bridge the gap between human intent and digital execution.\n\n"
                "Unlike traditional chatbots that simply respond to one-off prompts, RUHI combines:\n"
                "- **Reasoning & Planning**: Deconstructing complex challenges into actionable logic.\n"
                "- **Session & Personal Context**: Remembering what matters across your active session.\n"
                "- **Tool Orchestration**: Coordinating with specialized tools and desktop environments.\n\n"
                "In this web interface, you can explore reasoning and chat. When installed on your machine, RUHI gains secure, permissioned local execution capabilities."
            )

        if "plan" in p_lower:
            return (
                "Here is a structured framework to plan that goal:\n\n"
                "1. **Core Objective Clarification**: Define the exact measurable outcome.\n"
                "2. **Resource & Context Mapping**: Identify required inputs, dependencies, and constraints.\n"
                "3. **Milestone Breakdown**: Segment into 3 sequential phases.\n"
                "4. **Execution & Feedback Loop**: Continuous review with RUHI.\n\n"
                "Would you like me to tailor this for a specific technical or personal project?"
            )

        return (
            f"I understand your query: *\"{prompt}\"*.\n\n"
            f"As your personal AI system, I am maintaining our conversation context (currently {len(history) + 1} turns in this session). "
            "How would you like to proceed or deepen this exploration?"
        )
