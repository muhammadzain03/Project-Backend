#!/usr/bin/env python3
"""
analyze_results.py — Post-processing for SENG 533 load-test results.

Reads all Locust CSV files from the results/ directory, computes 95%
confidence intervals across repetitions, and outputs summary tables
suitable for the final report.

Output
──────
  analysis/
    summary_table.csv           — per-endpoint metrics with 95% CIs
    pivot_by_users.csv          — response time by concurrency level
    pivot_by_workload.csv       — response time by workload type
    throughput_summary.csv      — RPS by configuration
    report_tables.txt           — formatted tables ready to paste

Usage
─────
  python analyze_results.py                         # default: reads results/
  python analyze_results.py --results-dir results/  # explicit path
"""

import argparse
import os
import re
import sys

import numpy as np
import pandas as pd
from scipy import stats


ANALYSIS_DIR = "analysis"


def parse_args():
    p = argparse.ArgumentParser(description="Analyze SENG 533 load-test results.")
    p.add_argument("--results-dir", default="results", help="Root results directory.")
    p.add_argument("--outdir", default=ANALYSIS_DIR, help="Output directory.")
    p.add_argument("--confidence", type=float, default=0.95, help="CI level.")
    return p.parse_args()


def parse_run_tag(dirname: str) -> dict | None:
    """
    Extract workload, size, users, run number from directory name.
    Expected format: {workload}_{size}_{users}_run{N}
    Example: mixed_large_50_run2
    """
    pattern = r"^(read-heavy|write-heavy|mixed)_(small|large)_(\d+)_run(\d+)$"
    m = re.match(pattern, dirname)
    if not m:
        return None
    return {
        "workload": m.group(1),
        "data_size": m.group(2),
        "users": int(m.group(3)),
        "run": int(m.group(4)),
    }


def load_stats_csvs(results_dir: str) -> pd.DataFrame:
    """
    Walk the results directory and load all *_stats.csv files.
    Each row is one endpoint from one run.
    """
    rows = []

    for entry in sorted(os.listdir(results_dir)):
        run_dir = os.path.join(results_dir, entry)
        if not os.path.isdir(run_dir):
            continue

        meta = parse_run_tag(entry)
        if meta is None:
            print(f"  [skip] unrecognized directory: {entry}")
            continue

        # Find the stats CSV (Locust names it {prefix}_stats.csv)
        stats_files = [f for f in os.listdir(run_dir) if f.endswith("_stats.csv")]
        if not stats_files:
            print(f"  [skip] no stats CSV in: {entry}")
            continue

        csv_path = os.path.join(run_dir, stats_files[0])
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            print(f"  [error] reading {csv_path}: {e}")
            continue

        # Locust stats CSV columns:
        #   Type, Name, Request Count, Failure Count, Median Response Time,
        #   Average Response Time, Min Response Time, Max Response Time,
        #   Average Content Size, Requests/s, Failures/s,
        #   50%, 66%, 75%, 80%, 90%, 95%, 98%, 99%, 99.9%, 99.99%, 100%

        # Filter out the "Aggregated" row for per-endpoint analysis
        endpoint_rows = df[df["Name"] != "Aggregated"].copy()
        aggregated = df[df["Name"] == "Aggregated"].copy()

        for _, row in endpoint_rows.iterrows():
            rows.append({
                "workload":       meta["workload"],
                "data_size":      meta["data_size"],
                "users":          meta["users"],
                "run":            meta["run"],
                "endpoint":       f"{row.get('Type', '')} {row.get('Name', '')}".strip(),
                "request_count":  row.get("Request Count", 0),
                "failure_count":  row.get("Failure Count", 0),
                "avg_ms":         row.get("Average Response Time", 0),
                "median_ms":      row.get("Median Response Time", 0),
                "min_ms":         row.get("Min Response Time", 0),
                "max_ms":         row.get("Max Response Time", 0),
                "p95_ms":         row.get("95%", 0),
                "p99_ms":         row.get("99%", 0),
                "rps":            row.get("Requests/s", 0),
                "failure_rate":   (row.get("Failure Count", 0) / max(row.get("Request Count", 1), 1)) * 100,
            })

        # Also store aggregate row
        for _, row in aggregated.iterrows():
            rows.append({
                "workload":       meta["workload"],
                "data_size":      meta["data_size"],
                "users":          meta["users"],
                "run":            meta["run"],
                "endpoint":       "AGGREGATE",
                "request_count":  row.get("Request Count", 0),
                "failure_count":  row.get("Failure Count", 0),
                "avg_ms":         row.get("Average Response Time", 0),
                "median_ms":      row.get("Median Response Time", 0),
                "min_ms":         row.get("Min Response Time", 0),
                "max_ms":         row.get("Max Response Time", 0),
                "p95_ms":         row.get("95%", 0),
                "p99_ms":         row.get("99%", 0),
                "rps":            row.get("Requests/s", 0),
                "failure_rate":   (row.get("Failure Count", 0) / max(row.get("Request Count", 1), 1)) * 100,
            })

    if not rows:
        print("No data found. Make sure results/ contains run directories.")
        sys.exit(1)

    return pd.DataFrame(rows)


