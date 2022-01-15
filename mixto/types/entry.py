from typing import Optional, List, Union
from uuid import UUID
from pydantic import BaseModel, Extra


class Base(BaseModel):
    username: Optional[str]
    avatar: Optional[str]
    time_created: Optional[Union[str, int]]
    time_updated: Optional[Union[str, int]]

    class Config:
        extra = Extra.allow


class RequiredIDs(Base):
    entry_id: Optional[str]
    commit_id: Optional[str]
    workspace: Optional[str]


class Note(RequiredIDs):
    text: Optional[str]
    title: Optional[str]
    note_id: Optional[str]


class Description(Base):
    text: Optional[str]
    entry_id: Optional[str]
    comment_id: Optional[str]
    workspace: Optional[str]
    priority: Optional[str]


class Meta(BaseModel):
    file_name: Optional[str]
    hash: Optional[str]
    mime: Optional[str]
    size: Optional[int]
    slack_channel: Optional[str]
    slack_ts: Optional[str]


class Like(RequiredIDs):
    like_id: Optional[str]


class CommitTag(RequiredIDs):
    tag_id: Optional[str]
    text: Optional[str]


class Commit(RequiredIDs):
    type: Optional[str]
    title: Optional[str]
    data: Optional[str]
    marked: Optional[bool]
    locked: Optional[bool]
    size: Optional[int]
    activity_count: Optional[int] = 0
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
