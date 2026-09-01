#!/usr/bin/env python3
"""Audit the provenance of the published nominal bootstrap intervals.

The immutable ``1.0.0`` archive contains the nominal trials and the resulting
confidence-interval endpoints, but it does not contain the program that made
those intervals.  In particular, the archive does not record the resample
count, PRNG family/state, policy-stream allocation, or quantile convention.
Those choices cannot be recovered uniquely from ten endpoint values.

This module therefore does two deliberately separate things:

* verifies the hashes and all non-bootstrap summary statistics against the
  frozen nominal trials; and
* computes a *new, fully declared audit bootstrap* as a sensitivity check.

The audit bootstrap must never be represented as the recovered algorithm that
produced the published endpoints.  A numerical match, if one occurred by
chance, would not establish historical provenance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRIALS = REPOSITORY_ROOT / "results" / "nominal_trials.csv"
DEFAULT_SUMMARY = REPOSITORY_ROOT / "results" / "nominal_policy_summary.csv"

FROZEN_SHA256 = {
    "nominal_trials.csv":
        "5251ea88da0c076d5df73dff03e30c88bcbaa262fe843ee0f13dd2b4ceb615f8",
    "nominal_policy_summary.csv":
        "f0ef3cf3aeecac2018ddff1a2c4039e46962af08259cd3712d9160d6e303a742",
}

PROVENANCE_STATUS = "NOT_IDENTIFIABLE_FROM_RELEASE_ARTIFACTS"
AUDIT_ALGORITHM = "nonparametric percentile bootstrap of the sample median"
AUDIT_BIT_GENERATOR = "NumPy PCG64"
AUDIT_SEED = 20_260_901
AUDIT_RESAMPLES = 10_000
AUDIT_CONFIDENCE_LEVEL = 0.95
AUDIT_QUANTILE_METHOD = "linear"
AUDIT_BATCH_SIZE = 256

POLICY_ORDER = (
    "NO_PASSIVE",
    "RANDOM",
    "HIGHEST_SNR",
    "SHORTEST_PULSE",
    "METROLOGY_CONDITIONED_EIG",
)

SUMMARY_FIELDS = {
    "n": lambda frame: int(len(frame)),
    "median_position_error_m": lambda frame: float(
        np.median(frame["position_error_final_m"].to_numpy())
    ),
    "p90_position_error_m": lambda frame: float(
        np.quantile(frame["position_error_final_m"].to_numpy(), 0.9)
    ),
    "median_velocity_error_mps": lambda frame: float(
        np.median(frame["velocity_error_final_mps"].to_numpy())
    ),
    "p90_velocity_error_mps": lambda frame: float(
        np.quantile(frame["velocity_error_final_mps"].to_numpy(), 0.9)
    ),
    "median_used_measurements": lambda frame: float(
        np.median(frame["used_measurements"].to_numpy())
    ),
    "median_rejected_measurements": lambda frame: float(
        np.median(frame["rejected_measurements"].to_numpy())
    ),
}


class BootstrapAuditError(RuntimeError):
    """Raised when the frozen evidence cannot be safely audited."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_frozen_hashes(trials_path: Path, summary_path: Path) -> dict[str, Any]:
    """Verify the canonical files when the default frozen inputs are used."""

    actual = {
        trials_path.name: sha256_file(trials_path),
        summary_path.name: sha256_file(summary_path),
    }
    canonical_inputs = (
        trials_path.resolve() == DEFAULT_TRIALS.resolve()
        and summary_path.resolve() == DEFAULT_SUMMARY.resolve()
    )
    matches = {
        name: actual[name] == expected
        for name, expected in FROZEN_SHA256.items()
        if name in actual
    }
    if canonical_inputs and not all(matches.values()):
        raise BootstrapAuditError(
            "a canonical nominal input does not match its frozen SHA-256"
        )
    return {
        "canonical_inputs": canonical_inputs,
        "actual_sha256": actual,
        "expected_sha256": FROZEN_SHA256,
        "all_frozen_hashes_match": canonical_inputs and all(matches.values()),
    }


