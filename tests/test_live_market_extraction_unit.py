from smarkets_automation.market_snapshot import build_standard_market_snapshot


def test_build_standard_market_snapshot_reads_full_time_result_from_embedded_state() -> None:
    html = '''
    <script>
    self.__next_f.push([1,"...\\\"name\\\":\\\"Arsenal vs Everton\\\",\\\"full_slug\\\":\\\"/sport/football/example\\\",\\\"markets\\\":[{\\\"name\\\":\\\"Full-time result\\\",\\\"contracts\\\":[{\\\"name\\\":\\\"Arsenal\\\"},{\\\"name\\\":\\\"Draw\\\"},{\\\"name\\\":\\\"Everton\\\"}]}]..."])
    </script>
    '''

    snapshot = build_standard_market_snapshot("https://smarkets.com/sport/football/example", html)

    assert snapshot.market_name == "Full-time result"
    assert snapshot.contract_labels() == ["Arsenal", "Draw", "Everton"]
