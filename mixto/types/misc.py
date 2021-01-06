from pydantic import BaseModel
from typing import Dict, List, Optional

from typing_extensions import Literal


class Config(BaseModel):
    enabled: Optional[bool] = None
    token_set: Optional[bool] = None
    workspaces: Optional[Dict[str, str]]


class WorkspaceCommit(BaseModel):
    commit_id: str
    title: str
    type: str
    time_updated: int


class Workspace(BaseModel):
    entry_id: str
    workspace: str
    title: str
    category: str
    commit_count: int
    time_updated: int
    commits: List[WorkspaceCommit]


NoticeTypes = Literal["info", "done", "high", "medium", "low", "default"]

CommitTypes = Literal["dump", "script", "tool", "stdout"]
