from typing import Optional, Any, List
from pydantic import BaseModel, Extra
from uuid import UUID


class MixtoConfig(BaseModel, extra=Extra.allow):
    workspace_id: str
    workspace_name: Optional[str]
    api_key: str
    host: str
    instance: Optional[str]


class sharedBase(BaseModel, extra=Extra.allow):
    updated_at: Optional[str]
    created_at: Optional[str]
    meta: Optional[Any]
    user_id: Optional[str]
    workspace_id: Optional[UUID]
    entry_id: Optional[str]


class ActivityBase(sharedBase):
    activity_id: Optional[str]
    commit_id: Optional[UUID]
    message: Optional[str]
    action: Optional[str]
    activity_type: Optional[str]


class CommentBase(sharedBase):
    comment_id: Optional[UUID]
    commit_id: Optional[str]
    text: Optional[str]


class FileBase(sharedBase):
    file_id: Optional[str]
    name: Optional[str]
    hash: Optional[str]
    size: Optional[int]
    mime: Optional[str]
    bucket: Optional[str]
    artifact: Optional[bool]
    image: Optional[bool]


class FlagBase(sharedBase):
    flag: Optional[str]
    flag_id: Optional[str]


class LikeBase(sharedBase):
    like_id: Optional[str]


class NoteBase(sharedBase):
    note_id: Optional[str]
    data: Optional[str]


class StarBase(sharedBase):
    star_id: Optional[str]


class CommitTagBase(sharedBase):
    tag_id: Optional[str]
    text: Optional[str]


class EntryTagBase(sharedBase):
    tag_id: Optional[str]
    text: Optional[str]


class NoteTagBase(sharedBase):
    tag_id: Optional[str]
    text: Optional[str]


class TodoBase(sharedBase):
    todo_id: Optional[str]
    data: Optional[str]
    completed: Optional[bool]


class CommitBase(sharedBase):
    commit_id: Optional[str]
    data: Optional[str]
    title: Optional[str]
    commit_type: Optional[str]
    documentation: Optional[bool]
    artifact: Optional[bool]
    priority: Optional[str]


class EntryBase(sharedBase):
    category: Optional[str]
    description: Optional[str]
    priority: Optional[str]


class WorkspaceBase(BaseModel, extra=Extra.allow):
    updated_at: Optional[str]
    created_at: Optional[str]
    meta: Optional[Any]
    user_id: Optional[str]
    workspace_id: Optional[UUID]
    workspace_name: Optional[str]
    imported: Optional[bool]
    locked: Optional[bool]
    login: Optional[str]
    password: Optional[str]
    private: Optional[bool]
    url: Optional[str]
    description: Optional[str]
    enabled: Optional[bool]
    search_index: Optional[str]


class Hit(BaseModel, extra=Extra.allow):
    commit_id: Optional[str]
    workspace_id: Optional[str]
    entry_id: Optional[str]
    title: Optional[str]
    entry_title: Optional[str]
    data: Optional[str]
    category: Optional[str]
    workspace_name: Optional[str]
    search_index: Optional[str]
    tags: Optional[List[str]]
    commit_type: Optional[str]
    updated_at: Optional[str]
    priority: Optional[str]
    documentation: Optional[bool]


class Formatted(BaseModel, extra=Extra.allow):
    _formatted: Hit


class SearchOutput(BaseModel, extra=Extra.allow):
    estimatedTotalHits: Optional[int]
    hits: Optional[List[Formatted]]
