from dataclasses import dataclass


@dataclass(frozen=True)
class StandardContractSnapshot:
    label: str
    buy_percent: str = ""
    sell_percent: str = ""


@dataclass(frozen=True)
class StandardMarketSnapshot:
    event_url: str
    market_name: str
    contracts: list[StandardContractSnapshot | dict[str, str]]

    def __post_init__(self) -> None:
        normalized_contracts = [
            contract
            if isinstance(contract, StandardContractSnapshot)
            else StandardContractSnapshot(**contract)
            for contract in self.contracts
        ]
        object.__setattr__(self, "contracts", normalized_contracts)

    def contract_labels(self) -> list[str]:
        return [contract.label for contract in self.contracts]
