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
