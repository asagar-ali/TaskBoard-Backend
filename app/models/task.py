import datetime
import uuid
import enum

from sqlalchemy import Column, DateTime, String
from sqlalchemy import Enum as SAEnum

from app.core.database import Base


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    STARTED = "started"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), index=True, nullable=False)
    description = Column(String, nullable=True)
    status = Column(SAEnum(TaskStatus), nullable=False, default=TaskStatus.PENDING)
    org_id = Column(String, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_by = Column(String, index=True, nullable=False)
    # ✅ Fix: added onupdate so updated_at actually reflects the last edit time
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )