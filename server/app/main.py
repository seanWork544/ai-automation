from __future__ import annotations

import io
import json
import zipfile
from datetime import date, datetime
from typing import Dict

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from sqlmodel import Session, col, select

from .config import get_settings
from .database import engine, get_session, init_db
from .models import DailyLog, Exercise, PR, Project, ProjectUpdate, Task, TaskTemplate, User, Workout, WorkoutSet
from .routers import auth
from .routers.utils import build_crud_router
from .schemas import (
    DailyLogCreate,
    DailyLogRead,
    DailyLogUpdate,
    ExerciseCreate,
    ExerciseRead,
    ExerciseUpdate,
    PRCreate,
    PRRead,
    PRUpdate,
    ProjectCreate,
    ProjectRead,
    ProjectUpdateCreate,
    ProjectUpdatePatch,
    ProjectUpdateRead,
    TaskCreate,
    TaskRead,
    TaskTemplateCreate,
    TaskTemplateRead,
    TaskTemplateUpdate,
    TaskUpdate,
    WorkoutCreate,
    WorkoutRead,
    WorkoutSetCreate,
    WorkoutSetRead,
    WorkoutSetUpdate,
    WorkoutUpdate,
)
from .security import get_current_user
from .utils import compute_dashboard, compute_recurrence, export_entities

init_db()

app = FastAPI(title="LifeStack API")

settings = get_settings()

