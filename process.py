from datetime import date

import pandas as pd

from config import (
    ENROLLMENT_COL_FIRST,
    ENROLLMENT_COL_LAST,
    ENROLLMENT_COL_MONTHS,
    ENROLLMENT_COL_CENTER,
    BIRTHDAY_COL_FIRST,
    BIRTHDAY_COL_LAST,
    BIRTHDAY_COL_BIRTHDAY,
    BIRTHDAY_COL_CENTER,
    CENTERS,
)

CURRENT_MONTH_THRESHOLDS = {12, 24, 36, 48}
LAST_MONTH_THRESHOLDS = {13, 25, 37, 49}


def calculate_level(months: float) -> int:
    """Return the Mathnasium level for a given length of stay in months.
    Levels: 1 (0-11mo), 2 (12-23mo), 3 (24-35mo), 4 (36-47mo), 5 (48+mo, capped).
    """
    return min(int(months // 12) + 1, 5)


def get_levelups(df: pd.DataFrame, current: bool) -> list[dict]:
    """Return students who leveled up this month (current=True) or last month (current=False).

    Returns list of dicts: {name, old_level, new_level}. Sorted by name.
    """
    thresholds = CURRENT_MONTH_THRESHOLDS if current else LAST_MONTH_THRESHOLDS
    results = []
    for _, row in df.iterrows():
        months = float(str(row[ENROLLMENT_COL_MONTHS]).replace(" months", "").strip())
        if int(months) in thresholds:
            new_level = calculate_level(months)
            name = f"{row[ENROLLMENT_COL_FIRST]} {row[ENROLLMENT_COL_LAST]}"
            results.append({
                "name": name,
                "old_level": new_level - 1,
                "new_level": new_level,
            })
    return sorted(results, key=lambda x: x["name"])


def get_birthdays(df: pd.DataFrame, month: int) -> list[dict]:
    """Return students with birthdays in the given month (1=Jan, 12=Dec).

    Returns list of dicts: {name, birthday, age, _day}. Sorted by day.
    """
    results = []
    today = date.today()
    for _, row in df.iterrows():
        bday = pd.to_datetime(row[BIRTHDAY_COL_BIRTHDAY])
        if bday.month == month:
            age = today.year - bday.year
            name = f"{row[BIRTHDAY_COL_FIRST]} {row[BIRTHDAY_COL_LAST]}"
            results.append({
                "name": name,
                "birthday": "{} {}".format(bday.strftime("%b"), bday.day),
                "age": age,
                "_day": bday.day,
            })
    return sorted(results, key=lambda x: x["_day"])


def split_by_center(df: pd.DataFrame, center_col: str) -> dict:
    """Split a DataFrame into {center_name: sub-DataFrame}."""
    return {
        center: group.reset_index(drop=True)
        for center, group in df.groupby(center_col)
    }


def process(enrollment_path, birthdays_path, month: int) -> dict:
    """Load both reports, split by center, compute level-ups and birthdays.

    Returns:
        {
          "Englewood": {"current_levelups": [...], "last_levelups": [...], "birthdays": [...]},
          "Teaneck":   {"current_levelups": [...], "last_levelups": [...], "birthdays": [...]},
        }
    """
    enrollment_df = pd.read_excel(enrollment_path)
    birthdays_df = pd.read_excel(birthdays_path)

    if enrollment_df.empty:
        raise ValueError("Enrollment report is empty — check Radius filters and re-run.")
    if birthdays_df.empty:
        raise ValueError("Birthday report is empty — check Radius filters and re-run.")

    enrollment_by_center = split_by_center(enrollment_df, ENROLLMENT_COL_CENTER)
    birthdays_by_center = split_by_center(birthdays_df, BIRTHDAY_COL_CENTER)

    for center_name in CENTERS:
        if center_name not in enrollment_by_center:
            raise ValueError(
                "Center '{}' missing from enrollment report. "
                "Check that both centers were selected before export.".format(center_name)
            )

    result = {}
    for center_name in CENTERS:
        enroll = enrollment_by_center[center_name]
        bdays = birthdays_by_center.get(
            center_name, pd.DataFrame(columns=birthdays_df.columns)
        )
        result[center_name] = {
            "current_levelups": get_levelups(enroll, current=True),
            "last_levelups": get_levelups(enroll, current=False),
            "birthdays": get_birthdays(bdays, month=month),
        }
    return result
