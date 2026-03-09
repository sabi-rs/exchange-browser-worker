import os

import pytest

from smarkets_automation.cli import load_standard_market_snapshot


DEFAULT_LIVE_EVENT_URL = (
    "https://smarkets.com/football/england-premier-league/"
    "2026/03/14/17-30/arsenal-vs-everton/44919794/"
)


@pytest.mark.skipif(os.environ.get("SMARKETS_LIVE") != "1", reason="live smoke disabled")
def test_show_market_live_smoke() -> None:
    event_url = os.environ.get("SMARKETS_LIVE_EVENT_URL", DEFAULT_LIVE_EVENT_URL)

    snapshot = load_standard_market_snapshot(event_url)

    assert snapshot.market_name == "Full-time result"
    assert "Arsenal" in snapshot.contract_labels()
