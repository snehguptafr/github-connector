from pydantic import BaseModel
from typing import Optional

class IssueCreate(BaseModel):
    title: str
    body: Optional[str] = None

class PRCreate(BaseModel):
    title: str
    head: str
    base: str
    body: Optional[str] = None