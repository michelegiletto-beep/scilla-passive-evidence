import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "software"))

import bootstrap_nominal as bootstrap


class TestBootstrapProvenance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.trials, cls.summary = bootstrap.load_nominal_inputs()

    def test_frozen_nominal_hashes_match(self):
        result = bootstrap.verify_frozen_hashes(
            bootstrap.DEFAULT_TRIALS,
            bootstrap.DEFAULT_SUMMARY,
        )
        self.assertTrue(result["canonical_inputs"])
        self.assertTrue(result["all_frozen_hashes_match"])

    def test_pairing_and_seed_semantics_match(self):
        result = bootstrap.verify_pairing(self.trials)
        self.assertTrue(result["paired_policy_seed_sets"])
        self.assertTrue(result["frozen_nominal_seed_range_matches"])
        self.assertEqual(result["worlds_per_policy"], 300)
        self.assertEqual(result["first_seed"], 260_901)
        self.assertEqual(result["last_seed"], 261_200)

    def test_all_nonbootstrap_statistics_reproduce(self):
        result = bootstrap.verify_nonbootstrap_summary(self.trials, self.summary)
        self.assertTrue(result["all_nonbootstrap_statistics_match"])

    def test_declared_audit_bootstrap_is_deterministic_and_order_invariant(self):
        values = self.trials.loc[
            self.trials["policy"] == "METROLOGY_CONDITIONED_EIG",
            "position_error_final_m",
        ].to_numpy()
        first = bootstrap.audit_bootstrap_ci(
            values,
            rng=bootstrap._policy_rng(1234, "METROLOGY_CONDITIONED_EIG"),
            resamples=500,
        )
        second = bootstrap.audit_bootstrap_ci(
            values[::-1],
            rng=bootstrap._policy_rng(1234, "METROLOGY_CONDITIONED_EIG"),
            resamples=500,
        )
        self.assertEqual(first, second)

    def test_audit_explicitly_refuses_historical_exactness_claim(self):
        result = bootstrap.run_audit(resamples=500)
        self.assertEqual(
            result["provenance"]["status"],
            bootstrap.PROVENANCE_STATUS,
        )
        self.assertFalse(
            result["provenance"]["exact_historical_reconstruction_claimed"]
        )
        self.assertEqual(result["audit_result"], "PASS_WITH_PROVENANCE_LIMITATION")
        self.assertIn(
            "not recovered provenance",
            result["declared_audit_bootstrap"]["purpose"],
        )

    def test_hash_guard_rejects_modified_canonical_named_input(self):
        # Custom paths are inspectable but are never mislabeled as canonical.
        with tempfile.TemporaryDirectory() as directory:
            trials_path = Path(directory) / "nominal_trials.csv"
            summary_path = Path(directory) / "nominal_policy_summary.csv"
            trials_path.write_bytes(bootstrap.DEFAULT_TRIALS.read_bytes() + b"\n")
            summary_path.write_bytes(bootstrap.DEFAULT_SUMMARY.read_bytes())
            result = bootstrap.verify_frozen_hashes(trials_path, summary_path)
            self.assertFalse(result["canonical_inputs"])
            self.assertFalse(result["all_frozen_hashes_match"])

    def test_strict_cli_returns_nonzero_and_machine_readable_audit(self):
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "software" / "bootstrap_nominal.py"),
                "--resamples",
                "100",
                "--require-identifiable-provenance",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 2)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["provenance"]["status"], bootstrap.PROVENANCE_STATUS)

    def test_bootstrap_input_validation(self):
        with self.assertRaises(bootstrap.BootstrapAuditError):
            bootstrap.audit_bootstrap_ci(
                np.array([1.0]),
                rng=bootstrap._policy_rng(1, "NO_PASSIVE"),
                resamples=10,
            )
        with self.assertRaises(bootstrap.BootstrapAuditError):
            bootstrap._policy_rng(1, "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
