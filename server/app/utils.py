from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Dict, List

from fastapi import HTTPException
from sqlmodel import Session, func, select

from .models import DailyLog, PR, Project, ProjectUpdate, Task, Workout, WorkoutSet


def _parse_byday(rule: str) -> List[int]:
    rule = rule.upper()
    if "BYDAY" in rule:
        _, byday = rule.split("BYDAY=")
        if ";" in byday:
            byday = byday.split(";")[0]
        days = [chunk.strip() for chunk in byday.replace("RRULE:", "").split(",") if chunk.strip()]
    else:
        days = [chunk.strip() for chunk in rule.split(",") if chunk.strip()]
    mapping = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}
    return [mapping[d] for d in days if d in mapping]


def compute_recurrence(rule: str, start_date: date, weeks: int) -> List[str]:
    weekdays = _parse_byday(rule)
    if not weekdays:
        raise HTTPException(status_code=400, detail="Unsupported recurrence rule")
    results: List[str] = []
    current = start_date
    end = start_date + timedelta(weeks=weeks)
    while current <= end:
        if current.weekday() in weekdays:
            results.append(current.isoformat())
        current += timedelta(days=1)
    return results


def get_week_bounds(week_str: str) -> tuple[date, date]:
    try:
        year, week = map(int, week_str.split("-"))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid week format") from exc
    start = datetime.fromisocalendar(year, week, 1).date()
    end = start + timedelta(days=6)
    return start, end


def compute_streak(session: Session, model, user_id: int, date_column) -> int:
    today = date.today()
    streak = 0
    current_day = today
    while True:
        statement = select(func.count()).where(
            getattr(model, "user_id") == user_id,
            date_column == current_day,
        )
        count = session.exec(statement).one()[0]
        if count == 0:
            break
        streak += 1
        current_day -= timedelta(days=1)
    return streak


def compute_streaks(session: Session, user_id: int) -> Dict[str, int]:
    return {
        "daily_log": compute_streak(session, DailyLog, user_id, DailyLog.date),
        "workout": compute_streak(session, Workout, user_id, Workout.date),
    }


def compute_prs(session: Session, user_id: int) -> List[dict]:
    stmt = select(PR).where(PR.user_id == user_id).order_by(PR.date.desc()).limit(5)
    return [pr.dict() for pr in session.exec(stmt).all()]


def calculate_pr_candidates(sets: List[WorkoutSet]) -> Dict[int, Dict[int, WorkoutSet]]:
    best: Dict[int, Dict[int, WorkoutSet]] = defaultdict(dict)
    for workout_set in sets:
        exercise_best = best.setdefault(workout_set.exercise_id, {})
        current = exercise_best.get(workout_set.reps)
        if current is None or workout_set.weight > current.weight:
            exercise_best[workout_set.reps] = workout_set
    return best


def export_entities(session: Session, user_id: int) -> Dict[str, List[dict]]:
    data: Dict[str, List[dict]] = {}
    direct_models = [Task, DailyLog, Workout, Project, PR]
    for model in direct_models:
        stmt = select(model).where(getattr(model, "user_id") == user_id)
        records = [row.dict() for row in session.exec(stmt).all()]
        data[model.__tablename__] = records

    workout_sets = session.exec(
        select(WorkoutSet)
        .join(Workout)
        .where(Workout.user_id == user_id)
    ).all()
    data[WorkoutSet.__tablename__] = [row.dict() for row in workout_sets]

    project_updates = session.exec(
        select(ProjectUpdate)
        .join(Project)
        .where(Project.user_id == user_id)
    ).all()
    data[ProjectUpdate.__tablename__] = [row.dict() for row in project_updates]
    return data


def compute_dashboard(session: Session, user, week: str) -> Dict[str, object]:
    week_start, week_end = get_week_bounds(week)
    tasks = session.exec(
        select(Task).where(
            Task.user_id == user.id,
            Task.due_date >= week_start,
            Task.due_date <= week_end,
        )
    ).all()
    total_tasks = len(tasks)
    completed = len([task for task in tasks if task.status == "done"])
    overdue = len([task for task in tasks if task.due_date and task.due_date < date.today() and task.status != "done"])
    completion = (completed / total_tasks) * 100 if total_tasks else 0

    workouts = session.exec(
        select(Workout).where(Workout.user_id == user.id, Workout.date >= week_start, Workout.date <= week_end)
    ).all()
    sets = session.exec(
        select(WorkoutSet).join(Workout).where(
            Workout.user_id == user.id,
            Workout.date >= week_start,
            Workout.date <= week_end,
        )
    ).all()
    volume_by_exercise: Dict[int, float] = defaultdict(float)
    for workout_set in sets:
        volume_by_exercise[workout_set.exercise_id] += workout_set.weight * workout_set.reps

    active_projects = session.exec(select(Project).where(Project.user_id == user.id, Project.status == "active")).all()
    project_updates = session.exec(
        select(ProjectUpdate).join(Project).where(Project.user_id == user.id).order_by(ProjectUpdate.date.desc())
    ).all()
    last_update_by_project: Dict[int, date | None] = {}
    for update in project_updates:
        last_update_by_project.setdefault(update.project_id, update.date)

    streaks = compute_streaks(session, user.id)

    return {
        "task_completion_percent": round(completion, 2),
        "overdue_tasks": overdue,
        "workout_totals": {
            "sessions": len(workouts),
            "sets": len(sets),
            "volume_by_exercise": volume_by_exercise,
        },
        "latest_prs": compute_prs(session, user.id),
        "active_projects": [
            {
                "id": project.id,
                "title": project.title,
                "last_update": last_update_by_project.get(project.id),
            }
            for project in active_projects
        ],
        "streaks": streaks,
    }
