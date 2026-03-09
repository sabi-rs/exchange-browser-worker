from pathlib import Path

import pytest

from smarkets_automation import cli
from smarkets_automation.browser import (
    CONTRACT_ROW_SELECTOR,
    bet_button_css_selector,
    bet_button_locator_text,
    wait_for_contract_rows,
)
from smarkets_automation.market_snapshot import (
    StandardContractSnapshot,
    StandardMarketSnapshot,
)


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
