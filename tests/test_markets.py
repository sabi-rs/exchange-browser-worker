from pathlib import Path

import pytest

from smarkets_automation.markets import parse_match_odds_market


def test_parse_match_odds_market_extracts_contracts_and_quotes() -> None:
    html_path = Path(__file__).parent / "fixtures" / "market_page.html"
    html = html_path.read_text()

    market = parse_match_odds_market(html)

    assert market.market_name == "Match Odds"
    assert len(market.contracts) == 3
    assert market.contracts[0].label == "Arsenal"
    assert market.contracts[0].buy_percent == "74%"
    assert market.contracts[0].sell_percent == "76%"
    assert market.contracts[1].label == "Manchester United"
    assert market.contracts[1].sell_percent == "18%"
    assert market.contracts[1].buy_percent == "16%"
    assert market.contracts[2].label == "Everton"
    assert market.contracts[2].buy_percent == "10%"
    assert market.contracts[2].sell_percent == "12%"


def test_parse_match_odds_market_uses_last_top_level_heading_before_contracts() -> None:
    html = """
    <section data-market="match-odds">
      <h2>Popular picks</h2>
      <p>Ignore this helper heading.</p>
      <h2>Match Odds</h2>
      <div data-contract>
        <span data-label>Arsenal</span>
        <span data-buy>74%</span>
        <span data-sell>76%</span>
      </div>
    </section>
    """

    market = parse_match_odds_market(html)

    assert market.market_name == "Match Odds"


def test_parse_match_odds_market_ignores_nested_inline_markup_in_quote_fields() -> None:
    html = """
    <section data-market="match-odds">
      <h2>Match Odds</h2>
      <div data-contract>
        <span data-label>Arsenal</span>
        <span data-buy><strong>down</strong>74%</span>
        <span data-sell><em>up</em>76%</span>
      </div>
    </section>
    """

    market = parse_match_odds_market(html)

    assert market.contracts[0].buy_percent == "74%"
    assert market.contracts[0].sell_percent == "76%"


@pytest.mark.parametrize(
    "html",
    [
        "<section data-market='match-odds'><div data-contract></div></section>",
        "<section data-market='match-odds'><h2>Match Odds</h2></section>",
    ],
)
def test_parse_match_odds_market_fails_closed_without_required_data(html: str) -> None:
    with pytest.raises(ValueError):
        parse_match_odds_market(html)


@pytest.mark.parametrize(
    "contract_html",
    [
        "<span data-buy>74%</span><span data-sell>76%</span>",
        "<span data-label>Arsenal</span><span data-sell>76%</span>",
        "<span data-label>Arsenal</span><span data-buy>74%</span>",
    ],
)
def test_parse_match_odds_market_fails_closed_for_incomplete_contract_row(
    contract_html: str,
) -> None:
    html = (
        "<section data-market='match-odds'>"
        "<h2>Match Odds</h2>"
        f"<div data-contract>{contract_html}</div>"
        "</section>"
    )

    with pytest.raises(ValueError):
        parse_match_odds_market(html)
