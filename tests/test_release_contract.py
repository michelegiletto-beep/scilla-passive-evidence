import csv
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "software"))
import scilla_passive_core as core
import run_release


TRIAL_FIELDS = [
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
]


class TestFrozenReleaseContract(unittest.TestCase):
    def test_frozen_nominal_archive_hash_and_schema(self):
        path = ROOT / "results" / "nominal_trials.csv"
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(
            digest, "5251ea88da0c076d5df73dff03e30c88bcbaa262fe843ee0f13dd2b4ceb615f8"
        )
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            self.assertEqual(reader.fieldnames, TRIAL_FIELDS)
            rows = list(reader)
        self.assertEqual(len(rows), 1500)
        self.assertEqual([row["policy"] for row in rows[:5]], core.POLICIES)

    def test_selected_legacy_rows_reproduce_numerically(self):
        with (ROOT / "results" / "nominal_trials.csv").open(
            newline="", encoding="utf-8"
        ) as handle:
            archived = {
                (int(row["seed"]), row["policy"]): row for row in csv.DictReader(handle)
            }
        for seed in (260901, 260917, 261000, 261200):
            for actual in core.run_world_all(seed, model_version=core.LEGACY_MODEL_VERSION):
                expected = archived[(seed, actual["policy"])]
                self.assertEqual(list(actual), TRIAL_FIELDS)
                for field in TRIAL_FIELDS[2:5]:
                    self.assertAlmostEqual(
                        actual[field], float(expected[field]), delta=1e-10
                    )
                for field in TRIAL_FIELDS[5:]:
                    self.assertEqual(actual[field], int(expected[field]))

    def test_config_maps_to_core_and_declares_boundary(self):
        config = json.loads((ROOT / "config" / "release_config.json").read_text())
        self.assertEqual(config["release"], core.LEGACY_MODEL_VERSION)
        self.assertEqual(config["process_models"]["published_frozen"]["id"], core.LEGACY_MODEL_VERSION)
        self.assertEqual(config["process_models"]["corrected_candidate"]["id"], core.CANDIDATE_MODEL_VERSION)
        self.assertEqual(config["process_models"]["library_default"], core.DEFAULT_MODEL_VERSION)
        self.assertEqual(config["estimator"]["process_accel_sigma_mps2"], 0.12)
        self.assertEqual(config["estimator"]["nis_gate_1dof"], core.NIS_GATE)
        self.assertEqual(config["policies"], core.POLICIES)
        self.assertEqual(config["physics"]["carrier_hz"], core.FC)
        self.assertEqual(config["receiver_model"]["async_sigma_m"], core.ASYNC_SIGMA_M)


class TestRunnerContract(unittest.TestCase):
    def test_cli_requires_explicit_model_version(self):
        parser = run_release.build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["--mode", "quick"])

    def test_refuse_then_force_overwrite_preserves_unrelated_file(self):
        original_count = run_release.MODE_WORLD_COUNTS["quick"]
        run_release.MODE_WORLD_COUNTS["quick"] = 1
        try:
            with tempfile.TemporaryDirectory() as directory:
                out = Path(directory)
                marker = out / "do-not-delete.txt"
                marker.write_text("keep", encoding="utf-8")
                first = run_release.run_release(
                    mode="quick",
                    out=out,
                    model_version=core.LEGACY_MODEL_VERSION,
                    workers=1,
                )
                self.assertEqual(first["model_version"], core.LEGACY_MODEL_VERSION)
                before = (out / run_release.TRIALS_FILENAME).read_bytes()
                with self.assertRaises(FileExistsError):
                    run_release.run_release(
                        mode="quick",
                        out=out,
                        model_version=core.LEGACY_MODEL_VERSION,
                        workers=1,
                    )
                self.assertEqual(before, (out / run_release.TRIALS_FILENAME).read_bytes())
                run_release.run_release(
                    mode="quick",
                    out=out,
                    model_version=core.CANDIDATE_MODEL_VERSION,
                    force=True,
                    workers=1,
                )
                summary = json.loads((out / run_release.SUMMARY_FILENAME).read_text())
                self.assertEqual(summary["model_version"], core.CANDIDATE_MODEL_VERSION)
                self.assertEqual(marker.read_text(), "keep")
                self.assertFalse(list(out.glob(".*.tmp")))
        finally:
            run_release.MODE_WORLD_COUNTS["quick"] = original_count


if __name__ == "__main__":
    unittest.main()