def load_nominal_inputs(
    trials_path: Path = DEFAULT_TRIALS,
    summary_path: Path = DEFAULT_SUMMARY,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    required_trials = {
        "policy",
        "seed",
        "position_error_final_m",
        "velocity_error_final_mps",
        "used_measurements",
        "rejected_measurements",
    }
    required_summary = {
        "policy",
        "n",
        "median_position_error_m",
        "median_position_error_ci95_lo",
        "median_position_error_ci95_hi",
        "p90_position_error_m",
        "median_velocity_error_mps",
        "p90_velocity_error_mps",
        "median_used_measurements",
        "median_rejected_measurements",
    }
    trials = pd.read_csv(trials_path)
    summary = pd.read_csv(summary_path)
    missing_trials = required_trials - set(trials.columns)
    missing_summary = required_summary - set(summary.columns)
    if missing_trials or missing_summary:
        raise BootstrapAuditError(
            f"missing columns: trials={sorted(missing_trials)}, "
            f"summary={sorted(missing_summary)}"
        )
    if not bool(trials["policy"].duplicated(keep=False).all()):
        raise BootstrapAuditError("each policy must contain multiple paired trials")
    if summary["policy"].duplicated().any():
        raise BootstrapAuditError("summary contains duplicate policy rows")
    if set(trials["policy"]) != set(summary["policy"]):
        raise BootstrapAuditError("trial and summary policy sets differ")
    return trials, summary.set_index("policy", drop=False)


def verify_pairing(trials: pd.DataFrame) -> dict[str, Any]:
    seed_sets = {
        policy: tuple(sorted(group["seed"].astype(int).tolist()))
        for policy, group in trials.groupby("policy", sort=True)
    }
    unique_sets = {seeds for seeds in seed_sets.values()}
    paired = len(unique_sets) == 1
    expected = tuple(range(260_901, 261_201))
    frozen_seed_range = paired and next(iter(unique_sets), ()) == expected
    return {
        "paired_policy_seed_sets": paired,
        "frozen_nominal_seed_range_matches": frozen_seed_range,
        "worlds_per_policy": len(next(iter(unique_sets), ())),
        "first_seed": expected[0] if frozen_seed_range else None,
        "last_seed": expected[-1] if frozen_seed_range else None,
    }


def verify_nonbootstrap_summary(
    trials: pd.DataFrame,
    summary: pd.DataFrame,
    *,
    absolute_tolerance: float = 1e-12,
) -> dict[str, Any]:
    rows: dict[str, Any] = {}
    all_match = True
    for policy in sorted(summary.index):
        group = trials.loc[trials["policy"] == policy]
        field_results: dict[str, Any] = {}
        for field, calculator in SUMMARY_FIELDS.items():
            calculated = calculator(group)
            published = summary.at[policy, field]
            if field == "n":
                published = int(published)
                calculated = int(calculated)
                matches = calculated == published
                difference = calculated - published
            else:
                published = float(published)
                difference = float(calculated) - published
                matches = bool(
                    np.isclose(calculated, published, rtol=0.0, atol=absolute_tolerance)
                )
            all_match = all_match and matches
            field_results[field] = {
                "calculated": calculated,
                "published": published,
                "difference": difference,
                "matches": matches,
            }
        rows[policy] = field_results
    return {
        "absolute_tolerance": absolute_tolerance,
        "all_nonbootstrap_statistics_match": all_match,
        "policies": rows,
    }


def _policy_rng(seed: int, policy: str) -> np.random.Generator:
    """Return a stable, explicitly separated stream for one policy."""

    try:
        policy_index = POLICY_ORDER.index(policy)
    except ValueError as exc:
        raise BootstrapAuditError(f"unknown policy {policy!r}") from exc
    sequence = np.random.SeedSequence([int(seed), policy_index])
    return np.random.Generator(np.random.PCG64(sequence))


def audit_bootstrap_ci(
    values: np.ndarray,
    *,
    rng: np.random.Generator,
    resamples: int = AUDIT_RESAMPLES,
    confidence_level: float = AUDIT_CONFIDENCE_LEVEL,
    batch_size: int = AUDIT_BATCH_SIZE,
) -> tuple[float, float]:
    """Compute the declared audit interval without implying provenance."""

    sample = np.sort(np.asarray(values, dtype=float))
    if sample.ndim != 1 or sample.size < 2 or not np.all(np.isfinite(sample)):
        raise BootstrapAuditError("bootstrap values must be a finite 1-D sample")
    if resamples <= 0 or batch_size <= 0:
        raise BootstrapAuditError("resamples and batch_size must be positive")
    if not 0.0 < confidence_level < 1.0:
        raise BootstrapAuditError("confidence_level must lie strictly between 0 and 1")

    medians = np.empty(resamples, dtype=float)
    for start in range(0, resamples, batch_size):
        stop = min(start + batch_size, resamples)
        indices = rng.integers(0, sample.size, size=(stop - start, sample.size))
        medians[start:stop] = np.median(sample[indices], axis=1)
    alpha = 1.0 - confidence_level
    low, high = np.quantile(
        medians,
        [alpha / 2.0, 1.0 - alpha / 2.0],
        method=AUDIT_QUANTILE_METHOD,
    )
    return float(low), float(high)


def run_audit(
    trials_path: Path = DEFAULT_TRIALS,
    summary_path: Path = DEFAULT_SUMMARY,
    *,
    seed: int = AUDIT_SEED,
    resamples: int = AUDIT_RESAMPLES,
) -> dict[str, Any]:
    trials_path = Path(trials_path)
    summary_path = Path(summary_path)
    hashes = verify_frozen_hashes(trials_path, summary_path)
    trials, summary = load_nominal_inputs(trials_path, summary_path)
    pairing = verify_pairing(trials)
    nonbootstrap = verify_nonbootstrap_summary(trials, summary)

    candidate_rows: dict[str, Any] = {}
    endpoint_matches: list[bool] = []
    for policy in sorted(summary.index):
        values = trials.loc[
            trials["policy"] == policy, "position_error_final_m"
        ].to_numpy()
        low, high = audit_bootstrap_ci(
            values,
            rng=_policy_rng(seed, policy),
            resamples=resamples,
        )
        published_low = float(summary.at[policy, "median_position_error_ci95_lo"])
        published_high = float(summary.at[policy, "median_position_error_ci95_hi"])
        exact_low = low == published_low
        exact_high = high == published_high
        endpoint_matches.extend((exact_low, exact_high))
        candidate_rows[policy] = {
            "audit_ci95": [low, high],
            "published_ci95": [published_low, published_high],
            "difference_audit_minus_published": [
                low - published_low,
                high - published_high,
            ],
            "exact_endpoint_match": [exact_low, exact_high],
        }

    return {
        "audit_result": "PASS_WITH_PROVENANCE_LIMITATION",
        "provenance": {
            "status": PROVENANCE_STATUS,
            "exact_historical_reconstruction_claimed": False,
            "reason": (
                "Release 1.0.0 stores the interval endpoints but not the bootstrap "
                "generator, PRNG seed/state, resample count, stream allocation, or "
                "quantile implementation. Endpoint values do not uniquely identify "
                "those historical choices."
            ),
        },
        "frozen_inputs": hashes,
        "pairing": pairing,
        "nonbootstrap_reproduction": nonbootstrap,
        "declared_audit_bootstrap": {
            "purpose": "deterministic sensitivity check; not recovered provenance",
            "algorithm": AUDIT_ALGORITHM,
            "bit_generator": AUDIT_BIT_GENERATOR,
            "base_seed": seed,
            "policy_stream": "SeedSequence([base_seed, fixed_policy_index])",
            "policy_order": list(POLICY_ORDER),
            "resamples": resamples,
            "confidence_level": AUDIT_CONFIDENCE_LEVEL,
            "quantile_method": AUDIT_QUANTILE_METHOD,
            "sort_input_before_resampling": True,
            "published_endpoints_all_exactly_match": all(endpoint_matches),
            "policies": candidate_rows,
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit nominal CI provenance without claiming false exactness."
    )
    parser.add_argument("--trials", type=Path, default=DEFAULT_TRIALS)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--seed", type=int, default=AUDIT_SEED)
    parser.add_argument("--resamples", type=int, default=AUDIT_RESAMPLES)
    parser.add_argument(
        "--require-identifiable-provenance",
        action="store_true",
        help=(
            "return a non-zero status because release 1.0.0 does not contain "
            "enough metadata to identify its historical bootstrap"
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run_audit(
        args.trials,
        args.summary,
        seed=args.seed,
        resamples=args.resamples,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.require_identifiable_provenance:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
