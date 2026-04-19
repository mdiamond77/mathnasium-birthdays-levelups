import pandas as pd
import pytest
from process import calculate_level, get_levelups, get_birthdays, split_by_center

# ── calculate_level ──────────────────────────────────────────────────────────

def test_calculate_level_zero():
    assert calculate_level(0.0) == 1

def test_calculate_level_level1_boundary():
    assert calculate_level(11.9) == 1

def test_calculate_level_level2_start():
    assert calculate_level(12.0) == 2

def test_calculate_level_level2_mid():
    assert calculate_level(18.5) == 2

def test_calculate_level_level3_start():
    assert calculate_level(24.0) == 3

def test_calculate_level_level4_start():
    assert calculate_level(36.0) == 4

def test_calculate_level_level5_start():
    assert calculate_level(48.0) == 5

def test_calculate_level_capped_at_5():
    assert calculate_level(72.0) == 5

# ── get_levelups ─────────────────────────────────────────────────────────────

@pytest.fixture
def enrollment_df():
    return pd.DataFrame({
        "Student First Name": ["Alice", "Bob", "Carol", "Dave", "Eve"],
        "Student Last Name":  ["A",     "B",   "C",     "D",    "E"],
        "StudentLengthof Stay": [12.1, 24.3, 13.0, 5.5, 36.0],
        "Center": ["Englewood", "Englewood", "Teaneck", "Teaneck", "Englewood"],
    })

def test_get_levelups_current_month(enrollment_df):
    result = get_levelups(enrollment_df, current=True)
    names = [r["name"] for r in result]
    assert "Alice A" in names   # 12.1 → level up this month
    assert "Carol C" not in names  # 13.0 → last month
    assert "Bob B" in names     # 24.3 → level up this month
    assert "Dave D" not in names   # 5.5 → not a level-up month
    assert "Eve E" in names     # 36.0 → level up this month

def test_get_levelups_last_month(enrollment_df):
    result = get_levelups(enrollment_df, current=False)
    names = [r["name"] for r in result]
    assert "Carol C" in names      # 13.0 → leveled up last month
    assert "Alice A" not in names  # 12.1 → this month

def test_get_levelups_includes_old_and_new_level(enrollment_df):
    result = get_levelups(enrollment_df, current=True)
    alice = next(r for r in result if r["name"] == "Alice A")
    assert alice["old_level"] == 1
    assert alice["new_level"] == 2

def test_get_levelups_level5_cap(enrollment_df):
    """Students at 60+ months are not in any threshold set — never appear."""
    df = pd.DataFrame({
        "Student First Name": ["Zara"],
        "Student Last Name": ["Z"],
        "StudentLengthof Stay": [60.5],
        "Center": ["Englewood"],
    })
    assert get_levelups(df, current=True) == []
    assert get_levelups(df, current=False) == []

def test_get_levelups_sorted_by_name(enrollment_df):
    result = get_levelups(enrollment_df, current=True)
    names = [r["name"] for r in result]
    assert names == sorted(names)

# ── get_birthdays ─────────────────────────────────────────────────────────────

@pytest.fixture
def birthday_df():
    return pd.DataFrame({
        "Student First Name": ["Alice", "Bob", "Carol"],
        "Last Name":          ["A",     "B",   "C"],
        "Birthday": ["1915-04-03", "1913-11-17", "1918-04-22"],
        "Center": ["Englewood", "Englewood", "Teaneck"],
    })

def test_get_birthdays_returns_only_this_month(birthday_df):
    result = get_birthdays(birthday_df, month=4)
    names = [r["name"] for r in result]
    assert "Alice A" in names
    assert "Carol C" in names
    assert "Bob B" not in names  # November birthday

def test_get_birthdays_formats_date(birthday_df):
    result = get_birthdays(birthday_df, month=4)
    alice = next(r for r in result if r["name"] == "Alice A")
    assert alice["birthday"] == "Apr 3"

def test_get_birthdays_calculates_age(birthday_df):
    result = get_birthdays(birthday_df, month=4)
    alice = next(r for r in result if r["name"] == "Alice A")
    from datetime import date
    expected_age = date.today().year - 1915
    assert alice["age"] == expected_age

def test_get_birthdays_sorted_by_day(birthday_df):
    result = get_birthdays(birthday_df, month=4)
    days = [r["_day"] for r in result]
    assert days == sorted(days)

# ── split_by_center ───────────────────────────────────────────────────────────

def test_split_by_center(enrollment_df):
    result = split_by_center(enrollment_df, center_col="Center")
    assert set(result.keys()) == {"Englewood", "Teaneck"}
    assert len(result["Englewood"]) == 3
    assert len(result["Teaneck"]) == 2
