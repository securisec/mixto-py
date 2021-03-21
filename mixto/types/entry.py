from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel


class Note(BaseModel):
    text: Optional[str]
    title: Optional[str]
    notes_id: Optional[str]
    entry_id: Optional[str]
    username: Optional[str]
    avatar: Optional[str]
    time_created: Optional[int]
    time_updated: Optional[int]


class Description(BaseModel):
    text: Optional[str]
    entry_id: Optional[str]
    time_created: Optional[float]
    time_updated: Optional[float]
    username: Optional[str]
    avatar: Optional[str]
    comment_id: Optional[UUID] = None
    commit_id: Optional[UUID] = None
    priority: Optional[str] = None


class Meta(BaseModel):
    file_name: Optional[str] = None
    hash: Optional[str] = None
    mime: Optional[str] = None
    size: Optional[int] = None
    slack_channel: Optional[str] = None
    slack_ts: Optional[str] = None


class Commit(BaseModel):
    commit_id: Optional[UUID]
    entry_id: Optional[str]
    type: Optional[str]
    title: Optional[str]
    data: Optional[str]
    marked: Optional[bool]
    locked: Optional[bool]
    time_created: Optional[int]
    time_updated: Optional[int]
    username: Optional[str]
    avatar: Optional[str]
    comments: Optional[List[Description]]
    meta: Optional[Meta] = None


class Entry(BaseModel):
    entry_id: Optional[str]
    title: Optional[str]
    workspace: Optional[str]
    category: Optional[str]
    priority: Optional[str]
    time_created: Optional[int]
    time_updated: Optional[int]
    username: Optional[str]
    avatar: Optional[str]
    commits: List[Commit]
    description: Optional[Description]
    notice: Optional[Description]
    notes: Optional[List[Note]]