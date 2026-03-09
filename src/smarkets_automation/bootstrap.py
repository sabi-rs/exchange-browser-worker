from pathlib import Path


COPY_NAMES = [
    "Cookies",
    "Login Data",
    "Web Data",
    "Preferences",
    "Local Storage",
    "Session Storage",
    "Network",
]


def ensure_copyable_helium_profile(source: Path) -> None:
    if (source / "LOCK").exists():
        raise RuntimeError(
            "Helium must be closed before bootstrapping the automation profile"
        )


def planned_copy_paths(source: Path) -> list[Path]:
    return [source / name for name in COPY_NAMES if (source / name).exists()]
