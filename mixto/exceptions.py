from pydantic import BaseModel, Extra
from typing import List, Optional


class _extension(BaseModel,extra=Extra.allow):
    code: str
    path: str


class _error(BaseModel,extra=Extra.allow):
    extensions: Optional[_extension]
    message: Optional[str]


class Error(BaseModel,extra=Extra.allow):
    status: int
    errors: Optional[List[_error]]
