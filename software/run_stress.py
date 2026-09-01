#!/usr/bin/env python3
"""Reproduce the frozen SCILLA PASSIVE v1.0.0 stress evidence.

This runner deliberately selects the legacy v1.0.0 estimator when the core
offers more than one model.  It therefore exists to reproduce the published
Zenodo evidence, not to generate results for a later candidate model.
"""

from __future__ import annotations

import argparse
import hashlib
import inspect
import itertools
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scilla_passive_core as core  # noqa: E402


WORLDS_PER_CELL = 30

PHYSICS_GRID = tuple(
    dict(zip(("n_donors", "clutter_db", "rcs", "donor_sigma"), values))
    for values in itertools.product((4, 12, 20), (5, 15, 25), (10, 100, 1000), (30, 100))
)
INTEGRITY_GRID = tuple(
    dict(zip(("maneuver_deg", "assoc_error_prob", "outlier_prob"), values))
    for values in itertools.product((0, 20, 45), (0.0, 0.05, 0.15), (0.0, 0.05, 0.15))
)

TRIAL_COLUMNS = (
    "policy",
    "seed",
    "position_error_final_m",
    "velocity_error_final_mps",
    "position_sigma_final_m",
    "used_measurements",
    "rejected_measurements",
    "assoc_bad_accepted",
    "outlier_accepted",
    "eligible_measurements",
)
PHYSICS_DIMENSIONS = ("n_donors", "clutter_db", "rcs", "donor_sigma")
INTEGRITY_DIMENSIONS = ("maneuver_deg", "assoc_error_prob", "outlier_prob")

FROZEN_CSV_SHA256 = {
    "physics_robustness_trials.csv": "349e6c21df185c631fae0816b465156d38acad52cdadb3e076d6933bd073e779",
    "physics_robustness_scenario_summary.csv": "f706f5e3ce22dcb53b4f8ae163a273b96e0141a63a9cb6f060c8e29f360e4102",
    "integrity_stress_trials.csv": "c750ef3f08e531990e2f9166683379f85c929cd5490abdaaf159adbdff0c99f7",
    "integrity_stress_scenario_summary.csv": "f56d4508431790146faea2c0afdd580bbf117d0f6a4ed70ebb0023c877a75544",
    "integrity_gate_statistics.csv": "64d5d16881c3f74e134378662996fecb0ea535b422f099e951335c2ed73f0e76",
}


def _legacy_kwargs(kwargs: Mapping[str, object]) -> dict[str, object]:
    """Select v1.0.0 explicitly when a dual-model core is installed."""
    selected = dict(kwargs)
    if "model_version" in inspect.signature(core.run_world_all).parameters:
        selected["model_version"] = getattr(core, "LEGACY_MODEL_VERSION", "1.0.0")
    return selected


def _job(item: tuple[int, int, Mapping[str, object]]) -> tuple[int, list[dict[str, object]]]:
    scenario_id, seed, kwargs = item
    return scenario_id, core.run_world_all(seed, **_legacy_kwargs(kwargs))


def _jobs(
    grid: Sequence[Mapping[str, object]], seed_base: int, worlds_per_cell: int
) -> Iterable[tuple[int, int, Mapping[str, object]]]:
    for scenario_id, kwargs in enumerate(grid, start=1):
        for world_index in range(worlds_per_cell):
            yield scenario_id, seed_base + scenario_id * 1000 + world_index, kwargs


def _run_grid(
    grid: Sequence[Mapping[str, object]],
    dimensions: Sequence[str],
    seed_base: int,
    worlds_per_cell: int,
    workers: int,
) -> pd.DataFrame:
    work = list(_jobs(grid, seed_base, worlds_per_cell))
    if workers == 1:
        completed = map(_job, work)
    else:
        executor = ProcessPoolExecutor(max_workers=workers)
        completed = executor.map(_job, work, chunksize=5)

    rows: list[dict[str, object]] = []
    try:
        for scenario_id, results in completed:
            metadata = {"scenario_id": scenario_id, **grid[scenario_id - 1]}
            for result in results:
                rows.append({**result, **metadata})
    finally:
        if workers != 1:
            executor.shutdown()

    columns = [*TRIAL_COLUMNS, "scenario_id", *dimensions]
    return pd.DataFrame(rows, columns=columns)


def summarize_scenarios(trials: pd.DataFrame, dimensions: Sequence[str]) -> pd.DataFrame:
    """Create the exact frozen scenario-level median table."""
    rows: list[dict[str, object]] = []
    for scenario_id, group in trials.groupby("scenario_id", sort=True):
        medians = group.groupby("policy")["position_error_final_m"].median()
        row: dict[str, object] = {name: group.iloc[0][name] for name in dimensions}
        row["scenario_id"] = int(scenario_id)
        row.update(
            {
                "no_passive_median_m": medians["NO_PASSIVE"],
                "random_median_m": medians["RANDOM"],
                "highest_snr_median_m": medians["HIGHEST_SNR"],
                "shortest_pulse_median_m": medians["SHORTEST_PULSE"],
                "metrology_eig_median_m": medians["METROLOGY_CONDITIONED_EIG"],
            }
        )
        row["best_simple_median_m"] = min(
            row["random_median_m"],
            row["highest_snr_median_m"],
            row["shortest_pulse_median_m"],
        )
        row["metrology_eig_beats_no_passive"] = int(
            row["metrology_eig_median_m"] < row["no_passive_median_m"]
        )
        row["metrology_eig_beats_best_simple"] = int(
            row["metrology_eig_median_m"] < row["best_simple_median_m"]
        )
        rows.append(row)

    summary = pd.DataFrame(rows)
    for name in dimensions:
        if name not in ("assoc_error_prob", "outlier_prob"):
            summary[name] = summary[name].astype(int)
    return summary


