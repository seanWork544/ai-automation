from datetime import date, datetime, time
from typing import Optional

from pydantic import BaseModel, Field

from .models import ContextEnum, ProjectContext, ProjectStatus, TaskStatus


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: str
    password: str = Field(min_length=6)


class UserRead(BaseModel):
    id: int
    email: str

    class Config:
        orm_mode = True


class TaskBase(BaseModel):
    title: str
    notes: Optional[str] = None
    context: ContextEnum = ContextEnum.general
    due_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_recurring: bool = False
    recur_rule: Optional[str] = None
    priority: int = 0
    status: TaskStatus = TaskStatus.todo


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    title: Optional[str] = None
    status: Optional[TaskStatus] = None
    is_recurring: Optional[bool] = None


class TaskRead(TaskBase):
    id: int

    class Config:
        orm_mode = True


class TaskTemplateBase(BaseModel):
    title: str
    notes: Optional[str] = None
    context: ContextEnum = ContextEnum.general
    recur_rule: Optional[str] = None
    default_day_of_week: Optional[int] = None


class TaskTemplateCreate(TaskTemplateBase):
    pass


class TaskTemplateUpdate(TaskTemplateBase):
    title: Optional[str] = None


class TaskTemplateRead(TaskTemplateBase):
    id: int

    class Config:
        orm_mode = True


class DailyLogBase(BaseModel):
    date: date
    summary: str
    mood: Optional[int] = None


class DailyLogCreate(DailyLogBase):
    pass


class DailyLogUpdate(DailyLogBase):
    date: Optional[date] = None
    summary: Optional[str] = None


class DailyLogRead(DailyLogBase):
    id: int

    class Config:
        orm_mode = True


class ExerciseBase(BaseModel):
    name: str
    muscle_group: Optional[str] = None
    notes: Optional[str] = None


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseUpdate(ExerciseBase):
    name: Optional[str] = None


class ExerciseRead(ExerciseBase):
    id: int

    class Config:
        orm_mode = True


class WorkoutBase(BaseModel):
    date: date
    title: str
    notes: Optional[str] = None


class WorkoutCreate(WorkoutBase):
    pass


class WorkoutUpdate(WorkoutBase):
    date: Optional[date] = None
    title: Optional[str] = None


class WorkoutRead(WorkoutBase):
    id: int

    class Config:
        orm_mode = True


class WorkoutSetBase(BaseModel):
    workout_id: int
    exercise_id: int
    set_number: int
    weight: float
    reps: int
    rpe: Optional[float] = None
    notes: Optional[str] = None


class WorkoutSetCreate(WorkoutSetBase):
    pass


class WorkoutSetUpdate(BaseModel):
    set_number: Optional[int] = None
    weight: Optional[float] = None
    reps: Optional[int] = None
    rpe: Optional[float] = None
    notes: Optional[str] = None


class WorkoutSetRead(WorkoutSetBase):
    id: int

    class Config:
        orm_mode = True


class PRBase(BaseModel):
    exercise_id: int
    weight: float
    reps: int
    date: date


class PRCreate(PRBase):
    pass


class PRUpdate(BaseModel):
    weight: Optional[float] = None
    reps: Optional[int] = None
    date: Optional[date] = None


class PRRead(PRBase):
    id: int

    class Config:
        orm_mode = True


class ProjectBase(BaseModel):
    title: str
    status: ProjectStatus = ProjectStatus.active
    context: ProjectContext = ProjectContext.work
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    title: Optional[str] = None
    status: Optional[ProjectStatus] = None
    context: Optional[ProjectContext] = None


class ProjectRead(ProjectBase):
    id: int

    class Config:
        orm_mode = True


class ProjectUpdateBase(BaseModel):
    project_id: int
    date: date
    progress_percent: int
    note: Optional[str] = None
    how_it_was_done: Optional[str] = None


class ProjectUpdateCreate(ProjectUpdateBase):
    pass


class ProjectUpdatePatch(BaseModel):
    date: Optional[date] = None
    progress_percent: Optional[int] = None
    note: Optional[str] = None
    how_it_was_done: Optional[str] = None


class ProjectUpdateRead(ProjectUpdateBase):
    id: int

    class Config:
        orm_mode = True


class MediaCreate(BaseModel):
    project_update_id: int
    file_path: str
    caption: Optional[str] = None


class MediaRead(MediaCreate):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
