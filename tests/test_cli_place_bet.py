from pathlib import Path

import pytest

from smarkets_automation import cli
from smarkets_automation.config import AppPaths
from smarkets_automation.cli import main


def test_place_bet_review_mode_prints_preflight_summary(
    capsys,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(cli, "write_action_log", lambda logs_dir, payload: tmp_path / "mock-log.json")
    monkeypatch.setattr(cli.Path, "home", lambda: tmp_path)

    exit_code = main(
        [
            "place-bet",
            "--event-url",
            "https://smarkets.com/football/example",
            "--contract",
            "Arsenal",
            "--available-contract",
            "Arsenal",
            "--available-contract",
            "Draw",
            "--available-contract",
            "Everton",
            "--side",
            "buy",
            "--stake",
            "10",
        ],
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "review" in captured.out.lower()
    assert "arsenal" in captured.out.lower()


@pytest.mark.parametrize(
    ("extra_args", "expected_status"),
    [
        ([], "review"),
        (["--confirm"], "confirm"),
    ],
)
def test_place_bet_writes_audit_log(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    extra_args: list[str],
    expected_status: str,
) -> None:
    captured_log: dict[str, object] = {}

    monkeypatch.setattr(cli.Path, "home", lambda: tmp_path)

    def fake_write_action_log(logs_dir: Path, payload: dict[str, object]) -> Path:
        captured_log["logs_dir"] = logs_dir
        captured_log["payload"] = payload
        return logs_dir / "mock-log.json"

    monkeypatch.setattr(cli, "write_action_log", fake_write_action_log)

    exit_code = main(
        [
            "place-bet",
            "--event-url",
            "https://smarkets.com/football/example",
            "--contract",
            "Arsenal",
            "--available-contract",
            "Arsenal",
            "--available-contract",
            "Draw",
            "--available-contract",
            "Everton",
            "--side",
            "buy",
            "--stake",
            "10",
            *extra_args,
        ],
    )

    assert exit_code == 0
    assert captured_log["logs_dir"] == AppPaths.from_home(tmp_path).logs_dir
    assert captured_log["payload"] == {
        "status": expected_status,
        "event_url": "https://smarkets.com/football/example",
        "contract_label": "Arsenal",
        "side": "buy",
        "stake": "10",
    }


def test_place_bet_fails_closed_for_unknown_contract(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(cli, "write_action_log", lambda logs_dir, payload: tmp_path / "mock-log.json")
    monkeypatch.setattr(cli.Path, "home", lambda: tmp_path)

    with pytest.raises(ValueError):
        main(
            [
                "place-bet",
                "--event-url",
                "https://smarkets.com/football/example",
                "--contract",
                "Arsenal",
                "--available-contract",
                "Draw",
                "--available-contract",
                "Everton",
                "--side",
                "buy",
                "--stake",
                "10",
            ],
        )
