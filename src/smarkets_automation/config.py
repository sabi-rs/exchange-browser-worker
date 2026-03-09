from dataclasses import dataclass
from pathlib import Path


DEFAULT_HELIUM_ROOT = Path("~/.config/net.imput.helium").expanduser()


@dataclass(frozen=True)
class AppPaths:
    app_dir: Path
    profile_dir: Path
    logs_dir: Path

    @classmethod
    def from_home(cls, home: Path) -> "AppPaths":
        app_dir = home / ".config" / "smarkets-automation"
        return cls(
            app_dir=app_dir,
            profile_dir=app_dir / "profile",
            logs_dir=app_dir / "logs",
        )


def detect_helium_profile(helium_root: Path = DEFAULT_HELIUM_ROOT) -> Path:
    profile_dir = helium_root / "Default"
    if not profile_dir.is_dir():
        raise FileNotFoundError(f"Helium profile not found at {profile_dir}")
    return profile_dir
