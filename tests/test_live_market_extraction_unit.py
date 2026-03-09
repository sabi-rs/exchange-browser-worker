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


def test_build_standard_market_snapshot_reads_live_quotes_from_rendered_market_rows() -> None:
    html = """
    <div class="CompetitorsEventPrimaryMarket_primaryContracts__f_TDr">
      <div class="ContractRow_row__EYVzb">
        <span>Arsenal</span>
        <button class="BetButton_wrap__4KuBA BetButton_buy___RIrE">74%</button>
        <button class="BetButton_wrap__4KuBA BetButton_sell__po2hP">73%</button>
      </div>
      <div class="ContractRow_row__EYVzb">
        <span>Draw</span>
        <button class="BetButton_wrap__4KuBA BetButton_buy___RIrE">19%</button>
        <button class="BetButton_wrap__4KuBA BetButton_sell__po2hP">18%</button>
      </div>
      <div class="ContractRow_row__EYVzb">
        <span>Everton</span>
        <button class="BetButton_wrap__4KuBA BetButton_buy___RIrE">8%</button>
        <button class="BetButton_wrap__4KuBA BetButton_sell__po2hP">8%</button>
      </div>
    </div>
    <script>
    self.__next_f.push([1,"...\\\"markets\\\":[{\\\"name\\\":\\\"Full-time result\\\",\\\"contracts\\\":[{\\\"name\\\":\\\"Arsenal\\\"},{\\\"name\\\":\\\"Draw\\\"},{\\\"name\\\":\\\"Everton\\\"}]}]..."])
    </script>
    """

    snapshot = build_standard_market_snapshot("https://smarkets.com/sport/football/example", html)

    assert snapshot.contracts[0].buy_percent == "74%"
    assert snapshot.contracts[0].sell_percent == "73%"
    assert snapshot.contracts[1].buy_percent == "19%"
    assert snapshot.contracts[1].sell_percent == "18%"
