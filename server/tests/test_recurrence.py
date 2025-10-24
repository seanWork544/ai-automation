from datetime import date

from app.utils import compute_recurrence


def test_compute_recurrence_weekdays():
    start = date(2024, 1, 1)  # Monday
    instances = compute_recurrence("BYDAY=MO,WE,FR", start, weeks=1)
    assert instances == ["2024-01-01", "2024-01-03", "2024-01-05"]
