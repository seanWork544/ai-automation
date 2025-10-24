from datetime import date, timedelta

from sqlmodel import Session

from .database import engine
from .models import DailyLog, Exercise, PR, Project, ProjectUpdate, Task, TaskTemplate, User, Workout, WorkoutSet
from .security import get_password_hash


def seed() -> None:
    with Session(engine) as session:
        if session.query(User).count():
            return
        user = User(email="demo@example.com", password_hash=get_password_hash("password"))
        session.add(user)
        session.commit()
        session.refresh(user)

        templates = [
            TaskTemplate(user_id=user.id, title="Morning review", context="work", recur_rule="BYDAY=MO,TU,WE,TH,FR"),
            TaskTemplate(user_id=user.id, title="Daily planning", context="work", recur_rule="BYDAY=MO,WE,FR"),
            TaskTemplate(user_id=user.id, title="Gym prep", context="personal", recur_rule="BYDAY=MO,WE,FR"),
            TaskTemplate(user_id=user.id, title="Weekly retro", context="work", recur_rule="BYDAY=FR"),
            TaskTemplate(user_id=user.id, title="Family call", context="personal", recur_rule="BYDAY=SU"),
        ]
        session.add_all(templates)

        today = date.today()
        tasks = [
            Task(user_id=user.id, title="Kickoff sync", context="work", due_date=today, status="doing"),
            Task(user_id=user.id, title="Deep work", context="work", due_date=today + timedelta(days=1)),
            Task(user_id=user.id, title="Groceries", context="personal", due_date=today + timedelta(days=2)),
        ]
        session.add_all(tasks)

        logs = [
            DailyLog(user_id=user.id, date=today - timedelta(days=i), summary=f"Daily reflection {i}")
            for i in range(3)
        ]
        session.add_all(logs)

        exercises = [
            Exercise(user_id=user.id, name="Back Squat", muscle_group="Legs"),
            Exercise(user_id=user.id, name="Bench Press", muscle_group="Chest"),
            Exercise(user_id=user.id, name="Deadlift", muscle_group="Back"),
        ]
        session.add_all(exercises)
        session.flush()

        workout1 = Workout(user_id=user.id, date=today - timedelta(days=2), title="Lower A")
        workout2 = Workout(user_id=user.id, date=today, title="Upper A")
        session.add_all([workout1, workout2])
        session.flush()

        sets = [
            WorkoutSet(workout_id=workout1.id, exercise_id=exercises[0].id, set_number=1, weight=100, reps=5),
            WorkoutSet(workout_id=workout1.id, exercise_id=exercises[0].id, set_number=2, weight=105, reps=5),
            WorkoutSet(workout_id=workout2.id, exercise_id=exercises[1].id, set_number=1, weight=70, reps=8),
        ]
        session.add_all(sets)

        prs = [
            PR(user_id=user.id, exercise_id=exercises[0].id, weight=150, reps=1, date=today - timedelta(days=10)),
            PR(user_id=user.id, exercise_id=exercises[2].id, weight=200, reps=1, date=today - timedelta(days=20)),
        ]
        session.add_all(prs)

        projects = [
            Project(user_id=user.id, title="AI Automation", status="active", context="work"),
            Project(user_id=user.id, title="Home Gym Setup", status="active", context="personal"),
        ]
        session.add_all(projects)
        session.flush()

        updates = []
        for project in projects:
            for i in range(3):
                updates.append(
                    ProjectUpdate(
                        project_id=project.id,
                        date=today - timedelta(days=7 - i * 2),
                        progress_percent=min(100, 30 + i * 30),
                        note=f"Update {i} for {project.title}",
                        how_it_was_done="Placeholder summary",
                    )
                )
        session.add_all(updates)

        session.commit()


if __name__ == "__main__":
    seed()
