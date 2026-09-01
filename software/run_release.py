#!/usr/bin/env python3
"""Run the paired nominal SCILLA PASSIVE simulation deterministically.

The process model is intentionally an explicit command-line choice. This keeps
the immutable Zenodo v1.0.0 evidence separate from corrected candidate runs.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any, Iterable

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scilla_passive_core as core


TRIALS_FILENAME = "nominal_trials.csv"
SUMMARY_FILENAME = "summary.json"
MODE_WORLD_COUNTS = {"quick": 60, "nominal": 300}
FIRST_SEED = 260901


def job(payload: tuple[int, dict[str, Any], str]) -> list[dict[str, Any]]:
    seed, kwargs, model_version = payload
    return core.run_world_all(seed, model_version=model_version, **kwargs)


def flatten(groups: Iterable[Iterable[dict[str, Any]]]) -> list[dict[str, Any]]:
    return [row for group in groups for row in group]


def summarize(rows: list[dict[str, Any]]) -> dict[str, dict[str, float | int]]:
    result: dict[str, dict[str, float | int]] = {}
    for policy in core.POLICIES:
        group = [row for row in rows if row["policy"] == policy]
        if not group:
            raise ValueError(f"no trial rows for policy {policy}")
        result[policy] = {
            "n": len(group),
            "median_position_error_m": float(
                np.median([row["position_error_final_m"] for row in group])
            ),
            "p90_position_error_m": float(
                np.quantile([row["position_error_final_m"] for row in group], 0.9)
            ),
            "median_velocity_error_mps": float(
                np.median([row["velocity_error_final_mps"] for row in group])
            ),
            "median_used_measurements": float(
                np.median([row["used_measurements"] for row in group])
            ),
        }
    return result


def _existing_outputs(out: Path) -> list[Path]:
    return [
        target
        for target in (out / TRIALS_FILENAME, out / SUMMARY_FILENAME)
        if target.exists()
    ]


def _stage_csv(path: Path, rows: list[dict[str, Any]]) -> Path:
    if not rows:
        raise ValueError("cannot write an empty trial table")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return temporary


def _stage_json(path: Path, payload: dict[str, Any]) -> Path:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            # No trailing newline preserves the historical runner convention.
            handle.write(json.dumps(payload, indent=2))
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return temporary


def _publish_staged(staged: list[tuple[Path, Path]]) -> None:
    """Atomically replace each declared output, without deleting its directory."""

    try:
        for temporary, target in staged:
            os.replace(temporary, target)
    finally:
        for temporary, _target in staged:
            temporary.unlink(missing_ok=True)


def run_release(
    *,
    mode: str,
    out: Path,
    model_version: str,
    force: bool = False,
    workers: int | None = None,
) -> dict[str, Any]:
    if mode not in MODE_WORLD_COUNTS:
        raise ValueError(f"unknown mode {mode!r}; expected one of {tuple(MODE_WORLD_COUNTS)}")
    if model_version not in core.MODEL_VERSIONS:
        raise ValueError(
            f"unknown model_version {model_version!r}; expected one of {core.MODEL_VERSIONS}"
        )
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    existing = _existing_outputs(out)
    if existing and not force:
        names = ", ".join(str(path) for path in existing)
        raise FileExistsError(
            f"refusing to overwrite existing release output(s): {names}; rerun with --force"
        )
    if workers is not None and workers < 1:
        raise ValueError("workers must be at least 1")

    count = MODE_WORLD_COUNTS[mode]
    payloads = [
        (FIRST_SEED + offset, {}, model_version) for offset in range(count)
    ]
    worker_count = workers or min(8, os.cpu_count() or 2)
    started = time.time()
    if worker_count == 1:
        groups = [job(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(max_workers=worker_count) as executor:
            groups = list(executor.map(job, payloads, chunksize=5))
    rows = flatten(groups)
    summary: dict[str, Any] = {
        "mode": mode,
        "model_version": model_version,
        "model_status": core.MODELS[model_version],
        "elapsed_s": time.time() - started,
        "summary": summarize(rows),
    }

    staged: list[tuple[Path, Path]] = []
    try:
        staged.append((_stage_csv(out / TRIALS_FILENAME, rows), out / TRIALS_FILENAME))
        staged.append((_stage_json(out / SUMMARY_FILENAME, summary), out / SUMMARY_FILENAME))
        _publish_staged(staged)
    except BaseException:
        for temporary, _target in staged:
            temporary.unlink(missing_ok=True)
        raise
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run SCILLA PASSIVE paired nominal simulations."
    )
    parser.add_argument("--mode", choices=tuple(MODE_WORLD_COUNTS), default="quick")
    parser.add_argument("--out", default="reproduction_output")
    parser.add_argument(
        "--model-version",
        choices=core.MODEL_VERSIONS,
        required=True,
        help="1.0.0 reproduces the DOI release; 1.1.0-candidate runs the corrected model.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Atomically replace only nominal_trials.csv and summary.json if they exist.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Worker-process count (default: min(8, available CPUs)).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        summary = run_release(
            mode=args.mode,
            out=Path(args.out),
            model_version=args.model_version,
            force=args.force,
            workers=args.workers,
        )
    except (FileExistsError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
