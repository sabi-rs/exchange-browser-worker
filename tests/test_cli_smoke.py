import tomllib
import os
from pathlib import Path
import subprocess
import sys

import pytest

from smarkets_automation.cli import build_parser


EXPECTED_COMMANDS = {
    "bootstrap-session",
    "login",
    "search-events",
    "show-market",
    "place-bet",
}


def test_build_parser_exposes_expected_commands() -> None:
    parser = build_parser()

    for command in EXPECTED_COMMANDS - {"place-bet"}:
        if command == "show-market":
            assert (
                parser.parse_args(
                    ["show-market", "--event-url", "https://smarkets.com/example"],
                ).command
                == command
            )
            continue
        if command == "search-events":
            assert parser.parse_args(["search-events", "Arsenal Everton"]).command == command
            continue
        assert parser.parse_args([command]).command == command

    assert (
        parser.parse_args(
            [
                "place-bet",
                "--event-url",
                "https://smarkets.com/example",
                "--contract",
                "Arsenal",
                "--side",
                "buy",
                "--stake",
                "10",
            ],
        ).command
        == "place-bet"
    )

    with pytest.raises(SystemExit) as excinfo:
        parser.parse_args(["unknown-command"])

    assert excinfo.value.code == 2


def test_pyproject_declares_smarkets_console_script() -> None:
    pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    pyproject = tomllib.loads(pyproject_path.read_text())

    assert pyproject["project"]["scripts"]["smarkets"] == "smarkets_automation.cli:main"


def test_python_m_cli_invokes_main() -> None:
    root = Path(__file__).resolve().parents[1]
    env = dict(os.environ)
    env["PYTHONPATH"] = str(root / "src")

    result = subprocess.run(
        [sys.executable, "-m", "smarkets_automation.cli", "--help"],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "usage:" in result.stdout
