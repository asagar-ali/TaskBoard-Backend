import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.task import TaskStatus


class TaskCreate(BaseModel):
    title: str
    description: Optional[str]
    status: TaskStatus = TaskStatus.PENDING


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None

class TaskStatusUpdate(BaseModel):
    status: TaskStatus

class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: TaskStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class ConfigDict:
        from_attributes = True

