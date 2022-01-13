from typing import Optional
from pydantic import BaseModel


class AdminFile(BaseModel):
    key: Optional[str]
    size: Optional[int]
    name: Optional[str]
    username: Optional[str]
    workspace: Optional[str]
    mime: Optional[str]
    entry_id: Optional[str]
    time_added: Optional[str]


class ServiceAccount(BaseModel):
    api_key: Optional[str]
    id: Optional[str]
    time_created: Optional[int]
    username: Optional[str]

class Backup(BaseModel):
    key: Optional[str]
    size: Optional[int]