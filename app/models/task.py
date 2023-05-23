# /models/task.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date, datetime
from enum import Enum
from bson import ObjectId
from typing import Any


class TaskStatus(str, Enum):
    NOT_STARTED = "not started"
    IN_PROGRESS = "in progress"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"
    DONE = "done"

class Task(BaseModel):
    _id: Optional[ObjectId] = None
    id: Optional[str] = None
    name: str
    description: str
    due_date: datetime
    min_effort_required: int
    max_effort_required: int
    status: TaskStatus
    owner: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    importance: int
    parent_task: Optional[str] = Field(alias="parent_task_id")

    @validator("importance")
    def importance_range(cls, value):
        if value < 1 or value > 6:
            raise ValueError("importance must be between 1 and 6")
        return value

    @property
    def id_str(self) -> Optional[str]:
        if self.id:
            return str(self.id)
        return None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

    def dict(self, *args: Any, **kwargs: Any) -> dict:
        task_dict = super().dict(*args, **kwargs)
        if self.id:
            task_dict["id"] = str(self.id)
        return task_dict

    def get_status_string(self) -> str:
        return self.status.value

