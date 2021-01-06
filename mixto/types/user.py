from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UserInfo(BaseModel):
    username: Optional[str]
    avatar: Optional[str]
    api_key: Optional[str] = None
    admin: Optional[bool]
    disabled: Optional[bool]


class Version(BaseModel):
    BuildDate: datetime
    GitCommit: datetime
    Debug: Optional[bool]
    Production: Optional[bool]
    Version: Optional[str]


class Settings(BaseModel):
    dark_theme: Optional[bool]
    show_timestamp: Optional[bool]
    workspace: Optional[str]
