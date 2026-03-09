from dataclasses import dataclass

from smarkets_automation.market_snapshot import StandardContractSnapshot


VALID_SIDES = {"buy", "sell"}


@dataclass(frozen=True)
class PreflightPlan:
    event_url: str
    contract_label: str
    side: str
    stake: str
    expected_percent: str
    confirm: bool


def build_preflight(
    event_url: str,
    contracts: list[StandardContractSnapshot | str],
    requested_contract: str,
    side: str,
    stake: str,
    confirm: bool = False,
) -> PreflightPlan:
    normalized_url = event_url.strip()
    normalized_contract = requested_contract.strip()
    normalized_side = side.strip().lower()
    normalized_stake = stake.strip()
    normalized_contracts = [
        contract
        if isinstance(contract, StandardContractSnapshot)
        else StandardContractSnapshot(label=contract)
        for contract in contracts
    ]
    selected_contract = next(
        (contract for contract in normalized_contracts if contract.label == normalized_contract),
        None,
    )

    if not normalized_url:
        raise ValueError("Event URL is required")
    if selected_contract is None:
        raise ValueError("Contract label must match exactly")
    if normalized_side not in VALID_SIDES:
        raise ValueError("Side must be buy or sell")
    if not normalized_stake:
        raise ValueError("Stake is required")
    expected_percent = selected_contract.quote_for_side(normalized_side)
    if not expected_percent:
        raise ValueError("Selected contract is missing a live quote for requested side")

    return PreflightPlan(
        event_url=normalized_url,
        contract_label=normalized_contract,
        side=normalized_side,
        stake=normalized_stake,
        expected_percent=expected_percent,
        confirm=confirm,
    )
