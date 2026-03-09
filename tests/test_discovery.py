from pathlib import Path

import pytest

from smarkets_automation.discovery import (
    EventCandidate,
    filter_event_candidates,
    parse_search_results,
)


def test_parse_search_results_extracts_event_candidates() -> None:
    html_path = Path(__file__).parent / "fixtures" / "search_results.html"
    html = html_path.read_text()

    results = parse_search_results(html)

    assert results[0].label == "Premier League Arsenal vs Everton 14 Mar 5:30 PM"
    assert results[0].url.endswith("/arsenal-vs-everton/")


def test_filter_event_candidates_rejects_empty_queries() -> None:
    with pytest.raises(ValueError):
        filter_event_candidates(
            [EventCandidate(label="Arsenal Everton", url="/football/example")],
            "   ",
        )
