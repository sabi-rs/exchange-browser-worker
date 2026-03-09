from smarkets_automation.public_site import absolute_smarkets_url


def test_absolute_smarkets_url_expands_relative_paths() -> None:
    assert (
        absolute_smarkets_url("/football/example")
        == "https://smarkets.com/football/example"
    )
