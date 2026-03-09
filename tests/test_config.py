from pathlib import Path

import pytest

from smarkets_automation.config import AppPaths, detect_helium_profile


def test_detect_helium_profile_uses_default_profile_dir(tmp_path: Path):
    helium_root = tmp_path / "net.imput.helium"
    profile = helium_root / "Default"
    profile.mkdir(parents=True)

    detected = detect_helium_profile(helium_root)

    assert detected == profile


@pytest.mark.parametrize("default_is_dir", [False, None])
def test_detect_helium_profile_rejects_missing_or_non_directory_default(
    tmp_path: Path,
    default_is_dir: bool | None,
):
    helium_root = tmp_path / "net.imput.helium"
    helium_root.mkdir()

    default_path = helium_root / "Default"
    if default_is_dir is False:
        default_path.write_text("")

    with pytest.raises(FileNotFoundError):
        detect_helium_profile(helium_root)


def test_app_paths_nest_under_config_home(tmp_path: Path):
    paths = AppPaths.from_home(tmp_path)

    assert paths.app_dir == tmp_path / ".config" / "smarkets-automation"
    assert paths.profile_dir == paths.app_dir / "profile"
    assert paths.logs_dir == paths.app_dir / "logs"
