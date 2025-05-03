from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    ForeignKey,
    TIMESTAMP,
    Enum,
)
from database import Base
import enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import JSON


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    name = Column(String(100), nullable=False)
    description = Column(Text)
    skills = Column(JSON)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(15), unique=True, nullable=True)

    rejected_task_count = Column(Integer, default=0)
    assigned_task_count = Column(Integer, default=0)
    tasks_completed_count = Column(Integer, default=0)
    tasks_before_deadline_count = Column(Integer, default=0)
    new_skills_learnt = Column(JSON)
    marks = Column(Integer, default=0)

    user = relationship("User")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    role = Column(String(20), nullable=False)


class TaskStatus(enum.Enum):
    unassigned = "unassigned"
    in_progress = "in_progress"
    completed_before_deadline = "completed_before_deadline"
    completed_after_deadline = "completed_after_deadline"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    completed_at = Column(TIMESTAMP, nullable=True)
    deadline = Column(TIMESTAMP, nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    accepted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    mandatory = Column(Boolean, default=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.unassigned)
    rejected = Column(Boolean, default=False)
