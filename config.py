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
# These must be verified against real Radius export files in later tasks.
# Update here if the actual column names differ.
ENROLLMENT_COL_STUDENT = "Student Name"
ENROLLMENT_COL_MONTHS  = "Length of Stay"
ENROLLMENT_COL_CENTER  = "Center"

BIRTHDAY_COL_STUDENT   = "Student Name"
BIRTHDAY_COL_BIRTHDAY  = "Birthday"
BIRTHDAY_COL_CENTER    = "Center"
