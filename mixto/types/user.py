from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    username: Optional[str]
    avatar: Optional[str]
    api_key: Optional[str] = None
    admin: Optional[bool]
    disabled: Optional[bool]
    time_updated: Optional[int]
    time_created: Optional[int]
    service_account: Optional[bool]
    user_id: Optional[str]


class Settings(BaseModel):
    username: Optional[str]
    avatar: Optional[str]
    dark_theme: Optional[bool]
    show_timestamp: Optional[bool]
    workspace: Optional[str]
    theme: Optional[str]

class AvatarImage(BaseModel):
    avatar: Optional[str]
    seed: Optional[str]
    sprite: Optional[str]

class UserStats(BaseModel):
    username: Optional[str]
    avatar: Optional[str]
    entries: Optional[int]
    comments: Optional[int]
    commits: Optional[int]
    notes: Optional[int]
    flags: Optional[int]