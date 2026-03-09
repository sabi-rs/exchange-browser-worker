from smarkets_automation.market_snapshot import StandardMarketSnapshot


def test_standard_market_snapshot_exposes_available_contract_labels() -> None:
    snapshot = StandardMarketSnapshot(
        event_url="https://smarkets.com/football/example",
        market_name="Full-time result",
        contracts=[
            {"label": "Arsenal", "buy_percent": "73%", "sell_percent": "74%"},
            {"label": "Draw", "buy_percent": "18%", "sell_percent": "19%"},
        ],
    )

    assert snapshot.contract_labels() == ["Arsenal", "Draw"]
