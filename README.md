# Smarkets Automation

Browser-first terminal tooling for Smarkets under [projects/smarkets-automation](/home/thomas/projects/smarkets-automation).

Current scope:
- bootstrap an owned automation profile from Helium
- launch a persistent Playwright session against the owned profile
- parse public event and match-odds HTML fixtures
- build review or confirm preflight plans
- write audit logs for `place-bet`

Quick commands:

```bash
cd /home/thomas/projects/smarkets-automation
python -m pytest -v
python -m smarkets_automation.cli bootstrap-session
python -m smarkets_automation.cli login
python -m smarkets_automation.cli place-bet --event-url "https://smarkets.com/football/example" --contract Arsenal --available-contract Arsenal --available-contract Draw --available-contract Everton --side buy --stake 10
python -m smarkets_automation.cli place-bet --event-url "https://smarkets.com/football/example" --contract Arsenal --available-contract Arsenal --available-contract Draw --available-contract Everton --side buy --stake 10 --confirm
```

Live smoke:

```bash
cd /home/thomas/projects/smarkets-automation
SMARKETS_LIVE=1 python -m pytest tests/test_live_smoke.py -v
```

Notes:
- `bootstrap-session` refuses while the Helium profile is locked.
- `login` launches against `~/.config/smarkets-automation/profile`, not the live Helium profile.
- `place-bet` requires explicit available contract labels so contract selection fails closed.
- `place-bet` is review-only by default and records review/confirm actions under `~/.config/smarkets-automation/logs`.
