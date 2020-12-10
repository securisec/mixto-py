from pydantic import BaseModel
from typing import Optional

from typing_extensions import Literal


class Config(BaseModel):
    enabled: Optional[bool]
    channel: Optional[str] = None
    webhook: Optional[str] = None


NoticeTypes = Literal["info", "done", "high", "medium", "low", "default"]
