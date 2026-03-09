import pytest

from smarkets_automation.market_snapshot import StandardContractSnapshot
from smarkets_automation.orders import PreflightPlan, build_preflight


def test_build_preflight_requires_exact_contract_match() -> None:
    with pytest.raises(ValueError):
        build_preflight(
            event_url="https://smarkets.com/example",
            contracts=[
                StandardContractSnapshot("Arsenal", "74%", "73%"),
                StandardContractSnapshot("Draw", "19%", "18%"),
                StandardContractSnapshot("Everton", "8%", "8%"),
            ],
            requested_contract="Arse",
            side="buy",
            stake="10",
        )


def test_build_preflight_returns_plan_for_exact_contract_match() -> None:
    plan = build_preflight(
        event_url="https://smarkets.com/example",
        contracts=[
            StandardContractSnapshot("Arsenal", "74%", "73%"),
            StandardContractSnapshot("Draw", "19%", "18%"),
            StandardContractSnapshot("Everton", "8%", "8%"),
        ],
        requested_contract="Arsenal",
        side="sell",
        stake="10",
    )

    assert plan == PreflightPlan(
        event_url="https://smarkets.com/example",
        contract_label="Arsenal",
        side="sell",
        stake="10",
        expected_percent="73%",
        confirm=False,
    )


def test_build_preflight_tracks_confirm_mode() -> None:
    plan = build_preflight(
        event_url="https://smarkets.com/example",
        contracts=[
            StandardContractSnapshot("Arsenal", "74%", "73%"),
            StandardContractSnapshot("Draw", "19%", "18%"),
            StandardContractSnapshot("Everton", "8%", "8%"),
        ],
        requested_contract="Arsenal",
        side="buy",
        stake="10",
        confirm=True,
    )

    assert plan.confirm is True


@pytest.mark.parametrize(
    ("event_url", "side", "stake"),
    [
        ("", "buy", "10"),
        ("https://smarkets.com/example", "hold", "10"),
        ("https://smarkets.com/example", "buy", ""),
    ],
)
def test_build_preflight_fails_closed_for_invalid_input(
    event_url: str,
    side: str,
    stake: str,
) -> None:
    with pytest.raises(ValueError):
        build_preflight(
            event_url=event_url,
            contracts=[
                StandardContractSnapshot("Arsenal", "74%", "73%"),
                StandardContractSnapshot("Draw", "19%", "18%"),
                StandardContractSnapshot("Everton", "8%", "8%"),
            ],
            requested_contract="Arsenal",
            side=side,
            stake=stake,
        )


def test_build_preflight_fails_closed_without_quote_for_selected_side() -> None:
    with pytest.raises(ValueError, match="Selected contract is missing a live quote"):
        build_preflight(
            event_url="https://smarkets.com/example",
            contracts=[
                StandardContractSnapshot("Arsenal", "74%", ""),
                StandardContractSnapshot("Draw", "19%", "18%"),
                StandardContractSnapshot("Everton", "8%", "8%"),
            ],
            requested_contract="Arsenal",
            side="sell",
            stake="10",
        )
