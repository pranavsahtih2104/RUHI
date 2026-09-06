import re
import urllib.parse
from typing import Dict, Any, Optional
import httpx
from backend.services.tools.base import BaseTool


class WebRetrievalTool(BaseTool):
    """
    Safe Web Retrieval / Lookup Tool.
    Performs safe HTTP lookups of authorized public endpoints or text extraction.
    """
    name: str = "web_retrieval"
    description: str = "Safely fetch and parse text summaries from a public URL."
    category: str = "web"
    requires_desktop: bool = False

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The public HTTP/HTTPS URL to fetch and summarize."
                }
            },
            "required": ["url"]
        }

    async def execute(self, url: str = "", **kwargs: Any) -> Dict[str, Any]:
        if not url:
            return {
                "url": url,
                "error": "URL parameter is required.",
                "success": False
            }

        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return {
                "url": url,
                "error": "Only HTTP and HTTPS protocols are supported for safety.",
                "success": False
            }

        # Block localhost / private IP ranges for security
        hostname = (parsed.hostname or "").lower()
        if hostname in ("localhost", "127.0.0.1", "0.0.0.0") or hostname.startswith("192.168.") or hostname.startswith("10."):
            return {
                "url": url,
                "error": "Access to local and private networks is restricted.",
                "success": False
            }

        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                headers = {"User-Agent": "RUHI-AI-Core/1.0 (Personal AI Research Bot)"}
                resp = await client.get(url, headers=headers)
                
                if resp.status_code != 200:
                    return {
                        "url": url,
                        "status_code": resp.status_code,
                        "error": f"Remote server returned status {resp.status_code}",
                        "success": False
                    }

                # Simple clean text extraction
                text = resp.text
                clean_text = re.sub(r"<script.*?</script>", " ", text, flags=re.DOTALL | re.IGNORECASE)
                clean_text = re.sub(r"<style.*?</style>", " ", clean_text, flags=re.DOTALL | re.IGNORECASE)
                clean_text = re.sub(r"<[^>]+>", " ", clean_text)
                clean_text = re.sub(r"\s+", " ", clean_text).strip()

                truncated = clean_text[:2000] + ("..." if len(clean_text) > 2000 else "")

                return {
                    "url": url,
                    "status_code": 200,
                    "content_preview": truncated,
                    "content_length": len(clean_text),
                    "success": True
                }
        except Exception as e:
            return {
                "url": url,
                "error": f"Failed to retrieve URL: {str(e)}",
                "success": False
            }
