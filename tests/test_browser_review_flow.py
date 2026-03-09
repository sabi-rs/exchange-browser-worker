from pathlib import Path

import pytest

from smarkets_automation import cli
from smarkets_automation.browser import (
    CONTRACT_ROW_SELECTOR,
    PRIMARY_MARKET_SELECTOR,
    SLIP_CONTRACT_SELECTOR,
    SLIP_SIDE_TOGGLE_SELECTOR,
    STAKE_INPUT_SELECTOR,
    assert_live_quote_matches_preflight,
    assert_populated_bet_slip_matches_preflight,
    bet_button_css_selector,
    bet_button_locator_text,
    fill_stake_input,
    primary_market_contract_row,
    wait_for_contract_rows,
)
from smarkets_automation.market_snapshot import (
    StandardContractSnapshot,
    StandardMarketSnapshot,
)
from smarkets_automation.orders import PreflightPlan


def test_bet_button_locator_text_uses_contract_and_side() -> None:
    assert bet_button_locator_text("Arsenal", "buy") == "Arsenal|buy"


def test_bet_button_css_selector_uses_side_specific_button_class() -> None:
    assert bet_button_css_selector("buy") == "button[class*='BetButton_buy']"
    assert bet_button_css_selector("sell") == "button[class*='BetButton_sell']"


def test_wait_for_contract_rows_waits_for_contract_row_selector() -> None:
    waited: dict[str, str] = {}

    class FakePage:
        def wait_for_selector(self, selector: str) -> None:
            waited["selector"] = selector

    wait_for_contract_rows(FakePage())

    assert waited["selector"] == CONTRACT_ROW_SELECTOR


def test_primary_market_contract_row_scopes_lookup_to_primary_market() -> None:
    calls: list[tuple[str, object]] = []

    class FakeRowLocator:
        first = None

        def __init__(self) -> None:
            self.first = self

    fake_row = FakeRowLocator()

    class FakeMarketLocator:
        first = None

        def __init__(self) -> None:
            self.first = self

        def locator(self, selector: str) -> "FakeMarketLocator":
            calls.append(("market.locator", selector))
            return self

        def filter(self, *, has: object) -> FakeRowLocator:
            calls.append(("market.filter", has))
            return fake_row

    fake_market = FakeMarketLocator()

    class FakePage:
        def locator(self, selector: str) -> FakeMarketLocator:
            calls.append(("page.locator", selector))
            return fake_market

        def get_by_text(self, text: str, exact: bool = False) -> str:
            calls.append(("page.get_by_text", (text, exact)))
            return f"text:{text}:{exact}"

    contract_row = primary_market_contract_row(FakePage(), "Arsenal")

    assert contract_row is fake_row
    assert calls == [
        ("page.locator", PRIMARY_MARKET_SELECTOR),
        ("market.locator", CONTRACT_ROW_SELECTOR),
        ("page.get_by_text", ("Arsenal", True)),
        ("market.filter", "text:Arsenal:True"),
    ]


def test_fill_stake_input_fills_requested_stake() -> None:
    filled: dict[str, str] = {}

    class FakeStakeInput:
        first = None

        def __init__(self) -> None:
            self.first = self

        def count(self) -> int:
            return 1

        def fill(self, value: str) -> None:
            filled["value"] = value

    fake_input = FakeStakeInput()

    class FakePage:
        def wait_for_selector(self, selector: str) -> None:
            filled["waited_for"] = selector

        def locator(self, selector: str) -> FakeStakeInput:
            filled["selector"] = selector
            return fake_input

    fill_stake_input(FakePage(), "10")

    assert filled == {
        "waited_for": STAKE_INPUT_SELECTOR,
        "selector": STAKE_INPUT_SELECTOR,
        "value": "10",
    }


def test_fill_stake_input_fails_closed_when_input_is_missing() -> None:
    class MissingStakeInput:
        first = None

        def __init__(self) -> None:
            self.first = self

        def count(self) -> int:
            return 0

    class FakePage:
        def wait_for_selector(self, selector: str) -> None:
            assert selector == STAKE_INPUT_SELECTOR

        def locator(self, selector: str) -> MissingStakeInput:
            assert selector == STAKE_INPUT_SELECTOR
            return MissingStakeInput()

    with pytest.raises(ValueError, match="Stake input was not found on the live page"):
        fill_stake_input(FakePage(), "10")


def test_assert_live_quote_matches_preflight_fails_closed_on_quote_drift() -> None:
    class FakeButton:
        first = None

        def __init__(self) -> None:
            self.first = self

        def inner_text(self) -> str:
            return "72%"

    class FakeContractRow:
        def locator(self, selector: str) -> FakeButton:
            assert selector == bet_button_css_selector("buy")
            return FakeButton()

    with pytest.raises(ValueError, match="Live quote drift detected"):
        assert_live_quote_matches_preflight(
            FakeContractRow(),
            PreflightPlan(
                event_url="https://smarkets.com/football/example",
                contract_label="Arsenal",
                side="buy",
                stake="10",
                expected_percent="74%",
                confirm=True,
            ),
        )


def test_assert_populated_bet_slip_matches_preflight_checks_contract_side_and_stake() -> None:
    class FakeSlipValue:
        def __init__(self, text: str) -> None:
            self._text = text
            self.first = self

        def count(self) -> int:
            return 1

        def inner_text(self) -> str:
            return self._text

        def input_value(self) -> str:
            return self._text

    class FakePage:
        def locator(self, selector: str) -> FakeSlipValue:
            if selector == SLIP_CONTRACT_SELECTOR:
                return FakeSlipValue("Selected contractArsenal")
            if selector == SLIP_SIDE_TOGGLE_SELECTOR:
                return FakeSlipValue("Buy")
            if selector == STAKE_INPUT_SELECTOR:
                return FakeSlipValue("10")
            raise AssertionError(selector)

    assert_populated_bet_slip_matches_preflight(
        FakePage(),
        PreflightPlan(
            event_url="https://smarkets.com/football/example",
            contract_label="Arsenal",
            side="buy",
            stake="10",
            expected_percent="74%",
            confirm=False,
        ),
    )


def test_place_bet_review_mode_calls_review_execution(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    called: dict[str, object] = {}
    monkeypatch.setattr(cli.Path, "home", lambda: tmp_path)
    monkeypatch.setattr(
        cli,
        "load_standard_market_snapshot",
        lambda event_url: StandardMarketSnapshot(
            event_url=event_url,
            market_name="Full-time result",
            contracts=[
                StandardContractSnapshot("Arsenal", "73%", "74%"),
                StandardContractSnapshot("Draw", "18%", "19%"),
            ],
        ),
    )
    monkeypatch.setattr(cli, "write_action_log", lambda logs_dir, payload: tmp_path / "mock-log.json")
    monkeypatch.setattr(cli, "execute_confirm_bet", lambda profile_dir, plan: None)
    monkeypatch.setattr(
        cli,
        "execute_review_bet",
        lambda profile_dir, plan: called.setdefault("profile_dir", profile_dir),
    )

    exit_code = cli.main(
        [
            "place-bet",
            "--event-url",
            "https://smarkets.com/football/example",
            "--contract",
            "Arsenal",
            "--side",
            "buy",
            "--stake",
            "10",
        ],
    )

    assert exit_code == 0
    assert called["profile_dir"] == Path(tmp_path) / ".config" / "smarkets-automation" / "profile"
