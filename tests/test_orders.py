import pytest

from smarkets_automation.orders import PreflightPlan, build_preflight


def test_build_preflight_requires_exact_contract_match() -> None:
    with pytest.raises(ValueError):
        build_preflight(
            event_url="https://smarkets.com/example",
            contract_labels=["Arsenal", "Draw", "Everton"],
            requested_contract="Arse",
            side="buy",
            stake="10",
        )


def test_build_preflight_returns_plan_for_exact_contract_match() -> None:
    plan = build_preflight(
        event_url="https://smarkets.com/example",
        contract_labels=["Arsenal", "Draw", "Everton"],
        requested_contract="Arsenal",
        side="sell",
        stake="10",
    )

    assert plan == PreflightPlan(
        event_url="https://smarkets.com/example",
        contract_label="Arsenal",
        side="sell",
        stake="10",
        confirm=False,
    )


def test_build_preflight_tracks_confirm_mode() -> None:
    plan = build_preflight(
        event_url="https://smarkets.com/example",
        contract_labels=["Arsenal", "Draw", "Everton"],
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
            contract_labels=["Arsenal", "Draw", "Everton"],
            requested_contract="Arsenal",
            side=side,
            stake=stake,
        )
