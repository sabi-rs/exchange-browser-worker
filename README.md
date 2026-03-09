# Smarkets Automation

Browser-first terminal tooling for Smarkets under [projects/smarkets-automation](/home/thomas/projects/smarkets-automation).

Current scope:
- bootstrap an owned automation profile from Helium
- launch a persistent Playwright session against the owned profile
- discover live football event candidates from the public site
- extract standard football `Full-time result` market snapshots
- build review or confirm preflight plans from live market state
- write audit logs for `place-bet`

Quick commands:

```bash
cd /home/thomas/projects/smarkets-automation
PYTHONPATH=src python -m pytest -v
PYTHONPATH=src python -m smarkets_automation.cli bootstrap-session
PYTHONPATH=src python -m smarkets_automation.cli login
PYTHONPATH=src python -m smarkets_automation.cli search-events "Arsenal Everton"
PYTHONPATH=src python -m smarkets_automation.cli show-market --event-url "https://smarkets.com/football/england-premier-league/2026/03/14/17-30/arsenal-vs-everton/44919794/"
PYTHONPATH=src python -m smarkets_automation.cli place-bet --event-url "https://smarkets.com/football/england-premier-league/2026/03/14/17-30/arsenal-vs-everton/44919794/" --contract Arsenal --side buy --stake 10
PYTHONPATH=src python -m smarkets_automation.cli place-bet --event-url "https://smarkets.com/football/england-premier-league/2026/03/14/17-30/arsenal-vs-everton/44919794/" --contract Arsenal --side buy --stake 10 --confirm
```

Live smoke:

```bash
cd /home/thomas/projects/smarkets-automation
SMARKETS_LIVE=1 PYTHONPATH=src python -m pytest tests/test_live_smoke.py -v
```

Notes:
- `bootstrap-session` refuses while the Helium profile is locked.
- `login` launches against `~/.config/smarkets-automation/profile`, not the live Helium profile.
- `show-market` and `place-bet` are phase-1 flows for standard football `Full-time result` markets only.
- `place-bet` resolves available contracts and live percentages from the same market snapshot used by `show-market`.
- `place-bet` is review-only by default and records review/confirm actions under `~/.config/smarkets-automation/logs`.
- `place-bet` aborts if the live quote or populated slip state drifts from preflight assumptions.
- Bet builder is intentionally deferred to phase 2 and tracked separately in [docs/plans/2026-03-09-smarkets-bet-builder-phase-2.md](/home/thomas/projects/smarkets-automation/.worktrees/smarkets-live-execution/docs/plans/2026-03-09-smarkets-bet-builder-phase-2.md).
