from app.models import WorkoutSet
from app.utils import calculate_pr_candidates


def test_calculate_pr_candidates():
    sets = [
        WorkoutSet(workout_id=1, exercise_id=1, set_number=1, weight=100, reps=5),
        WorkoutSet(workout_id=1, exercise_id=1, set_number=2, weight=105, reps=5),
        WorkoutSet(workout_id=1, exercise_id=1, set_number=3, weight=90, reps=8),
        WorkoutSet(workout_id=2, exercise_id=2, set_number=1, weight=60, reps=10),
    ]
    prs = calculate_pr_candidates(sets)
    assert prs[1][5].weight == 105
    assert prs[1][5].set_number == 2
    assert prs[2][10].weight == 60
