from dataclasses import dataclass
from html.parser import HTMLParser
import json
import re


@dataclass(frozen=True)
class StandardContractSnapshot:
    label: str
    buy_percent: str = ""
    sell_percent: str = ""

    def quote_for_side(self, side: str) -> str:
        return self.buy_percent if side == "buy" else self.sell_percent


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


class _RenderedPrimaryMarketParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[dict[str, str]] = []
        self._primary_depth = 0
        self._row_depth = 0
        self._current_row: dict[str, str] | None = None
        self._current_button_side = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        class_name = attrs_dict.get("class", "")

        if self._primary_depth == 0 and "CompetitorsEventPrimaryMarket_primaryContracts" in class_name:
            self._primary_depth = 1
            return

        if self._primary_depth == 0:
            return

        self._primary_depth += 1

        if self._row_depth == 0 and "ContractRow_row" in class_name:
            self._row_depth = 1
            self._current_row = {
                "label": "",
                "buy_percent": "",
                "sell_percent": "",
            }
            return

        if self._row_depth == 0:
            return

        self._row_depth += 1
        if tag == "button":
            if "BetButton_buy" in class_name:
                self._current_button_side = "buy_percent"
            if "BetButton_sell" in class_name:
                self._current_button_side = "sell_percent"

    def handle_endtag(self, tag: str) -> None:
        if self._primary_depth == 0:
            return

        if self._row_depth > 0:
            if tag == "button":
                self._current_button_side = ""
            self._row_depth -= 1
            if self._row_depth == 0 and self._current_row:
                self._current_row["label"] = self._current_row["label"].strip()
                if self._current_row["label"]:
                    self.rows.append(self._current_row)
                self._current_row = None

        self._primary_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._current_row:
            return

        text = data.strip()
        if not text:
            return

        if self._current_button_side:
            self._current_row[self._current_button_side] += text
            return

        if self._current_row["buy_percent"] or self._current_row["sell_percent"]:
            return

        self._current_row["label"] += text


def _extract_rendered_primary_market_quotes(html: str) -> dict[str, tuple[str, str]]:
    parser = _RenderedPrimaryMarketParser()
    parser.feed(html)
    return {
        row["label"]: (row["buy_percent"], row["sell_percent"])
        for row in parser.rows
    }


def build_standard_market_snapshot(event_url: str, html: str) -> StandardMarketSnapshot:
    decoder = json.JSONDecoder()
    rendered_quotes = _extract_rendered_primary_market_quotes(html)

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
                StandardContractSnapshot(
                    label=contract["name"],
                    buy_percent=rendered_quotes.get(contract["name"], ("", ""))[0],
                    sell_percent=rendered_quotes.get(contract["name"], ("", ""))[1],
                )
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
