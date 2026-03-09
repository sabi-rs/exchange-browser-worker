import json

from smarkets_automation.logging_utils import write_action_log


def test_write_action_log_persists_status_and_event(tmp_path) -> None:
    log_path = write_action_log(
        tmp_path,
        {"status": "review", "event_url": "https://smarkets.com/football/example"},
    )

    payload = json.loads(log_path.read_text())

    assert payload["status"] == "review"
    assert payload["event_url"].startswith("https://smarkets.com/")


def test_write_action_log_does_not_allow_timestamp_override(tmp_path) -> None:
    log_path = write_action_log(
        tmp_path,
        {
            "timestamp": "fake-timestamp",
            "status": "review",
            "event_url": "https://smarkets.com/football/example",
        },
    )

    payload = json.loads(log_path.read_text())

    assert payload["timestamp"] != "fake-timestamp"
