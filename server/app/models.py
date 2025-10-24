from __future__ import annotations

from datetime import date, datetime, time
from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class ContextEnum(str, Enum):
    work = "work"
    personal = "personal"
    general = "general"


class TaskStatus(str, Enum):
    todo = "todo"
    doing = "doing"
    done = "done"


class ProjectStatus(str, Enum):
    active = "active"
    paused = "paused"
    done = "done"


class ProjectContext(str, Enum):
    work = "work"
    personal = "personal"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    tasks: List["Task"] = Relationship(back_populates="user")


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    title: str
    notes: Optional[str] = None
    context: ContextEnum = Field(default=ContextEnum.general, index=True)
    due_date: Optional[date] = Field(default=None, index=True)
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_recurring: bool = Field(default=False, index=True)
    recur_rule: Optional[str] = None
    priority: int = Field(default=0, index=True)
    status: TaskStatus = Field(default=TaskStatus.todo, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[User] = Relationship(back_populates="tasks")


class TaskTemplate(SQLModel, table=True):
    __tablename__ = "task_templates"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    title: str
    notes: Optional[str] = None
    context: ContextEnum = Field(default=ContextEnum.general)
    recur_rule: Optional[str] = None
    default_day_of_week: Optional[int] = Field(default=None)


class DailyLog(SQLModel, table=True):
    __tablename__ = "daily_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    date: date = Field(index=True)
    summary: str
    mood: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Exercise(SQLModel, table=True):
    __tablename__ = "exercises"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    name: str = Field(index=True)
    muscle_group: Optional[str] = None
    notes: Optional[str] = None


class Workout(SQLModel, table=True):
    __tablename__ = "workouts"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    date: date = Field(index=True)
    title: str
    notes: Optional[str] = None

    sets: List["WorkoutSet"] = Relationship(back_populates="workout", sa_relationship_kwargs={"cascade": "all, delete"})


class WorkoutSet(SQLModel, table=True):
    __tablename__ = "workout_sets"

    id: Optional[int] = Field(default=None, primary_key=True)
    workout_id: int = Field(foreign_key="workouts.id", index=True)
    exercise_id: int = Field(foreign_key="exercises.id", index=True)
    set_number: int = Field(index=True)
    weight: float
    reps: int
    rpe: Optional[float] = None
    notes: Optional[str] = None

    workout: Optional[Workout] = Relationship(back_populates="sets")
    exercise: Optional[Exercise] = Relationship()


class PR(SQLModel, table=True):
    __tablename__ = "prs"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    exercise_id: int = Field(foreign_key="exercises.id", index=True)
    weight: float
    reps: int
    date: date = Field(index=True)


class Project(SQLModel, table=True):
    __tablename__ = "projects"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    title: str
    status: ProjectStatus = Field(default=ProjectStatus.active, index=True)
    context: ProjectContext = Field(default=ProjectContext.work, index=True)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    updates: List["ProjectUpdate"] = Relationship(back_populates="project", sa_relationship_kwargs={"cascade": "all, delete"})


class ProjectUpdate(SQLModel, table=True):
    __tablename__ = "project_updates"

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id", index=True)
    date: date = Field(index=True)
    progress_percent: int
    note: Optional[str] = None
    how_it_was_done: Optional[str] = None

    project: Optional[Project] = Relationship(back_populates="updates")
    media_items: List["Media"] = Relationship(back_populates="project_update", sa_relationship_kwargs={"cascade": "all, delete"})


class Media(SQLModel, table=True):
    __tablename__ = "media"

    id: Optional[int] = Field(default=None, primary_key=True)
    project_update_id: int = Field(foreign_key="project_updates.id", index=True)
    file_path: str
    caption: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    project_update: Optional[ProjectUpdate] = Relationship(back_populates="media_items")
