from services.streak_engine import update_streak_on_completion, streak_days_grid


def test_streak_starts_on_first_activity_and_stays_same_day():
    first = update_streak_on_completion(None)
    assert first["current_streak"] == 1
    assert first["longest_streak"] == 1

    same_day = update_streak_on_completion(first)
    assert same_day["current_streak"] == 1
    assert same_day["longest_streak"] == 1

    grid = streak_days_grid(first)
    assert len(grid) == 7
    assert grid[-1] is True
