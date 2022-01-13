from typing import Optional, List, Union
from uuid import UUID
from pydantic import BaseModel


class Base(BaseModel):
    username: Optional[str]
    avatar: Optional[str]
    time_created: Optional[Union[str, int]]
    time_updated: Optional[Union[str, int]]


class Note(Base):
    workspace: Optional[str]
    text: Optional[str]
    title: Optional[str]
    entry_id: Optional[str]
    note_id: Optional[str]
    commit_id: Optional[str]


class Description(Base):
    text: Optional[str]
    entry_id: Optional[str]
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


class Like(Base):
    like_id: Optional[str]
    commit_id: Optional[str]
    entry_id: Optional[str]
    workspace: Optional[str]


class CommitTag(Base):
    tag_id: Optional[str]
    commit_id: Optional[str]
    entry_id: Optional[str]
    workspace: Optional[str]
    text: Optional[str]


class Commit(Base):
    commit_id: Optional[UUID]
    entry_id: Optional[str]
    workspace: Optional[str]
    type: Optional[str]
    title: Optional[str]
    data: Optional[str]
    marked: Optional[bool]
    locked: Optional[bool]
    size: Optional[int]
    comments: Optional[List[Description]]
    likes: Optional[List[Like]]
    tags: Optional[List[CommitTag]]
    meta: Optional[Meta] = None


class Flag(Base):
    entry_id: Optional[str]
    flag_id: Optional[str]
    workspace: Optional[str]
    flag: Optional[str]


class Entry(Base):
    entry_id: Optional[str]
    title: Optional[str]
    workspace: Optional[str]
    category: Optional[str]
    priority: Optional[str]
    entry_tags: Optional[List[str]]
    commits: Optional[List[Commit]]
    description: Optional[Description]
    notice: Optional[Description]
    notes: Optional[List[Note]]
    flags: Optional[List[Flag]]
    commit_count: Optional[int]
    flags_count: Optional[int]
    notes_count: Optional[int]


class Activity(BaseModel):
    entry_id: Optional[str]
    workspace: Optional[str]
    entry_title: Optional[str]
    message: Optional[str]
    time_created: Optional[int]
    type: Optional[str]
    username: Optional[str]
    avatar: Optional[str]