app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(
    build_crud_router(
        model=Task,
        create_schema=TaskCreate,
        update_schema=TaskUpdate,
        read_schema=TaskRead,
        prefix="/tasks",
        tags=["tasks"],
    )
)
app.include_router(
    build_crud_router(
        model=TaskTemplate,
        create_schema=TaskTemplateCreate,
        update_schema=TaskTemplateUpdate,
        read_schema=TaskTemplateRead,
        prefix="/task-templates",
        tags=["task-templates"],
    )
)
app.include_router(
    build_crud_router(
        model=DailyLog,
        create_schema=DailyLogCreate,
        update_schema=DailyLogUpdate,
        read_schema=DailyLogRead,
        prefix="/daily-logs",
        tags=["daily-logs"],
    )
)
app.include_router(
    build_crud_router(
        model=Exercise,
        create_schema=ExerciseCreate,
        update_schema=ExerciseUpdate,
        read_schema=ExerciseRead,
        prefix="/exercises",
        tags=["exercises"],
    )
)
app.include_router(
    build_crud_router(
        model=Workout,
        create_schema=WorkoutCreate,
        update_schema=WorkoutUpdate,
        read_schema=WorkoutRead,
        prefix="/workouts",
        tags=["workouts"],
    )
)
app.include_router(
    build_crud_router(
        model=PR,
        create_schema=PRCreate,
        update_schema=PRUpdate,
        read_schema=PRRead,
        prefix="/prs",
        tags=["prs"],
    )
)
app.include_router(
    build_crud_router(
        model=Project,
        create_schema=ProjectCreate,
        update_schema=ProjectUpdate,
        read_schema=ProjectRead,
        prefix="/projects",
        tags=["projects"],
    )
)
@app.post("/quick-capture", status_code=201)
def quick_capture(
    data: Dict[str, object],
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    capture_type = data.get("type")
    payload = data.get("payload") or {}
    if capture_type == "task":
        schema = TaskCreate(**payload)
        task = Task(**schema.dict(), user_id=current_user.id)
        session.add(task)
        session.commit()
        session.refresh(task)
        return {"status": "ok", "task_id": task.id}
    if capture_type == "log":
        schema = DailyLogCreate(**payload)
        log = DailyLog(**schema.dict(), user_id=current_user.id)
        session.add(log)
        session.commit()
        session.refresh(log)
        return {"status": "ok", "log_id": log.id}
    if capture_type == "set":
        schema = WorkoutSetCreate(**payload)
        workout = session.get(Workout, schema.workout_id)
        if not workout or workout.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Workout not found")
        workout_set = WorkoutSet(**schema.dict())
        session.add(workout_set)
        session.commit()
        session.refresh(workout_set)
        return {"status": "ok", "set_id": workout_set.id}
    if capture_type == "project_update":
        schema = ProjectUpdateCreate(**payload)
        project = session.get(Project, schema.project_id)
        if not project or project.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Project not found")
        update = ProjectUpdate(**schema.dict())
        session.add(update)
        session.commit()
        session.refresh(update)
        return {"status": "ok", "project_update_id": update.id}
    raise HTTPException(status_code=400, detail="Unsupported capture type")


@app.get("/workout-sets", response_model=list[WorkoutSetRead])
def list_workout_sets(
    workout_id: int | None = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    statement = select(WorkoutSet).join(Workout).where(Workout.user_id == current_user.id)
    if workout_id:
        statement = statement.where(WorkoutSet.workout_id == workout_id)
    return session.exec(statement).all()


@app.post("/workout-sets", response_model=WorkoutSetRead, status_code=201)
def create_workout_set(
    payload: WorkoutSetCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    workout = session.get(Workout, payload.workout_id)
    if not workout or workout.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Workout not found")
    workout_set = WorkoutSet(**payload.dict())
    session.add(workout_set)
    session.commit()
    session.refresh(workout_set)
    return workout_set


@app.patch("/workout-sets/{set_id}", response_model=WorkoutSetRead)
def update_workout_set(
    set_id: int,
    payload: WorkoutSetUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    workout_set = session.get(WorkoutSet, set_id)
    if not workout_set:
        raise HTTPException(status_code=404, detail="Set not found")
    workout = session.get(Workout, workout_set.workout_id)
    if not workout or workout.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Workout not found")
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(workout_set, key, value)
    session.add(workout_set)
    session.commit()
    session.refresh(workout_set)
    return workout_set


@app.delete("/workout-sets/{set_id}", status_code=204)
def delete_workout_set(
    set_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    workout_set = session.get(WorkoutSet, set_id)
    if not workout_set:
        raise HTTPException(status_code=404, detail="Set not found")
    workout = session.get(Workout, workout_set.workout_id)
    if not workout or workout.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Workout not found")
    session.delete(workout_set)
    session.commit()


@app.get("/project-updates", response_model=list[ProjectUpdateRead])
def list_project_updates(
    project_id: int | None = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    statement = select(ProjectUpdate).join(Project).where(Project.user_id == current_user.id)
    if project_id:
        statement = statement.where(ProjectUpdate.project_id == project_id)
    return session.exec(statement).all()


@app.post("/project-updates", response_model=ProjectUpdateRead, status_code=201)
def create_project_update(
    payload: ProjectUpdateCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    project = session.get(Project, payload.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    update = ProjectUpdate(**payload.dict())
    session.add(update)
    session.commit()
    session.refresh(update)
    return update


@app.patch("/project-updates/{update_id}", response_model=ProjectUpdateRead)
def update_project_update(
    update_id: int,
    payload: ProjectUpdatePatch,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    update = session.get(ProjectUpdate, update_id)
    if not update:
        raise HTTPException(status_code=404, detail="Update not found")
    project = session.get(Project, update.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(update, key, value)
    session.add(update)
    session.commit()
    session.refresh(update)
    return update


@app.delete("/project-updates/{update_id}", status_code=204)
def delete_project_update(
    update_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    update = session.get(ProjectUpdate, update_id)
    if not update:
        raise HTTPException(status_code=404, detail="Update not found")
    project = session.get(Project, update.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    session.delete(update)
    session.commit()


@app.post("/tasks/expand-recurring")
def expand_recurring(
    payload: dict,
    current_user: User = Depends(get_current_user),
):
    rule = payload.get("recur_rule")
    start_date = payload.get("start_date")
    weeks = int(payload.get("weeks", 4))
    if not rule or not start_date:
        raise HTTPException(status_code=400, detail="Missing recur_rule or start_date")
    start = date.fromisoformat(start_date)
    return {"instances": compute_recurrence(rule, start, weeks)}


@app.get("/dashboard/overview")
def dashboard_overview(
    week: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return compute_dashboard(session, current_user, week)


@app.get("/search")
def search(
    q: str = "",
    context: str | None = None,
    status_filter: str | None = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    results = {"tasks": [], "daily_logs": [], "projects": [], "project_updates": []}
    if q:
        like_query = f"%{q.lower()}%"
        task_stmt = select(Task).where(Task.user_id == current_user.id, col(Task.title).ilike(like_query))
        if context:
            task_stmt = task_stmt.where(Task.context == context)
        if status_filter:
            task_stmt = task_stmt.where(Task.status == status_filter)
        results["tasks"] = session.exec(task_stmt).all()

        log_stmt = select(DailyLog).where(DailyLog.user_id == current_user.id, col(DailyLog.summary).ilike(like_query))
        results["daily_logs"] = session.exec(log_stmt).all()

        project_stmt = select(Project).where(Project.user_id == current_user.id, col(Project.title).ilike(like_query))
        if context:
            project_stmt = project_stmt.where(Project.context == context)
        results["projects"] = session.exec(project_stmt).all()

        update_stmt = select(ProjectUpdate).join(Project).where(
            Project.user_id == current_user.id,
            col(ProjectUpdate.note).ilike(like_query) | col(ProjectUpdate.how_it_was_done).ilike(like_query),
        )
        results["project_updates"] = session.exec(update_stmt).all()
    return results


@app.get("/export.json")
def export_json(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    export_data = export_entities(session, current_user.id)
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for filename, records in export_data.items():
            zip_file.writestr(f"{filename}.json", json.dumps(records, default=str, indent=2))
    zip_buffer.seek(0)
    return StreamingResponse(zip_buffer, media_type="application/zip", headers={"Content-Disposition": "attachment; filename=lifstack_export_json.zip"})


@app.get("/export.csv")
def export_csv(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    export_data = export_entities(session, current_user.id)
    buffer = io.StringIO()
    csv_archives: dict[str, str] = {}
    for key, records in export_data.items():
        if not records:
            continue
        columns = records[0].keys()
        rows = [";".join(columns)]
        for record in records:
            rows.append(";".join(str(record[col] or "") for col in columns))
        csv_archives[key] = "\n".join(rows)
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for filename, content in csv_archives.items():
            zip_file.writestr(f"{filename}.csv", content)
    zip_buffer.seek(0)
    return StreamingResponse(zip_buffer, media_type="application/zip", headers={"Content-Disposition": "attachment; filename=lifstack_export.zip"})


@app.post("/uploads")
def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    if file.content_type not in {"image/png", "image/jpeg", "image/webp"}:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    contents = file.file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")
    file_path = settings.upload_dir / f"{datetime.utcnow().timestamp()}_{file.filename}"
    with file_path.open("wb") as f:
        f.write(contents)
    return {"file_path": str(file_path.relative_to(settings.upload_dir.parent))}


@app.post("/backup")
def backup_database():
    with open(engine.url.database, "rb") as db_file:
        return db_file.read()


@app.post("/restore")
def restore_database(file: UploadFile = File(...)):
    contents = file.file.read()
    if len(contents) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Backup too large")
    with open(engine.url.database, "wb") as db_file:
        db_file.write(contents)
    return {"status": "ok"}
