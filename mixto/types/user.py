from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UserInfo(BaseModel):
    username: Optional[str]
    avatar: Optional[str]
    api_key: Optional[str] = None


class Version(BaseModel):
    build_date: datetime
    git_commit: Optional[str]
    version: Optional[str]


class Settings(BaseModel):
    dark_theme: Optional[bool]
