from pydantic import BaseModel
from typing import Any, Dict, List, Optional, Literal, Union

from mixto.types.entry import Note


class Base(BaseModel):
    username: Optional[str]
    avatar: Optional[str]
    time_created: Optional[Union[str, int]]
    time_updated: Optional[Union[str, int]]


class Version(BaseModel):
    BuildDate: str
    GitCommit: str
    Debug: Optional[bool]
    Production: Optional[bool]
    Version: Optional[str]
    GitBranch: Optional[str]
    integrations: Optional[Dict[str, Dict[str, Any]]]


class ValidDataTypes(BaseModel):
    categories: List[str]
    types: List[str]
    priorities: List[str]


class Etag(BaseModel):
    created: Optional[str]
    etag: Optional[str]


class Config(BaseModel):
    enabled: Optional[bool] = None
    token_set: Optional[bool] = None
    workspaces: Optional[Dict[str, str]]


class WorkspaceCommit(BaseModel):
    commit_id: str
    title: str
    type: str
    time_updated: int


class Workspace(Base):
    workspace_id: Optional[str]
    description: Optional[str]
    workspace: Optional[str]
    private: Optional[bool]
    locked: Optional[bool]
    imported: Optional[bool]
    entries_count: Optional[int]
    commits_count: Optional[int]
    flags_count: Optional[int]


NoticeTypes = Literal["info", "done", "high", "medium", "low", "default"]

CommitTypes = Literal[
    "dump", "script", "tool", "stdout", "url", "asciinema", "file", "image"
]

EntryCategories = Literal[
    "android",
    "cloud",
    "crypto",
    "firmware",
    "forensics",
    "hardware",
    "ios",
    "misc",
    "network",
    "password",
    "pcap",
    "pwn",
    "reversing",
    "stego",
    "web",
    "none",
    "other",
    "scripting",
]


class Hit(BaseModel):
    category: Optional[str]
    data: Optional[str]
    entry_id: Optional[str]
    entry_tags: Optional[List[str]]
    entry_title: Optional[str]
    flags: Optional[List[str]]
    id: Optional[str]
    notes: Optional[List[Any]]
    tags: Optional[List[str]]
    time_updated: Optional[Union[str, int]]
    title: Optional[str]
    type: Optional[str]
    workspace: Optional[str]
