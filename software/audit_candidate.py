#!/usr/bin/env python3
"""Audit the corrected SCILLA PASSIVE process-model candidate.

This script compares an explicitly generated ``1.1.0-candidate`` nominal and
stress run with the immutable v1.0.0 evidence.  It reports whether the
qualitative architecture conclusion survives the process-model correction; it
does not promote the candidate or create a measured-performance claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scilla_passive_core as core  # noqa: E402


POLICY_ORDER = (
    "NO_PASSIVE",
    "HIGHEST_SNR",
    "RANDOM",
    "SHORTEST_PULSE",
    "METROLOGY_CONDITIONED_EIG",
)
BASE_SEED = 20260902
BOOTSTRAP_RESAMPLES = 10_000


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def percentile_interval(values: np.ndarray, policy_index: int) -> tuple[float, float]:
    """Deterministic percentile interval for the sample median."""
    rng = np.random.default_rng(np.random.SeedSequence([BASE_SEED, policy_index]))
    medians = np.empty(BOOTSTRAP_RESAMPLES, dtype=float)
    for start in range(0, BOOTSTRAP_RESAMPLES, 1_000):
        stop = min(start + 1_000, BOOTSTRAP_RESAMPLES)
        draws = rng.integers(0, len(values), size=(stop - start, len(values)))
        medians[start:stop] = np.median(values[draws], axis=1)
    low, high = np.quantile(medians, (0.025, 0.975), method="linear")
    return float(low), float(high)


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_candidate_metadata(nominal_dir: Path, stress_dir: Path) -> None:
    nominal = load_json(nominal_dir / "summary.json")
    stress = load_json(stress_dir / "RUN_METADATA.json")
    for label, metadata in (("nominal", nominal), ("stress", stress)):
        if metadata.get("model_version") != core.CANDIDATE_MODEL_VERSION:
            raise ValueError(f"{label} output is not {core.CANDIDATE_MODEL_VERSION}")
    if stress.get("physics_cells") != 54 or stress.get("integrity_cells") != 27:
        raise ValueError("candidate stress grid is incomplete")
    if stress.get("worlds_per_cell") != 30:
        raise ValueError("candidate stress run must use 30 worlds per cell")


def nominal_audit(trials: pd.DataFrame) -> dict[str, object]:
    if set(trials["policy"]) != set(POLICY_ORDER):
        raise ValueError("candidate nominal policy set does not match the declared contract")
    counts = trials.groupby("policy")["seed"].nunique()
    if not (counts == 300).all():
        raise ValueError("candidate nominal run must contain 300 paired worlds per policy")

    seed_sets = [set(group["seed"]) for _, group in trials.groupby("policy")]
    if any(seeds != seed_sets[0] for seeds in seed_sets[1:]):
        raise ValueError("candidate nominal policies do not share the same paired seeds")

    policies: dict[str, object] = {}
    for index, policy in enumerate(POLICY_ORDER):
        group = trials.loc[trials["policy"] == policy]
        values = group["position_error_final_m"].to_numpy(dtype=float)
        low, high = percentile_interval(values, index)
        policies[policy] = {
            "worlds": int(len(group)),
            "median_final_position_error_m": float(np.median(values)),
            "p90_final_position_error_m": float(np.quantile(values, 0.9, method="linear")),
            "median_final_velocity_error_mps": float(
                group["velocity_error_final_mps"].median()
            ),
            "audit_bootstrap_95_percent_interval_m": [low, high],
        }

    paired = trials.pivot(index="seed", columns="policy", values="position_error_final_m")
    difference = (
        paired["METROLOGY_CONDITIONED_EIG"] - paired["SHORTEST_PULSE"]
    ).to_numpy(dtype=float)
    paired_low, paired_high = percentile_interval(difference, len(POLICY_ORDER))
    return {
        "policies": policies,
        "paired_eig_vs_shortest_pulse": {
            "eig_better_worlds": int(np.sum(difference < 0)),
            "ties": int(np.sum(difference == 0)),
            "shortest_pulse_better_worlds": int(np.sum(difference > 0)),
            "eig_better_fraction": float(np.mean(difference < 0)),
            "paired_median_difference_m": float(np.median(difference)),
            "audit_bootstrap_95_percent_interval_of_paired_median_m": [
                paired_low,
                paired_high,
            ],
        },
    }


def stress_audit(
    candidate: pd.DataFrame,
    legacy: pd.DataFrame,
    expected_cells: int,
) -> dict[str, object]:
    if len(candidate) != expected_cells or len(legacy) != expected_cells:
        raise ValueError(f"stress summary must contain {expected_cells} cells")

    architecture = candidate["metrology_eig_beats_no_passive"].astype(int)
    optimizer = candidate["metrology_eig_beats_best_simple"].astype(int)
    legacy_architecture = legacy["metrology_eig_beats_no_passive"].astype(int)
    legacy_optimizer = legacy["metrology_eig_beats_best_simple"].astype(int)
    return {
        "cells": expected_cells,
        "architecture_beats_no_passive_cells": int(architecture.sum()),
        "architecture_beats_no_passive_fraction": float(architecture.mean()),
        "eig_beats_best_simple_cells": int(optimizer.sum()),
        "eig_beats_best_simple_fraction": float(optimizer.mean()),
        "architecture_gate_cells_changed_vs_v1_0_0": int(
            np.sum(architecture.to_numpy() != legacy_architecture.to_numpy())
        ),
        "optimizer_gate_cells_changed_vs_v1_0_0": int(
            np.sum(optimizer.to_numpy() != legacy_optimizer.to_numpy())
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nominal-dir", type=Path, required=True)
    parser.add_argument("--stress-dir", type=Path, required=True)
    parser.add_argument("--legacy-dir", type=Path, default=Path("results"))
    parser.add_argument("--out", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    validate_candidate_metadata(args.nominal_dir, args.stress_dir)

    nominal_path = args.nominal_dir / "nominal_trials.csv"
    candidate_physics_path = args.stress_dir / "physics_robustness_scenario_summary.csv"
    candidate_integrity_path = args.stress_dir / "integrity_stress_scenario_summary.csv"
    legacy_physics_path = args.legacy_dir / "physics_robustness_scenario_summary.csv"
    legacy_integrity_path = args.legacy_dir / "integrity_stress_scenario_summary.csv"

    nominal = pd.read_csv(nominal_path, float_precision="round_trip")
    candidate_physics = pd.read_csv(candidate_physics_path, float_precision="round_trip")
    candidate_integrity = pd.read_csv(candidate_integrity_path, float_precision="round_trip")
    legacy_physics = pd.read_csv(legacy_physics_path, float_precision="round_trip")
    legacy_integrity = pd.read_csv(legacy_integrity_path, float_precision="round_trip")

    nominal_result = nominal_audit(nominal)
    physics_result = stress_audit(candidate_physics, legacy_physics, 54)
    integrity_result = stress_audit(candidate_integrity, legacy_integrity, 27)

    medians = nominal_result["policies"]
    architecture_preserved = (
        medians["METROLOGY_CONDITIONED_EIG"]["median_final_position_error_m"]
        < medians["NO_PASSIVE"]["median_final_position_error_m"]
        and physics_result["architecture_gate_cells_changed_vs_v1_0_0"] == 0
        and integrity_result["architecture_gate_cells_changed_vs_v1_0_0"] == 0
    )

    inputs = [
        nominal_path,
        args.nominal_dir / "summary.json",
        args.stress_dir / "RUN_METADATA.json",
        args.stress_dir / "physics_robustness_trials.csv",
        candidate_physics_path,
        args.stress_dir / "integrity_stress_trials.csv",
        candidate_integrity_path,
        args.stress_dir / "integrity_gate_statistics.csv",
    ]
    report = {
        "audit_id": "SCILLA-PASSIVE-CORRECTED-PROCESS-MODEL-2026-09-02",
        "status": "PASS_CANDIDATE_NOT_PROMOTED" if architecture_preserved else "REVIEW",
        "model_version": core.CANDIDATE_MODEL_VERSION,
        "model_status": core.MODELS[core.CANDIDATE_MODEL_VERSION],
        "evidence_class": "SIMULATED",
        "architecture_conclusion_preserved": architecture_preserved,
        "nominal": nominal_result,
        "physics_stress": physics_result,
        "integrity_stress": integrity_result,
        "bootstrap_contract": {
            "purpose": "declared candidate audit, not historical v1.0.0 reconstruction",
            "bit_generator": "NumPy PCG64",
            "base_seed": BASE_SEED,
            "resamples": BOOTSTRAP_RESAMPLES,
            "confidence_level": 0.95,
            "quantile_method": "linear",
        },
        "input_sha256": {path.name: sha256(path) for path in inputs},
        "claim_boundary": {
            "supported": "The corrected candidate preserves the qualitative simulated second-observation architecture conclusion on the frozen nominal seeds and stress grids.",
            "not_supported": [
                "measured RF performance",
                "operational detection range",
                "customer value",
                "a robust proprietary donor-optimizer advantage",
                "promotion of 1.1.0-candidate to a released model",
            ],
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if architecture_preserved else 1


if __name__ == "__main__":
    raise SystemExit(main())
