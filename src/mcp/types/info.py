from pydantic import BaseModel, ConfigDict
from typing import Optional
from src.mcp.types.common import Icon

class Implementation(BaseModel):
    name: str
    title: Optional[str] = None
    version: str
    websiteUrl: Optional[str] = None
    description: Optional[str] = None
    icons: Optional[list[Icon]] = None
    
    model_config = ConfigDict(extra='allow')