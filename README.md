# exchange-browser-worker

Python browser automation worker for exchange market inspection and execution.

It is currently focused on Smarkets session bootstrap, market discovery, quote extraction, and review-first bet placement.

## Develop

```bash
uv venv .venv --python 3.11
uv pip install --python .venv/bin/python -e .
.venv/bin/python -m pytest -v
```
