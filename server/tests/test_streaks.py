from datetime import date, timedelta

from app.models import DailyLog, Workout
from app.utils import compute_streaks


def test_compute_streaks(session):
    today = date.today()
    logs = [DailyLog(user_id=1, date=today - timedelta(days=i), summary=f"Log {i}") for i in range(3)]
    workouts = [Workout(user_id=1, date=today - timedelta(days=i), title=f"Workout {i}") for i in range(2)]
    session.add_all(logs + workouts)
    session.commit()

    streaks = compute_streaks(session, user_id=1)
    assert streaks["daily_log"] == 3
    assert streaks["workout"] == 2
