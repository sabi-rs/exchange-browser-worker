from pathlib import Path


def _ensure_owned_profile_dir(profile_dir: Path) -> Path:
    resolved_profile_dir = profile_dir.expanduser()
    if resolved_profile_dir.parts[-2:] == ("net.imput.helium", "Default"):
        raise ValueError("Browser automation must use the owned profile, not the live Helium profile")
    return resolved_profile_dir


def browser_launch_args(profile_dir: Path) -> list[str]:
    owned_profile_dir = _ensure_owned_profile_dir(profile_dir)
    return [f"--user-data-dir={owned_profile_dir}"]


def launch_login_browser(profile_dir: Path) -> None:
    owned_profile_dir = _ensure_owned_profile_dir(profile_dir)
    owned_profile_dir.mkdir(parents=True, exist_ok=True)

    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(owned_profile_dir),
            headless=False,
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://smarkets.com")

        try:
            while context.pages:
                context.pages[0].wait_for_timeout(1000)
        finally:
            context.close()
