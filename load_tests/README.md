# Locust UI Load Tests

This folder contains the files needed to run load tests from the Locust web UI.

## Files Used By UI Runs

- `locustfile.py` - Locust user behavior and custom CLI options.
- `data_generators.py` - Generated emails, credentials, and random image bytes.
- `requirements-locust.txt` - Python dependencies for Locust tests.

## Install Dependencies

```bash
pip install -r load_tests/requirements-locust.txt
```

## Start Locust UI

```bash
python -m locust -f load_tests/locustfile.py --host=http://127.0.0.1:5000
```

Open the UI at http://127.0.0.1:8089.

## Optional UI Flags

```bash
python -m locust -f load_tests/locustfile.py --host=http://127.0.0.1:5000 --workload-type read-heavy --data-size large --cleanup off --request-timeout 5
```

- `--workload-type`: `read-heavy`, `write-heavy`, or `mixed`.
- `--data-size`: `small` (description writes) or `large` (profile-photo uploads).
- `--cleanup`: default is `off`; set `on` only if you want user deletion during stop.
- `--request-timeout`: per-request timeout in seconds (default `5`).