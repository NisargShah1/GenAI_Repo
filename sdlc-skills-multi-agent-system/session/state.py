from pydantic import BaseModel, Field
from typing import List, Optional

class TaskState(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    agent: str
    status: str = "PENDING" # PENDING, IN_PROGRESS, COMPLETED
    skills_needed: List[str] = Field(default_factory=list)
    output: Optional[str] = None
    sequence: int = 0

class CodeFileState(BaseModel):
    id: Optional[int] = None
    path: str
    content: str

class SprintSessionState(BaseModel):
    sprint_id: Optional[int] = None
    requirement: str
    status: str = "PLANNED"
    current_task_id: Optional[int] = None
    current_agent: Optional[str] = None
    tasks: List[TaskState] = Field(default_factory=list)
    loaded_skills: List[str] = Field(default_factory=list)
    generated_files: List[CodeFileState] = Field(default_factory=list)
    conversation_summary: Optional[str] = None
