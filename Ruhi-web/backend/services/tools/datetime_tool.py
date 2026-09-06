from datetime import datetime, timezone
import zoneinfo
from typing import Dict, Any, Optional
from backend.services.tools.base import BaseTool


class DateTimeTool(BaseTool):
    name: str = "datetime_tool"
    description: str = "Query current date, time, day of the week, UTC offset, or timezone."
    category: str = "utility"
    requires_desktop: bool = False

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "timezone_name": {
                    "type": "string",
                    "description": "Optional IANA timezone name (e.g. 'UTC', 'America/New_York', 'Asia/Kolkata')"
                }
            }
        }

    async def execute(self, timezone_name: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        try:
            if timezone_name:
                tz = zoneinfo.ZoneInfo(timezone_name)
                now = datetime.now(tz)
                tz_str = timezone_name
            else:
                now = datetime.now(timezone.utc)
                tz_str = "UTC"

            return {
                "iso": now.isoformat(),
                "formatted": now.strftime("%A, %B %d, %Y at %I:%M:%S %p %Z"),
                "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M:%S"),
                "day_of_week": now.strftime("%A"),
                "timezone": tz_str,
                "success": True
            }
        except Exception as e:
            now_utc = datetime.now(timezone.utc)
            return {
                "iso": now_utc.isoformat(),
                "formatted": now_utc.strftime("%A, %B %d, %Y at %I:%M:%S %p UTC"),
                "timezone": "UTC (fallback)",
                "error": f"Invalid timezone '{timezone_name}': {str(e)}",
                "success": True
            }
