from pathlib import Path

from smarkets_automation.orders import PreflightPlan


PRIMARY_MARKET_SELECTOR = "div[class*='CompetitorsEventPrimaryMarket_primaryContracts']"
CONTRACT_ROW_SELECTOR = "div[class*='ContractRow_row']"
STAKE_INPUT_SELECTOR = "input[aria-label='Stake input']"


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


def bet_button_locator_text(contract_label: str, side: str) -> str:
    return f"{contract_label}|{side.lower()}"


def bet_button_css_selector(side: str) -> str:
    return f"button[class*='BetButton_{side.lower()}']"


def wait_for_contract_rows(page) -> None:
    page.wait_for_selector(CONTRACT_ROW_SELECTOR)


def primary_market_contract_row(page, contract_label: str):
    return page.locator(PRIMARY_MARKET_SELECTOR).first.locator(CONTRACT_ROW_SELECTOR).filter(
        has=page.get_by_text(contract_label, exact=True),
    ).first


def fill_stake_input(page, stake: str) -> None:
    page.wait_for_selector(STAKE_INPUT_SELECTOR)
    stake_input = page.locator(STAKE_INPUT_SELECTOR).first
    if stake_input.count() == 0:
        raise ValueError("Stake input was not found on the live page")
    stake_input.fill(stake)


def _populate_bet_slip(profile_dir: Path, plan: PreflightPlan):
    owned_profile_dir = _ensure_owned_profile_dir(profile_dir)
    owned_profile_dir.mkdir(parents=True, exist_ok=True)

    from playwright.sync_api import sync_playwright

    playwright = sync_playwright().start()
    context = playwright.chromium.launch_persistent_context(
        user_data_dir=str(owned_profile_dir),
        headless=False,
    )
    page = context.pages[0] if context.pages else context.new_page()
    page.goto(plan.event_url, wait_until="domcontentloaded")
    wait_for_contract_rows(page)

    contract_row = primary_market_contract_row(page, plan.contract_label)
    if contract_row.count() == 0:
        context.close()
        playwright.stop()
        raise ValueError("Contract row was not found on the live page")

    side_button = contract_row.locator(bet_button_css_selector(plan.side))
    if side_button.count() == 0:
        context.close()
        playwright.stop()
        raise ValueError("Requested side button was not found on the live page")

    side_button.first.click()
    fill_stake_input(page, plan.stake)
    return playwright, context, page


def execute_review_bet(profile_dir: Path, plan: PreflightPlan) -> None:
    playwright, context, _page = _populate_bet_slip(profile_dir, plan)
    context.close()
    playwright.stop()


def execute_confirm_bet(profile_dir: Path, plan: PreflightPlan) -> None:
    playwright, context, page = _populate_bet_slip(profile_dir, plan)
    submit_button = page.get_by_role("button", name="Place bet")
    if submit_button.count() == 0:
        context.close()
        playwright.stop()
        raise ValueError("Final submit button was not found on the live page")
    submit_button.first.click()
    context.close()
    playwright.stop()
