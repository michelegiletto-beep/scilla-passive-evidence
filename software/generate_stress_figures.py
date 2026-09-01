#!/usr/bin/env python3
"""Regenerate Figures 03--05 from SCILLA PASSIVE stress summaries."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402


def physics_plot_data(summary: pd.DataFrame) -> pd.DataFrame:
    data = summary[["rcs", "n_donors", "no_passive_median_m", "metrology_eig_median_m"]].copy()
    data["error_ratio"] = data["no_passive_median_m"] / data["metrology_eig_median_m"]
    return data


def failure_table_data(summary: pd.DataFrame) -> pd.DataFrame:
    failures = summary.loc[summary["metrology_eig_beats_no_passive"] == 0].copy()
    return pd.DataFrame(
        {
            "Donors": failures["n_donors"].astype(int),
            "Clutter dB": failures["clutter_db"].astype(int),
            "RCS m²": failures["rcs"].astype(int),
            "Donor σ m": failures["donor_sigma"].astype(int),
            "No-passive m": failures["no_passive_median_m"].round().astype(int),
            "Passive m": failures["metrology_eig_median_m"].round().astype(int),
        }
    )


def integrity_plot_data(summary: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    for dimension in ("maneuver_deg", "assoc_error_prob", "outlier_prob"):
        for value, group in summary.groupby(dimension, sort=True):
            records.append(
                {
                    "label": f"{dimension}={value}",
                    "fraction": float(group["metrology_eig_beats_best_simple"].mean()),
                }
            )
    return pd.DataFrame(records)


def figure_physics(summary: pd.DataFrame, target: Path) -> None:
    data = physics_plot_data(summary)
    fig, ax = plt.subplots(figsize=(11, 7.12))
    ax.scatter(
        data["rcs"],
        data["error_ratio"],
        s=35 + 7 * data["n_donors"],
        alpha=0.65,
        edgecolors="#1f77b4",
        linewidths=1.2,
    )
    ax.axhline(1.0, color="#1f77b4", linestyle="--", linewidth=2)
    ax.set_xscale("log")
    ax.set_xlabel("Bistatic RCS sensitivity point (m^2)", fontsize=14)
    ax.set_ylabel("Median error ratio: no-passive / passive", fontsize=14)
    ax.set_title(
        "Physics robustness across 54 frozen scenarios\n"
        "marker size scales with candidate-donor count",
        fontsize=18,
    )
    ax.tick_params(labelsize=13)
    fig.tight_layout()
    fig.savefig(target, dpi=170)
    plt.close(fig)


def figure_failures(summary: pd.DataFrame, target: Path) -> None:
    table_data = failure_table_data(summary)
    fig, ax = plt.subplots(figsize=(11, 6.21))
    ax.axis("off")
    ax.set_title(
        "Preserved physics failure regimes: no simulated benefit vs propagation baseline",
        fontsize=18,
        pad=22,
    )
    table = ax.table(
        cellText=table_data.values,
        colLabels=table_data.columns,
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(14)
    table.scale(1.08, 1.8)
    fig.tight_layout()
    fig.savefig(target, dpi=170)
    plt.close(fig)


def figure_integrity(summary: pd.DataFrame, target: Path) -> None:
    data = integrity_plot_data(summary)
    fig, ax = plt.subplots(figsize=(11, 6.37))
    positions = np.arange(len(data))
    ax.bar(positions, data["fraction"], color="#1f77b4")
    ax.axhline(0.5, color="#1f77b4", linestyle="--", linewidth=2)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Fraction of scenario cells beating best simple baseline", fontsize=14)
    ax.set_title("Optimizer/donor-selection stress: advantage is not robust", fontsize=18)
    ax.set_xticks(positions, data["label"], rotation=36, ha="right")
    ax.tick_params(labelsize=12)
    fig.tight_layout()
    fig.savefig(target, dpi=190)
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("reproduction_stress"))
    parser.add_argument("--out", type=Path, default=Path("reproduction_stress/figures"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    physics = pd.read_csv(
        args.input / "physics_robustness_scenario_summary.csv", float_precision="round_trip"
    )
    integrity = pd.read_csv(
        args.input / "integrity_stress_scenario_summary.csv", float_precision="round_trip"
    )
    figure_physics(physics, args.out / "Fig03_physics_robustness.png")
    figure_failures(physics, args.out / "Fig04_preserved_failure_regimes.png")
    figure_integrity(integrity, args.out / "Fig05_integrity_selection_stress.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
