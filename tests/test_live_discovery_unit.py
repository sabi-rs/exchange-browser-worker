from smarkets_automation.discovery import EventCandidate, filter_event_candidates


def test_filter_event_candidates_matches_query_terms_and_deduplicates() -> None:
    candidates = [
        EventCandidate(label="Arsenal Everton", url="/football/.../arsenal-vs-everton/1"),
        EventCandidate(label="Arsenal Everton", url="/football/.../arsenal-vs-everton/1"),
        EventCandidate(label="West Ham Brentford", url="/football/.../west-ham-vs-brentford/2"),
    ]

    filtered = filter_event_candidates(candidates, "Arsenal Everton")

    assert filtered == [
        EventCandidate(
            label="Arsenal Everton",
            url="/football/.../arsenal-vs-everton/1",
        ),
    ]
