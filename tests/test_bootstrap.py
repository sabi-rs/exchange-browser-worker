from pathlib import Path

import pytest

from smarkets_automation.bootstrap import (
    ensure_copyable_helium_profile,
    planned_copy_paths,
)
from smarkets_automation.cli import main


def test_copy_refuses_when_helium_lock_exists(tmp_path: Path):
    source = tmp_path / "Default"
    source.mkdir()
    (source / "LOCK").write_text("")

    with pytest.raises(RuntimeError):
        ensure_copyable_helium_profile(source)


def test_ensure_copyable_helium_profile_allows_profile_without_lock(tmp_path: Path):
    source = tmp_path / "Default"
    source.mkdir()

    ensure_copyable_helium_profile(source)


def test_planned_copy_paths_include_cookie_and_storage_files(tmp_path: Path):
    source = tmp_path / "Default"
    source.mkdir()
    (source / "Cookies").write_text("")
    (source / "Local Storage").mkdir()

    planned = planned_copy_paths(source)

    assert source / "Cookies" in planned
    assert source / "Local Storage" in planned


def test_bootstrap_session_enforces_copyable_profile_rule(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    called_with: list[Path] = []

    def fake_detect_helium_profile() -> Path:
        return tmp_path / "Default"

    def fake_ensure_copyable_helium_profile(source: Path) -> None:
        called_with.append(source)
        raise RuntimeError("Helium must be closed before bootstrapping the automation profile")

    monkeypatch.setattr(
        "smarkets_automation.cli.detect_helium_profile",
        fake_detect_helium_profile,
    )
    monkeypatch.setattr(
        "smarkets_automation.cli.ensure_copyable_helium_profile",
        fake_ensure_copyable_helium_profile,
    )

    with pytest.raises(
        RuntimeError,
        match="Helium must be closed before bootstrapping the automation profile",
    ):
        main(["bootstrap-session"])

    assert called_with == [tmp_path / "Default"]
