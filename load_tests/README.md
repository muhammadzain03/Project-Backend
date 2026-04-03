# SENG 533 — Load tests

Load-testing suite for the ProfileHub backend using [Locust](https://locust.io/).

## Files

| File | Purpose |
|---|---|
| `locustfile.py` | Locust user behaviour — signup, login, profile reads, photo/description writes |
| `data_generators.py` | Unique emails, credentials, random images (PNG + JPEG), descriptions |
| `run_matrix.py` | Headless batch runner — iterates the full experiment matrix |
| `analyze_results.py` | Post-processing — 95% confidence intervals, summary tables |
| `requirements-locust.txt` | Python dependencies |

## Quick start

Run Locust commands from the **`load_tests/`** directory so `data_generators` imports resolve.

```bash
cd load_tests
pip install -r requirements-locust.txt
```

Paths like `/user/{email}` use **URL-encoded** emails (e.g. `%40` for `@`) to match the production frontend and Flask routing.

## 1. Manual run (Locust web UI)

```bash
locust -f locustfile.py --host http://127.0.0.1:5000
```

Open http://127.0.0.1:8089, set user count and spawn rate, start the test.

### CLI flags

| Flag | Values | Default | Description |
|---|---|---|---|
| `--workload-type` | `read-heavy`, `write-heavy`, `mixed` | `mixed` | Read/write ratio |
| `--data-size` | `small`, `large` | `large` | `small` = JSON only; `large` = ~500 KB image uploads |
| `--cleanup` | `off`, `on` | `off` | Delete test users when the run stops |
| `--request-timeout` | seconds | `30` | Per-request timeout |

```bash
locust -f locustfile.py --host http://127.0.0.1:5000 \
       --workload-type read-heavy --data-size large --cleanup on
```

## 2. Full experiment matrix (headless)

Runs **every** combination automatically and saves CSVs:

```bash
python run_matrix.py --host http://127.0.0.1:5000
```

Default matrix: 3 workloads × 2 sizes × 4 user levels × 3 reps = **72 runs** at 5 min each (~6 hours).

### Subset runs

```bash
# Quick smoke test: one config, one rep, 60 seconds
python run_matrix.py --workloads mixed --sizes large --users 10 --reps 1 --duration 60

# Only 10 and 50 users, mixed workload
python run_matrix.py --users 10,50 --workloads mixed

# Dry run (shows commands without executing)
python run_matrix.py --dry-run
```

## 3. Analyze results

After `run_matrix.py` finishes:

```bash
python analyze_results.py
```

Outputs to `analysis/`:
- `summary_table.csv` — per-endpoint means with 95% CIs
- `pivot_by_users.csv` — avg response time by concurrency level
- `throughput_summary.csv` — RPS by workload type
- `report_tables.txt` — formatted tables for the final report

## Endpoints tested

| Operation | Endpoint | Category |
|---|---|---|
| Sign up | `POST /auth/signup` | Setup (once per user) |
| Log in | `POST /auth/login` | Read (35% of reads) |
| Get profile | `GET /user/{email}` | Read (65% of reads) |
| Upload description | `POST /user/{email}/description` | Write (100% small; 30% large) |
| Upload photo | `POST /user/{email}/profile-photo` | Write (0% small; 70% large) |
| Delete user | `DELETE /user/{email}` | Cleanup (when --cleanup on) |

## Experiment matrix

| Factor | Levels |
|---|---|
| Workload type | read-heavy (80R/20W), mixed (50/50), write-heavy (20R/80W) |
| Data size | small (~200 B JSON), large (~500 KB PNG + JSON) |
| Concurrency | 10, 25, 50, 100 users |
| Duration | 300s (5 min) per run |
| Repetitions | 3 per configuration |
