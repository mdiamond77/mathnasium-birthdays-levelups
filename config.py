import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR / "input"

# ── Radius ────────────────────────────────────────────────────────────────────
# Verify this URL against ~/mathnasium-page-goals/download.py
RADIUS_LOGIN_URL = "https://go.mathnasium.com/"

CENTERS = {
    "Englewood": {
        "radius_id": "2428",
        "recipient": "englewood@mathnasium.com",
    },
    "Teaneck": {
        "radius_id": "2871",
        "recipient": "teaneck@mathnasium.com",
    },
}
CC_RECIPIENT = "matt.diamond@mathnasium.com"

# ── Column names ──────────────────────────────────────────────────────────────
# Enrollment Report columns (verified against real Radius export)
ENROLLMENT_COL_FIRST   = "Student First Name"
ENROLLMENT_COL_LAST    = "Student Last Name"
ENROLLMENT_COL_MONTHS  = "StudentLengthof Stay"
ENROLLMENT_COL_CENTER  = "Center"

# Birthday Report columns (verified against real Radius export)
BIRTHDAY_COL_FIRST     = "Student First Name"
BIRTHDAY_COL_LAST      = "Last Name"
BIRTHDAY_COL_BIRTHDAY  = "Birthday"
BIRTHDAY_COL_CENTER    = "Center"
