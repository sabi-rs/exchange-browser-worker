from pathlib import Path

import pytest

from smarkets_automation import cli
from smarkets_automation.config import AppPaths
from smarkets_automation.browser import browser_launch_args


def test_browser_launch_args_point_to_owned_profile(tmp_path: Path) -> None:
    profile_dir = tmp_path / "profile"

    args = browser_launch_args(profile_dir)

    assert "--user-data-dir" in args[0]
    assert str(profile_dir) in args[0]


def test_browser_launch_args_do_not_point_to_helium_source_profile(tmp_path: Path) -> None:
    owned_profile_dir = tmp_path / "profile"

    args = browser_launch_args(owned_profile_dir)

    assert str(owned_profile_dir) in args[0]


def test_browser_launch_args_reject_live_helium_profile(tmp_path: Path) -> None:
    helium_profile_dir = tmp_path / "net.imput.helium" / "Default"

    with pytest.raises(ValueError):
        browser_launch_args(helium_profile_dir)


def test_login_launches_browser_with_owned_profile(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    launched: dict[str, Path] = {}
    expected_paths = AppPaths.from_home(tmp_path)

    monkeypatch.setattr(cli.Path, "home", lambda: tmp_path)
    monkeypatch.setattr(
        cli,
        "launch_login_browser",
        lambda profile_dir: launched.setdefault("profile_dir", profile_dir),
    )

    exit_code = cli.main(["login"])

    assert exit_code == 0
    assert launched["profile_dir"] == expected_paths.profile_dir
