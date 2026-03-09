from smarkets_automation import cli


def test_search_events_prints_resolved_candidates(capsys, monkeypatch) -> None:
    monkeypatch.setattr(
        cli,
        "search_event_candidates",
        lambda query: [("Arsenal Everton", "https://smarkets.com/football/example")],
    )

    exit_code = cli.main(["search-events", "Arsenal Everton"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Arsenal Everton" in captured.out
    assert "https://smarkets.com/football/example" in captured.out


def test_search_event_candidates_uses_live_search_results_html(monkeypatch) -> None:
    monkeypatch.setattr(
        cli,
        "load_search_results_html",
        lambda query: """
        <div role="dialog">
          <a href="/football/england-premier-league/2026/03/14/17-30/arsenal-vs-everton/44919794/">
            Premier League Arsenal vs Everton 14 Mar 5:30 PM
          </a>
          <a href="/football/england-premier-league/2026/03/21/17-30/everton-vs-chelsea/44929596/">
            Premier League Everton vs Chelsea 21 Mar 5:30 PM
          </a>
        </div>
        """,
    )

    assert cli.search_event_candidates("Arsenal Everton") == [
        (
            "Premier League Arsenal vs Everton 14 Mar 5:30 PM",
            "https://smarkets.com/football/england-premier-league/2026/03/14/17-30/arsenal-vs-everton/44919794/",
        ),
    ]
