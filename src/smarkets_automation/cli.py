import argparse
from pathlib import Path

from smarkets_automation.bootstrap import ensure_copyable_helium_profile
from smarkets_automation.browser import browser_launch_args, launch_login_browser
from smarkets_automation.config import AppPaths, detect_helium_profile
from smarkets_automation.discovery import filter_event_candidates, parse_search_results
from smarkets_automation.logging_utils import write_action_log
from smarkets_automation.market_snapshot import build_standard_market_snapshot
from smarkets_automation.orders import build_preflight
from smarkets_automation.public_site import (
    absolute_smarkets_url,
    load_event_page_html,
    load_public_page_html,
)


COMMANDS = [
    "bootstrap-session",
    "login",
    "search-events",
    "show-market",
    "place-bet",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="smarkets")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in COMMANDS:
        command_parser = subparsers.add_parser(command)
        if command == "search-events":
            command_parser.add_argument("query")
        if command == "show-market":
            command_parser.add_argument("--event-url", required=True)
        if command == "place-bet":
            command_parser.add_argument("--event-url", required=True)
            command_parser.add_argument("--contract", required=True)
            command_parser.add_argument("--side", required=True)
            command_parser.add_argument("--stake", required=True)
            command_parser.add_argument("--confirm", action="store_true")

    return parser


def search_event_candidates(query: str) -> list[tuple[str, str]]:
    candidates = filter_event_candidates(
        parse_search_results(load_public_page_html("/")),
        query,
    )
    if not candidates:
        raise ValueError(f"no event candidates found for query: {query}")
    return [
        (candidate.label, absolute_smarkets_url(candidate.url))
        for candidate in candidates
    ]


def load_standard_market_snapshot(event_url: str):
    return build_standard_market_snapshot(event_url, load_event_page_html(event_url))


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "bootstrap-session":
        ensure_copyable_helium_profile(detect_helium_profile())

    if args.command == "login":
        profile_dir = AppPaths.from_home(Path.home()).profile_dir
        browser_launch_args(profile_dir)
        launch_login_browser(profile_dir)

    if args.command == "search-events":
        for label, url in search_event_candidates(args.query):
            print(f"{label} {url}")

    if args.command == "show-market":
        snapshot = load_standard_market_snapshot(args.event_url)
        print(snapshot.market_name)
        for contract in snapshot.contracts:
            buy_percent = f" buy={contract.buy_percent}" if contract.buy_percent else ""
            sell_percent = f" sell={contract.sell_percent}" if contract.sell_percent else ""
            print(f"{contract.label}{buy_percent}{sell_percent}")

    if args.command == "place-bet":
        snapshot = load_standard_market_snapshot(args.event_url)
        plan = build_preflight(
            event_url=args.event_url,
            contract_labels=snapshot.contract_labels(),
            requested_contract=args.contract,
            side=args.side,
            stake=args.stake,
            confirm=args.confirm,
        )
        status = "confirm" if plan.confirm else "review"
        write_action_log(
            AppPaths.from_home(Path.home()).logs_dir,
            {
                "status": status,
                "event_url": plan.event_url,
                "contract_label": plan.contract_label,
                "side": plan.side,
                "stake": plan.stake,
            },
        )
        print("Confirm mode" if plan.confirm else "Review mode")
        print(f"Event URL: {plan.event_url}")
        print(f"Contract: {plan.contract_label}")
        print(f"Side: {plan.side}")
        print(f"Stake: {plan.stake}")

    return 0
