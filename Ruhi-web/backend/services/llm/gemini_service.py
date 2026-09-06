import asyncio
import logging
from typing import List, Optional, AsyncIterator, Any, cast
from google import genai
from google.genai import types

from backend.config.settings import settings
from backend.models.schemas import ChatMessage
from backend.services.llm.base import BaseLLMProvider

logger = logging.getLogger("ruhi.llm.gemini")


class GeminiProvider(BaseLLMProvider):
    """
    Google Gemini implementation of BaseLLMProvider.
    Decoupled from RUHI Core logic.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.DEFAULT_MODEL
        self.fallback_model = settings.FALLBACK_MODEL
        self._client: Optional[genai.Client] = None
        self._init_client()

    def _init_client(self):
        key = self.api_key.strip() if self.api_key else ""
        if key:
            try:
                self._client = genai.Client(api_key=key)
                logger.info(f"GeminiProvider initialized with model: {self.model}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self._client = None
        else:
            logger.warning("No GEMINI_API_KEY detected. AI operations will require configuration.")
            self._client = None

    def is_configured(self) -> bool:
        return self._client is not None or bool(settings.GEMINI_API_KEY.strip())

    def get_provider_name(self) -> str:
        return "Google Gemini"

    def _ensure_client(self):
        if not self._client and settings.GEMINI_API_KEY.strip():
            self.api_key = settings.GEMINI_API_KEY.strip()
            self._init_client()

        if not self._client:
            raise RuntimeError(
                "Gemini API key is not configured. Please set GEMINI_API_KEY in your environment or .env file."
            )

    def _build_contents(self, history: List[ChatMessage], new_message: str) -> list[types.Content]:
        contents = []
        for msg in history:
            role = "user" if msg.role == "user" else "model"
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg.content)]
                )
            )
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=new_message)]
            )
        )
        return contents

    async def generate_response(
        self,
        history: List[ChatMessage],
        new_message: str,
        system_instruction: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        self._ensure_client()
        contents = self._build_contents(history, new_message)

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=kwargs.get("temperature", 0.7),
            top_p=kwargs.get("top_p", 0.95),
        )

        def _call_model(model_name: str) -> str:
            assert self._client is not None
            response = self._client.models.generate_content(
                model=model_name,
                contents=cast(Any, contents),
                config=config
            )
            if response and response.text:
                return response.text.strip()
            return ""

        try:
            result = await asyncio.to_thread(_call_model, self.model)
            if result:
                return result
            return "I received your message, but the generated response was empty."
        except Exception as e:
            logger.warning(f"Error with primary model {self.model}: {e}. Retrying with fallback {self.fallback_model}...")
            try:
                result = await asyncio.to_thread(_call_model, self.fallback_model)
                if result:
                    return result
                return "I received your message, but the generated response was empty."
            except Exception as fallback_err:
                logger.error(f"Fallback model failed: {fallback_err}")
                raise RuntimeError(f"LLM Provider error: {str(e)}")

    async def stream_response(
        self,
        history: List[ChatMessage],
        new_message: str,
        system_instruction: Optional[str] = None,
        **kwargs: Any
    ) -> AsyncIterator[str]:
        self._ensure_client()
        contents = self._build_contents(history, new_message)

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=kwargs.get("temperature", 0.7),
            top_p=kwargs.get("top_p", 0.95),
        )

        def _get_stream(model_name: str):
            assert self._client is not None
            return self._client.models.generate_content_stream(
                model=model_name,
                contents=cast(Any, contents),
                config=config
            )

        queue: asyncio.Queue[Optional[str]] = asyncio.Queue()
        error_container: list[Exception] = []

        def _worker():
            try:
                stream = _get_stream(self.model)
                for chunk in stream:
                    if chunk.text:
                        queue.put_nowait(chunk.text)
            except Exception as err:
                logger.warning(f"Streaming failed on primary model {self.model}: {err}. Retrying on fallback {self.fallback_model}...")
                try:
                    stream = _get_stream(self.fallback_model)
                    for chunk in stream:
                        if chunk.text:
                            queue.put_nowait(chunk.text)
                except Exception as fb_err:
                    logger.error(f"Streaming fallback failed: {fb_err}")
                    error_container.append(fb_err)
            finally:
                queue.put_nowait(None)

        loop = asyncio.get_running_loop()
        loop.run_in_executor(None, _worker)

        while True:
            item = await queue.get()
            if item is None:
                break
            yield item

        if error_container:
            raise RuntimeError(f"Streaming generation error: {str(error_container[0])}")
