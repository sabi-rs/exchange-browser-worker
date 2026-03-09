import os
import re
from pathlib import Path

import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import expect, sync_playwright

from smarkets_automation.config import AppPaths


@pytest.mark.skipif(os.environ.get("SMARKETS_LIVE") != "1", reason="live smoke disabled")
def test_login_or_member_page_opens_from_owned_profile() -> None:
    profile_dir = AppPaths.from_home(Path.home()).profile_dir
    profile_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=True,
        )
        page = context.pages[0] if context.pages else context.new_page()

        try:
            page.goto("https://smarkets.com", wait_until="domcontentloaded")
            expect(page).to_have_title(re.compile("Smarkets"))

            login_button = page.get_by_role("button", name="Log in")
            try:
                login_button.wait_for(state="visible", timeout=5000)
            except PlaywrightTimeoutError:
                assert page.url.startswith("https://smarkets.com/")
            else:
                login_button.click()
                expect(page).to_have_url(re.compile(r"login=true"))
                expect(page.get_by_role("textbox").first).to_be_visible()
        finally:
            context.close()
