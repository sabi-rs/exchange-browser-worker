from dataclasses import dataclass


VALID_SIDES = {"buy", "sell"}


@dataclass(frozen=True)
class PreflightPlan:
    event_url: str
    contract_label: str
    side: str
    stake: str
    confirm: bool


def build_preflight(
    event_url: str,
    contract_labels: list[str],
    requested_contract: str,
    side: str,
    stake: str,
    confirm: bool = False,
) -> PreflightPlan:
    normalized_url = event_url.strip()
    normalized_contract = requested_contract.strip()
    normalized_side = side.strip().lower()
    normalized_stake = stake.strip()

    if not normalized_url:
        raise ValueError("Event URL is required")
    if normalized_contract not in contract_labels:
        raise ValueError("Contract label must match exactly")
    if normalized_side not in VALID_SIDES:
        raise ValueError("Side must be buy or sell")
    if not normalized_stake:
        raise ValueError("Stake is required")

    return PreflightPlan(
        event_url=normalized_url,
        contract_label=normalized_contract,
        side=normalized_side,
        stake=normalized_stake,
        confirm=confirm,
    )