def compute_ci(values: np.ndarray, confidence: float = 0.95) -> tuple:
    """Compute mean and 95% confidence interval for an array of values."""
    n = len(values)
    if n < 2:
        return values.mean(), 0.0, values.mean(), values.mean()

    mean = values.mean()
    se = stats.sem(values)
    t_crit = stats.t.ppf((1 + confidence) / 2, df=n - 1)
    margin = t_crit * se

    return mean, margin, mean - margin, mean + margin


def build_summary(df: pd.DataFrame, confidence: float = 0.95) -> pd.DataFrame:
    """
    Group by (workload, data_size, users, endpoint) across runs,
    then compute mean ± CI for key metrics.
    """
    group_cols = ["workload", "data_size", "users", "endpoint"]
    results = []

    for key, group in df.groupby(group_cols):
        workload, data_size, users, endpoint = key

        avg_vals    = group["avg_ms"].values
        p95_vals    = group["p95_ms"].values
        rps_vals    = group["rps"].values
        fail_vals   = group["failure_rate"].values
        count_vals  = group["request_count"].values

        avg_mean, avg_margin, avg_lo, avg_hi = compute_ci(avg_vals, confidence)
        p95_mean, p95_margin, p95_lo, p95_hi = compute_ci(p95_vals, confidence)
        rps_mean, rps_margin, rps_lo, rps_hi = compute_ci(rps_vals, confidence)

        results.append({
            "workload":         workload,
            "data_size":        data_size,
            "users":            users,
            "endpoint":         endpoint,
            "n_runs":           len(group),
            "total_requests":   int(count_vals.sum()),
            "avg_ms_mean":      round(avg_mean, 2),
            "avg_ms_ci":        f"±{avg_margin:.2f}",
            "avg_ms_lo":        round(avg_lo, 2),
            "avg_ms_hi":        round(avg_hi, 2),
            "p95_ms_mean":      round(p95_mean, 2),
            "p95_ms_ci":        f"±{p95_margin:.2f}",
            "rps_mean":         round(rps_mean, 3),
            "rps_ci":           f"±{rps_margin:.3f}",
            "failure_pct_mean": round(fail_vals.mean(), 2),
        })

    return pd.DataFrame(results)


def build_pivot_table(summary: pd.DataFrame, value_col: str, index_col: str) -> pd.DataFrame:
    """Build a pivot table from the summary for the aggregate endpoint."""
    agg = summary[summary["endpoint"] == "AGGREGATE"].copy()
    if agg.empty:
        return pd.DataFrame()

    pivot = agg.pivot_table(
        index=[index_col, "data_size"],
        columns="workload",
        values=value_col,
        aggfunc="first",
    )
    return pivot


