#!/usr/bin/env python3
"""
run_matrix.py — Headless batch runner for the SENG 533 experiment matrix.

Iterates every combination of:
  - workload type   : read-heavy, write-heavy, mixed
  - data size       : small, large
  - concurrency     : 10, 25, 50, 100
  - repetitions     : 3 (for confidence intervals)

Each run executes Locust in headless mode for a configurable duration,
then saves the CSV output to a structured directory.

Output structure
────────────────
  results/
    mixed_large_50_run1/
      mixed_large_50_run1_stats.csv
      mixed_large_50_run1_stats_history.csv
      mixed_large_50_run1_failures.csv
      mixed_large_50_run1_exceptions.csv
    mixed_large_50_run2/
      ...

Usage
─────
  python run_matrix.py                                         # all defaults
  python run_matrix.py --host https://your-cloudrun-url.run.app
  python run_matrix.py --duration 180 --reps 5                 # 3-min runs, 5 reps
  python run_matrix.py --users 10,50                           # subset of user levels
  python run_matrix.py --workloads mixed --sizes large         # single config
"""

import argparse
import os
import subprocess
import sys
import time


# ── Defaults ────────────────────────────────────────────────────────────────
DEFAULT_HOST       = "http://127.0.0.1:5000"
DEFAULT_DURATION   = 180       # 3 minutes per run
DEFAULT_RAMP_RATE  = 10        # users spawned per second
DEFAULT_REPS       = 3         # repetitions per configuration
DEFAULT_USERS      = [5, 10, 15, 20]
DEFAULT_WORKLOADS  = ["read-heavy", "write-heavy", "mixed"]
DEFAULT_SIZES      = ["small", "large"]
DEFAULT_TIMEOUT    = 30.0
RESULTS_DIR        = "results"
LOCUSTFILE         = os.path.join(os.path.dirname(__file__), "locustfile.py")


def parse_args():
    p = argparse.ArgumentParser(description="Run the full SENG 533 experiment matrix.")
    p.add_argument("--host",       default=DEFAULT_HOST,  help="Backend base URL.")
    p.add_argument("--duration",   type=int, default=DEFAULT_DURATION, help="Seconds per run.")
    p.add_argument("--ramp-rate",  type=int, default=DEFAULT_RAMP_RATE, help="Users spawned/sec.")
    p.add_argument("--reps",       type=int, default=DEFAULT_REPS, help="Repetitions per config.")
    p.add_argument("--timeout",    type=float, default=DEFAULT_TIMEOUT, help="Per-request timeout.")
    p.add_argument("--users",      default=",".join(str(u) for u in DEFAULT_USERS),
                   help="Comma-separated user counts.")
    p.add_argument("--workloads",  default=",".join(DEFAULT_WORKLOADS),
                   help="Comma-separated workload types.")
    p.add_argument("--sizes",      default=",".join(DEFAULT_SIZES),
                   help="Comma-separated data sizes.")
    p.add_argument("--outdir",     default=RESULTS_DIR, help="Root output directory.")
    p.add_argument("--dry-run",    action="store_true", help="Print commands without running.")
    return p.parse_args()


def run_single(
    host: str,
    workload: str,
    size: str,
    users: int,
    run_num: int,
    duration: int,
    ramp_rate: int,
    timeout: float,
    outdir: str,
    dry_run: bool,
) -> bool:
    """Execute a single Locust headless run. Returns True on success."""

    tag = f"{workload}_{size}_{users}_run{run_num}"
    run_dir = os.path.join(outdir, tag)
    os.makedirs(run_dir, exist_ok=True)
    csv_prefix = os.path.join(run_dir, tag)

    cmd = [
        sys.executable, "-m", "locust",
        "-f", LOCUSTFILE,
        "--host", host,
        "--headless",
        "-u", str(users),
        "-r", str(min(ramp_rate, users)),   # ramp rate <= user count
        "-t", f"{duration}s",
        "--workload-type", workload,
        "--data-size", size,
        "--cleanup", "on",
        "--request-timeout", str(timeout),
        "--csv", csv_prefix,
        "--csv-full-history",
        "--only-summary",                    # suppress per-second console spam
    ]

    print(f"\n{'='*70}")
    print(f"  RUN: {tag}")
    print(f"  {users} users | {workload} | {size} | {duration}s | rep {run_num}")
    print(f"  CSV → {csv_prefix}_stats.csv")
    print(f"{'='*70}")

    if dry_run:
        print(f"  [DRY RUN] {' '.join(cmd)}")
        return True

    start = time.time()
    result = subprocess.run(cmd, cwd=os.path.dirname(LOCUSTFILE) or ".")
    elapsed = time.time() - start

    print(f"  Finished in {elapsed:.0f}s — exit code {result.returncode}")
    return result.returncode == 0


def main():
    args = parse_args()

    user_levels = [int(u.strip()) for u in args.users.split(",")]
    workloads   = [w.strip() for w in args.workloads.split(",")]
    sizes       = [s.strip() for s in args.sizes.split(",")]

    total_runs = len(workloads) * len(sizes) * len(user_levels) * args.reps
    total_time_min = (total_runs * args.duration) / 60

    print(f"\nSENG 533 — Experiment matrix")
    print(f"  Host:       {args.host}")
    print(f"  Workloads:  {workloads}")
    print(f"  Sizes:      {sizes}")
    print(f"  Users:      {user_levels}")
    print(f"  Reps:       {args.reps}")
    print(f"  Duration:   {args.duration}s per run")
    print(f"  Total runs: {total_runs}")
    print(f"  Est. time:  {total_time_min:.0f} minutes ({total_time_min/60:.1f} hours)")
    print(f"  Output:     {args.outdir}/")
    print()

    os.makedirs(args.outdir, exist_ok=True)

    completed = 0
    failed    = 0

    for workload in workloads:
        for size in sizes:
            for users in user_levels:
                for rep in range(1, args.reps + 1):
                    ok = run_single(
                        host=args.host,
                        workload=workload,
                        size=size,
                        users=users,
                        run_num=rep,
                        duration=args.duration,
                        ramp_rate=args.ramp_rate,
                        timeout=args.timeout,
                        outdir=args.outdir,
                        dry_run=args.dry_run,
                    )
                    if ok:
                        completed += 1
                    else:
                        failed += 1

    print(f"\n{'='*70}")
    print(f"  MATRIX COMPLETE — {completed} passed, {failed} failed out of {total_runs}")
    print(f"  Results in: {os.path.abspath(args.outdir)}/")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
