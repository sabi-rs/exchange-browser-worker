import json
from datetime import datetime, timezone
from pathlib import Path


def write_action_log(logs_dir: Path, payload: dict[str, object]) -> Path:
    logs_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc)
    log_path = logs_dir / f"{timestamp.strftime('%Y%m%dT%H%M%S%fZ')}.json"
    log_payload = {**payload, "timestamp": timestamp.isoformat()}
    log_path.write_text(json.dumps(log_payload, indent=2, sort_keys=True))
    return log_path
