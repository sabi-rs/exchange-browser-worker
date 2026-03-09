from pathlib import Path

from smarkets_automation.orders import PreflightPlan


PRIMARY_MARKET_SELECTOR = "div[class*='CompetitorsEventPrimaryMarket_primaryContracts']"
CONTRACT_ROW_SELECTOR = "div[class*='ContractRow_row']"
SLIP_CONTRACT_SELECTOR = "[aria-label='Selected contract']"
SLIP_SIDE_TOGGLE_SELECTOR = "button[aria-label='Toggle side']"
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


def assert_live_quote_matches_preflight(contract_row, plan: PreflightPlan) -> None:
    actual_percent = contract_row.locator(bet_button_css_selector(plan.side)).first.inner_text().strip()
    if actual_percent != plan.expected_percent:
        raise ValueError("Live quote drift detected for requested selection")


def fill_stake_input(page, stake: str) -> None:
    page.wait_for_selector(STAKE_INPUT_SELECTOR)
    stake_input = page.locator(STAKE_INPUT_SELECTOR).first
    if stake_input.count() == 0:
        raise ValueError("Stake input was not found on the live page")
    stake_input.fill(stake)


def assert_populated_bet_slip_matches_preflight(page, plan: PreflightPlan) -> None:
    slip_contract = page.locator(SLIP_CONTRACT_SELECTOR).first
    slip_side = page.locator(SLIP_SIDE_TOGGLE_SELECTOR).first
    stake_input = page.locator(STAKE_INPUT_SELECTOR).first

    if slip_contract.count() == 0 or slip_side.count() == 0 or stake_input.count() == 0:
        raise ValueError("Live bet slip did not populate required fields")
    if plan.contract_label not in slip_contract.inner_text():
        raise ValueError("Live bet slip contract does not match preflight")
    if plan.side.capitalize() not in slip_side.inner_text():
        raise ValueError("Live bet slip side does not match preflight")
    if stake_input.input_value().strip() != plan.stake:
        raise ValueError("Live bet slip stake does not match preflight")


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

    assert_live_quote_matches_preflight(contract_row, plan)
    side_button.first.click()
    fill_stake_input(page, plan.stake)
    assert_populated_bet_slip_matches_preflight(page, plan)
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
