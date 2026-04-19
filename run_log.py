import json
from datetime import datetime, timezone
from pathlib import Path

LOG_PATH = Path(__file__).parent / "run_log.json"


def read_log() -> list:
    if not LOG_PATH.exists():
        return []
    with open(LOG_PATH) as f:
        return json.load(f)


def write_log(month: str, success: bool, error: str = "") -> None:
    log = read_log()
    log.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "month": month,
        "success": success,
        "error": error,
    })
    with open(LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)
