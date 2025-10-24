from datetime import date

from app.models import DailyLog, Exercise, Project, ProjectUpdate, Task, Workout, WorkoutSet
from app.utils import export_entities


def test_export_entities_structure(session):
    task = Task(user_id=1, title="Test", context="work", due_date=date.today())
    log = DailyLog(user_id=1, date=date.today(), summary="Summary")
    workout = Workout(user_id=1, date=date.today(), title="Session")
    project = Project(user_id=1, title="Project", context="work")
    exercise = Exercise(user_id=1, name="Squat")
    session.add_all([task, log, workout, project, exercise])
    session.commit()

    workout_set = WorkoutSet(workout_id=workout.id, exercise_id=exercise.id, set_number=1, weight=100, reps=5)
    update = ProjectUpdate(project_id=project.id, date=date.today(), progress_percent=10)
    session.add_all([workout_set, update])
    session.commit()

    data = export_entities(session, user_id=1)
    assert "tasks" in data
    assert any(item["title"] == "Test" for item in data["tasks"])
    assert "workout_sets" in data
    assert len(data["workout_sets"]) == 1
    assert data["project_updates"][0]["project_id"] == project.id
