from dataclasses import dataclass
from html.parser import HTMLParser


@dataclass(frozen=True)
class ContractQuote:
    label: str
    buy_percent: str
    sell_percent: str


@dataclass(frozen=True)
class MatchOddsMarket:
    market_name: str
    contracts: list[ContractQuote]


class _MatchOddsParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_market = False
        self._market_section_depth = 0
        self._current_field: str | None = None
        self._current_field_span_depth = 0
        self._current_contract: dict[str, str] | None = None
        self._current_contract_div_depth = 0
        self._ignored_inline_depth = 0
        self._market_name_parts: list[str] = []
        self.contracts: list[ContractQuote] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)

        if tag == "section" and attributes.get("data-market") == "match-odds":
            self._in_market = True
            self._market_section_depth = 1
            return

        if not self._in_market:
            return

        if tag == "section":
            self._market_section_depth += 1
            return

        if (
            tag == "h2"
            and self._market_section_depth == 1
            and not self.contracts
            and self._current_contract is None
        ):
            self._market_name_parts = []
            self._current_field = "market_name"
            return

        if tag == "div" and "data-contract" in attributes:
            self._current_contract = {"label": "", "buy": "", "sell": ""}
            self._current_contract_div_depth = 1
            return

        if tag == "div" and self._current_contract is not None:
            self._current_contract_div_depth += 1
            return

        if tag != "span":
            if (
                self._current_contract is not None
                and self._current_field in {"buy", "sell"}
                and self._current_field_span_depth > 0
            ):
                self._ignored_inline_depth += 1
            return

        if self._current_contract is None:
            return

        if "data-label" in attributes:
            self._current_field = "label"
            self._current_field_span_depth = 1
        elif "data-buy" in attributes:
            self._current_field = "buy"
            self._current_field_span_depth = 1
        elif "data-sell" in attributes:
            self._current_field = "sell"
            self._current_field_span_depth = 1
        elif self._current_field is not None:
            self._current_field_span_depth += 1
            if self._current_field in {"buy", "sell"}:
                self._ignored_inline_depth += 1

    def handle_data(self, data: str) -> None:
        if self._ignored_inline_depth > 0:
            return

        if self._current_field is None:
            return

        stripped = data.strip()
        if not stripped:
            return

        if self._current_field == "market_name":
            self._market_name_parts.append(stripped)
            return

        if self._current_contract is not None:
            if self._current_field == "label":
                existing_label = self._current_contract["label"]
                if data[:1].isspace() and existing_label and not existing_label.endswith(" "):
                    existing_label += " "
                existing_label += stripped
                if data[-1:].isspace() and not existing_label.endswith(" "):
                    existing_label += " "
                self._current_contract["label"] = existing_label
                return
            self._current_contract[self._current_field] += stripped

    def handle_endtag(self, tag: str) -> None:
        if tag == "section" and self._in_market:
            self._market_section_depth -= 1
            if self._market_section_depth == 0:
                self._in_market = False
                self._current_field = None
            return

        if not self._in_market:
            return

        if tag == "span" and self._current_contract is not None:
            if self._current_field_span_depth == 0:
                return
            if (
                self._ignored_inline_depth > 0
                and self._current_field in {"buy", "sell"}
                and self._current_field_span_depth > 1
            ):
                self._ignored_inline_depth -= 1
            self._current_field_span_depth -= 1
            if self._current_field_span_depth == 0:
                self._current_field = None
                return
            return

        if (
            self._current_contract is not None
            and self._current_field in {"buy", "sell"}
            and self._ignored_inline_depth > 0
        ):
            self._ignored_inline_depth -= 1
            return

        if tag == "h2":
            self._current_field = None
            return

        if tag == "div" and self._current_contract is not None:
            self._current_contract_div_depth -= 1
            if self._current_contract_div_depth == 0:
                if not all(self._current_contract.values()):
                    raise ValueError("Match odds market data is incomplete")
                self.contracts.append(
                    ContractQuote(
                        label=self._current_contract["label"].strip(),
                        buy_percent=self._current_contract["buy"],
                        sell_percent=self._current_contract["sell"],
                    ),
                )
                self._current_contract = None


def parse_match_odds_market(html: str) -> MatchOddsMarket:
    parser = _MatchOddsParser()
    parser.feed(html)
    market_name = " ".join(parser._market_name_parts)
    if not market_name or not parser.contracts:
        raise ValueError("Match odds market data is incomplete")
    return MatchOddsMarket(market_name=market_name, contracts=parser.contracts)
