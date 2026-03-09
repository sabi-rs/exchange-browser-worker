from dataclasses import dataclass
import json
import re


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


def _decode_embedded_state_payloads(html: str) -> list[str]:
    payloads = re.findall(
        r'self\.__next_f\.push\(\[1,"(.*?)"\]\)',
        html,
        re.DOTALL,
    )
    return [bytes(payload, "utf-8").decode("unicode_escape") for payload in payloads]


def build_standard_market_snapshot(event_url: str, html: str) -> StandardMarketSnapshot:
    decoder = json.JSONDecoder()

    for payload in _decode_embedded_state_payloads(html):
        marker = '"markets":'
        marker_index = payload.find(marker)
        if marker_index == -1:
            continue

        markets, _ = decoder.raw_decode(payload[marker_index + len(marker) :])
        for market in markets:
            if market.get("name") != "Full-time result":
                continue
            contracts = [
                StandardContractSnapshot(label=contract["name"])
                for contract in market.get("contracts", [])
                if contract.get("name")
            ]
            if not contracts:
                break
            return StandardMarketSnapshot(
                event_url=event_url,
                market_name=market["name"],
                contracts=contracts,
            )

    raise ValueError("event page is missing supported standard market data")
