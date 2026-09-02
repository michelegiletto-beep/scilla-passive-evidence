import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "software"))

import generate_stress_figures as figures  # noqa: E402
import run_stress as stress  # noqa: E402


class TestStressDefinition(unittest.TestCase):
    def test_grid_cardinality_and_order(self):
        self.assertEqual(len(stress.PHYSICS_GRID), 54)
        self.assertEqual(stress.PHYSICS_GRID[0], {"n_donors": 4, "clutter_db": 5, "rcs": 10, "donor_sigma": 30})
        self.assertEqual(stress.PHYSICS_GRID[-1], {"n_donors": 20, "clutter_db": 25, "rcs": 1000, "donor_sigma": 100})
        self.assertEqual(len(stress.INTEGRITY_GRID), 27)
        self.assertEqual(stress.INTEGRITY_GRID[0], {"maneuver_deg": 0, "assoc_error_prob": 0.0, "outlier_prob": 0.0})
        self.assertEqual(stress.INTEGRITY_GRID[-1], {"maneuver_deg": 45, "assoc_error_prob": 0.15, "outlier_prob": 0.15})

    def test_seed_schedule(self):
        physics = list(stress._jobs(stress.PHYSICS_GRID, 300_000, 30))
        integrity = list(stress._jobs(stress.INTEGRITY_GRID, 500_000, 30))
        self.assertEqual((physics[0][0], physics[0][1]), (1, 301_000))
        self.assertEqual((physics[-1][0], physics[-1][1]), (54, 354_029))
        self.assertEqual((integrity[0][0], integrity[0][1]), (1, 501_000))
        self.assertEqual((integrity[-1][0], integrity[-1][1]), (27, 527_029))
        self.assertEqual(physics[0][3], stress.core.LEGACY_MODEL_VERSION)

    def test_candidate_model_is_explicitly_selectable(self):
        jobs = list(
            stress._jobs(
                stress.PHYSICS_GRID[:1],
                300_000,
                1,
                stress.core.CANDIDATE_MODEL_VERSION,
            )
        )
        self.assertEqual(jobs[0][3], stress.core.CANDIDATE_MODEL_VERSION)
        candidate = stress._run_grid(
            stress.PHYSICS_GRID[:1],
            stress.PHYSICS_DIMENSIONS,
            300_000,
            1,
            1,
            stress.core.CANDIDATE_MODEL_VERSION,
        )
        self.assertEqual(len(candidate), len(stress.core.POLICIES))
        self.assertTrue((candidate["seed"] == 301_000).all())

    def test_first_world_matches_frozen(self):
        generated = stress._run_grid(
            stress.PHYSICS_GRID[:1], stress.PHYSICS_DIMENSIONS, 300_000, 1, 1
        )
        frozen = pd.read_csv(
            ROOT / "results/physics_robustness_trials.csv", float_precision="round_trip"
        ).head(5)
        pd.testing.assert_frame_equal(generated.reset_index(drop=True), frozen.reset_index(drop=True))


class TestFrozenTransforms(unittest.TestCase):
    def _roundtrip_exact(self, generated: pd.DataFrame, frozen_name: str):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / frozen_name
            stress._write_csv(generated, output)
            expected = ROOT / "results" / frozen_name
            self.assertEqual(output.read_bytes(), expected.read_bytes())

    def test_physics_summary_exact(self):
        trials = pd.read_csv(
            ROOT / "results/physics_robustness_trials.csv", float_precision="round_trip"
        )
        summary = stress.summarize_scenarios(trials, stress.PHYSICS_DIMENSIONS)
        self._roundtrip_exact(summary, "physics_robustness_scenario_summary.csv")

    def test_integrity_summary_exact(self):
        trials = pd.read_csv(
            ROOT / "results/integrity_stress_trials.csv", float_precision="round_trip"
        )
        summary = stress.summarize_scenarios(trials, stress.INTEGRITY_DIMENSIONS)
        self._roundtrip_exact(summary, "integrity_stress_scenario_summary.csv")

    def test_integrity_gate_exact(self):
        trials = pd.read_csv(
            ROOT / "results/integrity_stress_trials.csv", float_precision="round_trip"
        )
        gate = stress.integrity_gate_statistics(trials)
        self._roundtrip_exact(gate, "integrity_gate_statistics.csv")

    def test_frozen_hashes_are_immutable(self):
        for name, expected in stress.FROZEN_CSV_SHA256.items():
            digest = hashlib.sha256((ROOT / "results" / name).read_bytes()).hexdigest()
            self.assertEqual(digest, expected, name)


class TestFigureData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.physics = pd.read_csv(
            ROOT / "results/physics_robustness_scenario_summary.csv", float_precision="round_trip"
        )
        cls.integrity = pd.read_csv(
            ROOT / "results/integrity_stress_scenario_summary.csv", float_precision="round_trip"
        )

    def test_physics_ratio_definition(self):
        data = figures.physics_plot_data(self.physics)
        expected = self.physics["no_passive_median_m"] / self.physics["metrology_eig_median_m"]
        np.testing.assert_array_equal(data["error_ratio"].to_numpy(), expected.to_numpy())

    def test_preserved_failure_rows(self):
        table = figures.failure_table_data(self.physics)
        self.assertEqual(len(table), 3)
        self.assertEqual(table["Donors"].tolist(), [4, 4, 4])
        self.assertEqual(table["Clutter dB"].tolist(), [15, 25, 25])

    def test_integrity_bar_values(self):
        data = figures.integrity_plot_data(self.integrity)
        self.assertEqual(len(data), 9)
        np.testing.assert_allclose(
            data["fraction"].to_numpy(),
            np.array([5 / 9, 4 / 9, 3 / 9, 5 / 9, 3 / 9, 4 / 9, 6 / 9, 4 / 9, 2 / 9]),
            rtol=0,
            atol=0,
        )


if __name__ == "__main__":
    unittest.main()
