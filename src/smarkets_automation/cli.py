import argparse
from pathlib import Path

from smarkets_automation.bootstrap import ensure_copyable_helium_profile
from smarkets_automation.browser import browser_launch_args, launch_login_browser
from smarkets_automation.config import AppPaths, detect_helium_profile
from smarkets_automation.logging_utils import write_action_log
from smarkets_automation.orders import build_preflight


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
        if command == "place-bet":
            command_parser.add_argument("--event-url", required=True)
            command_parser.add_argument("--contract", required=True)
            command_parser.add_argument(
                "--available-contract",
                action="append",
                dest="available_contracts",
                required=True,
            )
            command_parser.add_argument("--side", required=True)
            command_parser.add_argument("--stake", required=True)
            command_parser.add_argument("--confirm", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "bootstrap-session":
        ensure_copyable_helium_profile(detect_helium_profile())

    if args.command == "login":
        profile_dir = AppPaths.from_home(Path.home()).profile_dir
        browser_launch_args(profile_dir)
        launch_login_browser(profile_dir)

    if args.command == "place-bet":
        plan = build_preflight(
            event_url=args.event_url,
            contract_labels=args.available_contracts,
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
