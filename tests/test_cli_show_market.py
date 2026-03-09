from smarkets_automation import cli
from smarkets_automation.market_snapshot import (
    StandardContractSnapshot,
    StandardMarketSnapshot,
)


def test_show_market_prints_standard_market_snapshot(capsys, monkeypatch) -> None:
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

    exit_code = cli.main(
        ["show-market", "--event-url", "https://smarkets.com/football/example"],
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Full-time result" in captured.out
    assert "Arsenal" in captured.out
    assert "buy=73%" in captured.out
    assert "sell=74%" in captured.out
