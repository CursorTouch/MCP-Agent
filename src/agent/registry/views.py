from pydantic import BaseModel
from typing import Any

class ToolResult(BaseModel):
    is_success: bool
    content: Any | None = None
    error: str | None = None