def integrity_gate_statistics(trials: pd.DataFrame) -> pd.DataFrame:
    gate = (
        trials.groupby(["scenario_id", "policy"])
        .agg(
            accepted_assoc_bad=("assoc_bad_accepted", "sum"),
            accepted_outliers=("outlier_accepted", "sum"),
            used=("used_measurements", "sum"),
            rejected=("rejected_measurements", "sum"),
        )
        .reset_index()
    )
    numerator = gate["accepted_assoc_bad"] + gate["accepted_outliers"]
    gate["corrupt_accepted_fraction"] = (numerator / gate["used"].replace(0, np.nan)).fillna(0.0)
    return gate


def _write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, lineterminator="\n")


def run_physics(out: Path, worlds_per_cell: int, workers: int) -> tuple[Path, Path]:
    trials = _run_grid(PHYSICS_GRID, PHYSICS_DIMENSIONS, 300_000, worlds_per_cell, workers)
    summary = summarize_scenarios(trials, PHYSICS_DIMENSIONS)
    trials_path = out / "physics_robustness_trials.csv"
    summary_path = out / "physics_robustness_scenario_summary.csv"
    _write_csv(trials, trials_path)
    _write_csv(summary, summary_path)
    return trials_path, summary_path


def run_integrity(out: Path, worlds_per_cell: int, workers: int) -> tuple[Path, Path, Path]:
    fixed = {"n_donors": 12, "clutter_db": 10, "rcs": 100, "donor_sigma": 30}
    grid = tuple({**fixed, **values} for values in INTEGRITY_GRID)
    dimensions = (*PHYSICS_DIMENSIONS, *INTEGRITY_DIMENSIONS)
    trials = _run_grid(grid, dimensions, 500_000, worlds_per_cell, workers)
    summary = summarize_scenarios(trials, INTEGRITY_DIMENSIONS)
    gate = integrity_gate_statistics(trials)
    trials_path = out / "integrity_stress_trials.csv"
    summary_path = out / "integrity_stress_scenario_summary.csv"
    gate_path = out / "integrity_gate_statistics.csv"
    _write_csv(trials, trials_path)
    _write_csv(summary, summary_path)
    _write_csv(gate, gate_path)
    return trials_path, summary_path, gate_path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_frozen(generated_dir: Path, frozen_dir: Path) -> dict[str, object]:
    """Require byte-exact reproduction of all five published CSV files."""
    checks: list[dict[str, object]] = []
    ok = True
    for name, expected_hash in FROZEN_CSV_SHA256.items():
        generated = generated_dir / name
        frozen = frozen_dir / name
        generated_hash = sha256(generated) if generated.is_file() else None
        frozen_hash = sha256(frozen) if frozen.is_file() else None
        passed = generated_hash == frozen_hash == expected_hash
        ok &= passed
        checks.append(
            {
                "path": name,
                "expected_sha256": expected_hash,
                "generated_sha256": generated_hash,
                "frozen_sha256": frozen_hash,
                "byte_exact": passed,
            }
        )
    report = {"ok": ok, "files": checks}
    print(json.dumps(report, indent=2))
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", choices=("physics", "integrity", "all"), default="all")
    parser.add_argument("--out", type=Path, default=Path("reproduction_stress"))
    parser.add_argument("--frozen", type=Path, default=Path("results"))
    parser.add_argument("--worlds-per-cell", type=int, default=WORLDS_PER_CELL)
    parser.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 2))
    parser.add_argument("--verify-frozen", action="store_true")
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Skip simulation and compare an already generated output directory.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.worlds_per_cell < 1:
        raise SystemExit("--worlds-per-cell must be positive")
    if args.workers < 1:
        raise SystemExit("--workers must be positive")
    if (args.verify_frozen or args.verify_only) and args.worlds_per_cell != WORLDS_PER_CELL:
        raise SystemExit("Frozen verification requires exactly 30 worlds per cell")

    started = time.time()
    if not args.verify_only:
        args.out.mkdir(parents=True, exist_ok=True)
        if args.suite in ("physics", "all"):
            run_physics(args.out, args.worlds_per_cell, args.workers)
        if args.suite in ("integrity", "all"):
            run_integrity(args.out, args.worlds_per_cell, args.workers)
        print(f"completed suite={args.suite} in {time.time() - started:.1f}s")

    if args.verify_frozen or args.verify_only:
        if args.suite != "all":
            raise SystemExit("Frozen verification requires --suite all")
        return 0 if verify_frozen(args.out, args.frozen)["ok"] else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