def format_report_table(summary: pd.DataFrame) -> str:
    """Format key results as plain-text tables for pasting into the report."""
    lines = []
    lines.append("=" * 90)
    lines.append("SENG 533 — Load Test Summary (95% Confidence Intervals)")
    lines.append("=" * 90)

    agg = summary[summary["endpoint"] == "AGGREGATE"].copy()
    agg = agg.sort_values(["workload", "data_size", "users"])

    for (wl, ds), group in agg.groupby(["workload", "data_size"]):
        lines.append(f"\n  Workload: {wl}  |  Data size: {ds}")
        lines.append(f"  {'Users':>5}  {'Avg (ms)':>12}  {'95% CI':>14}  {'p95 (ms)':>10}  "
                      f"{'RPS':>8}  {'Fail %':>7}  {'Requests':>10}")
        lines.append(f"  {'-'*5}  {'-'*12}  {'-'*14}  {'-'*10}  {'-'*8}  {'-'*7}  {'-'*10}")

        for _, r in group.iterrows():
            lines.append(
                f"  {r['users']:>5}  {r['avg_ms_mean']:>12.2f}  "
                f"{r['avg_ms_ci']:>14}  {r['p95_ms_mean']:>10.2f}  "
                f"{r['rps_mean']:>8.3f}  {r['failure_pct_mean']:>7.2f}  "
                f"{r['total_requests']:>10}"
            )

    lines.append("\n")

    # Per-endpoint breakdown for the most interesting config
    lines.append("-" * 90)
    lines.append("Per-endpoint breakdown (all configurations)")
    lines.append("-" * 90)

    endpoints = summary[summary["endpoint"] != "AGGREGATE"].copy()
    endpoints = endpoints.sort_values(["workload", "data_size", "users", "endpoint"])

    for (wl, ds, users), group in endpoints.groupby(["workload", "data_size", "users"]):
        lines.append(f"\n  {wl} | {ds} | {users} users")
        lines.append(f"  {'Endpoint':<40}  {'Avg (ms)':>10}  {'p95 (ms)':>10}  {'RPS':>8}  {'Fail %':>7}")
        lines.append(f"  {'-'*40}  {'-'*10}  {'-'*10}  {'-'*8}  {'-'*7}")

        for _, r in group.iterrows():
            lines.append(
                f"  {r['endpoint']:<40}  {r['avg_ms_mean']:>10.2f}  "
                f"{r['p95_ms_mean']:>10.2f}  {r['rps_mean']:>8.3f}  "
                f"{r['failure_pct_mean']:>7.2f}"
            )

    return "\n".join(lines)


def main():
    args = parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    print(f"Loading results from: {args.results_dir}/")
    df = load_stats_csvs(args.results_dir)
    n_configs = df.groupby(["workload", "data_size", "users", "run"]).ngroups
    print(f"  Loaded {len(df)} rows across {n_configs} run configurations")

    print(f"Computing {args.confidence*100:.0f}% confidence intervals...")
    summary = build_summary(df, args.confidence)

    # Save CSVs
    summary_path = os.path.join(args.outdir, "summary_table.csv")
    summary.to_csv(summary_path, index=False)
    print(f"  Saved: {summary_path}")

    pivot_users = build_pivot_table(summary, "avg_ms_mean", "users")
    if not pivot_users.empty:
        pivot_path = os.path.join(args.outdir, "pivot_by_users.csv")
        pivot_users.to_csv(pivot_path)
        print(f"  Saved: {pivot_path}")

    pivot_workload = build_pivot_table(summary, "rps_mean", "users")
    if not pivot_workload.empty:
        tput_path = os.path.join(args.outdir, "throughput_summary.csv")
        pivot_workload.to_csv(tput_path)
        print(f"  Saved: {tput_path}")

    # Formatted report tables
    report_text = format_report_table(summary)
    report_path = os.path.join(args.outdir, "report_tables.txt")
    with open(report_path, "w") as f:
        f.write(report_text)
    print(f"  Saved: {report_path}")

    # Print to console too
    print(f"\n{report_text}")


if __name__ == "__main__":
    main()
