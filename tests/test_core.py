import copy
import math
import pickle
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "software"))
import scilla_passive_core as s


class TestDeclaredPhysics(unittest.TestCase):
    def test_scan_period_and_dwell(self):
        self.assertAlmostEqual(s.SCAN_PERIOD, 2.5, places=12)
        self.assertAlmostEqual(s.dwell_s(), 0.0125, places=12)

    def test_horizon_goldens(self):
        self.assertAlmostEqual(s.H_TX_TGT, 33.64337318519364, places=12)
        self.assertAlmostEqual(s.H_RX_TGT, 35.61040723909894, places=12)
        self.assertAlmostEqual(s.H_TX_RX, 43.18515304705361, places=12)

    def test_pulse_sigma_goldens_and_order(self):
        expected = {
            "S1": 20.89734839156442,
            "S2": 23.84358605606869,
            "M1": 32.77295201919737,
            "M2": 47.669766334316876,
            "M3": 63.79590096426263,
            "L": 105.75945416293435,
        }
        values = [s.base_meas_sigma(mode) for mode in s.MODE_NAMES]
        for mode, value in expected.items():
            self.assertAlmostEqual(s.base_meas_sigma(mode), value, places=12)
        self.assertEqual(values, sorted(values))

    def test_bistatic_zero_at_target_on_tx(self):
        rx = np.array([0.0, 0.0])
        tx = np.array([1000.0, 0.0])
        x = np.array([1000.0, 0.0, 0.0, 0.0])
        self.assertAlmostEqual(s.h(x, tx, rx), 0.0, places=12)

    def test_state_jacobian_matches_finite_difference(self):
        x = np.array([1400.0, -600.0, 4.0, -2.0])
        tx = np.array([-2100.0, 1700.0])
        rx = np.array([250.0, 100.0])
        analytic = s.H(x, tx, rx)[0, :2]
        epsilon = 1e-3
        numeric = []
        for axis in range(2):
            plus = x.copy()
            minus = x.copy()
            plus[axis] += epsilon
            minus[axis] -= epsilon
            numeric.append((s.h(plus, tx, rx) - s.h(minus, tx, rx)) / (2 * epsilon))
        np.testing.assert_allclose(analytic, numeric, rtol=0.0, atol=2e-9)

    def test_donor_jacobian_matches_finite_difference(self):
        x = np.array([1400.0, -600.0, 4.0, -2.0])
        tx = np.array([-2100.0, 1700.0])
        rx = np.array([250.0, 100.0])
        analytic = s.donor_jacobian(x, tx, rx)
        epsilon = 1e-3
        numeric = []
        for axis in range(2):
            plus = tx.copy()
            minus = tx.copy()
            plus[axis] += epsilon
            minus[axis] -= epsilon
            numeric.append((s.h(x, plus, rx) - s.h(x, minus, rx)) / (2 * epsilon))
        np.testing.assert_allclose(analytic, numeric, rtol=0.0, atol=2e-9)

    def test_effective_variance_oracle(self):
        x = np.array([3000.0, 4000.0, 0.0, 0.0])
        tx = np.array([-5000.0, 2000.0])
        rx = np.array([0.0, 0.0])
        donor_sigma = 30.0
        jacobian = s.donor_jacobian(x, tx, rx)
        expected_variance = (
            s.base_meas_sigma("M1") ** 2
            + donor_sigma**2 * float(jacobian @ jacobian)
        )
        self.assertAlmostEqual(
            s.effective_sigma(x, tx, rx, "M1", donor_sigma) ** 2,
            expected_variance,
            places=10,
        )

    def test_singular_jacobians_raise_instead_of_masking(self):
        rx = np.array([0.0, 0.0])
        tx = np.array([1000.0, 0.0])
        with self.assertRaises(s.GeometryError):
            s.H(np.array([0.0, 0.0, 0.0, 0.0]), tx, rx)
        with self.assertRaises(s.GeometryError):
            s.H(np.array([1000.0, 0.0, 0.0, 0.0]), tx, rx)
        with self.assertRaises(s.GeometryError):
            s.donor_jacobian(np.array([1000.0, 0.0, 0.0, 0.0]), tx, rx)
        with self.assertRaises(s.GeometryError):
            s.donor_jacobian(np.array([500.0, 0.0, 0.0, 0.0]), rx, rx)


class TestProcessModels(unittest.TestCase):
    def setUp(self):
        self.x = np.array([1200.0, -400.0, 5.0, -2.0])
        self.P = np.array(
            [
                [900.0, 20.0, 4.0, 0.0],
                [20.0, 700.0, 0.0, 3.0],
                [4.0, 0.0, 2.0, 0.1],
                [0.0, 3.0, 0.1, 1.5],
            ]
        )

    def test_default_is_candidate_but_versions_are_explicit(self):
        self.assertEqual(s.DEFAULT_MODEL_VERSION, s.CANDIDATE_MODEL_VERSION)
        self.assertEqual(s.MODEL_VERSIONS, ("1.0.0", "1.1.0-candidate"))

    def test_legacy_process_noise_exact_formula(self):
        dt = 0.7
        q = 0.12
        gain = np.array(
            [[0.5 * dt * dt, 0], [0, 0.5 * dt * dt], [dt, 0], [0, dt]],
            float,
        )
        expected = gain @ (q * q * np.eye(2)) @ gain.T
        np.testing.assert_array_equal(
            s.process_noise(dt, q, model_version=s.LEGACY_MODEL_VERSION), expected
        )

    def test_candidate_process_noise_exact_cwna_formula(self):
        dt = 0.7
        q = 0.12
        expected = q**2 * np.array(
            [
                [dt**3 / 3, 0, dt**2 / 2, 0],
                [0, dt**3 / 3, 0, dt**2 / 2],
                [dt**2 / 2, 0, dt, 0],
                [0, dt**2 / 2, 0, dt],
            ]
        )
        np.testing.assert_array_equal(
            s.process_noise(dt, q, model_version=s.CANDIDATE_MODEL_VERSION), expected
        )

    def test_candidate_prediction_is_partition_invariant(self):
        direct_x, direct_P = s.predict(
            self.x, self.P, 1.7, model_version=s.CANDIDATE_MODEL_VERSION
        )
        split_x, split_P = s.predict(
            self.x, self.P, 0.4, model_version=s.CANDIDATE_MODEL_VERSION
        )
        split_x, split_P = s.predict(
            split_x, split_P, 1.3, model_version=s.CANDIDATE_MODEL_VERSION
        )
        np.testing.assert_allclose(split_x, direct_x, rtol=0.0, atol=2e-13)
        np.testing.assert_allclose(split_P, direct_P, rtol=0.0, atol=2e-12)

    def test_legacy_prediction_is_not_partition_invariant(self):
        _direct_x, direct_P = s.predict(
            self.x, self.P, 1.7, model_version=s.LEGACY_MODEL_VERSION
        )
        split_x, split_P = s.predict(
            self.x, self.P, 0.4, model_version=s.LEGACY_MODEL_VERSION
        )
        _split_x, split_P = s.predict(
            split_x, split_P, 1.3, model_version=s.LEGACY_MODEL_VERSION
        )
        self.assertGreater(float(np.max(np.abs(split_P - direct_P))), 1e-4)

    def test_non_psd_covariance_is_rejected(self):
        bad = np.diag([1.0, 1.0, 1.0, -0.1])
        with self.assertRaises(s.CovarianceError):
            s.predict(self.x, bad, 1.0)

    def test_unknown_model_is_rejected(self):
        with self.assertRaises(ValueError):
            s.predict(self.x, self.P, 1.0, model_version="future-magic")


class TestFilterAndReplay(unittest.TestCase):
    def setUp(self):
        self.x = np.array([1000.0, 500.0, 4.0, -1.0])
        self.P = np.diag([400.0, 625.0, 4.0, 4.0])
        self.tx = np.array([-2500.0, 1800.0])
        self.rx = np.array([0.0, 0.0])
        self.sigma = 30.0

    def test_nis_gate_accepts_equality_and_rejects_above(self):
        predicted = s.h(self.x, self.tx, self.rx)
        _innovation, variance, _jacobian = s.innovation_stats(
            self.x, self.P, predicted, self.tx, self.rx, self.sigma
        )
        at_gate = predicted + math.sqrt(s.NIS_GATE * variance)
        _x, _P, accepted, nis = s.update(
            self.x, self.P, at_gate, self.tx, self.rx, self.sigma
        )
        self.assertTrue(accepted)
        self.assertAlmostEqual(nis, s.NIS_GATE, places=12)
        above_gate = predicted + math.sqrt((s.NIS_GATE + 1e-6) * variance)
        _x, _P, accepted, nis = s.update(
            self.x, self.P, above_gate, self.tx, self.rx, self.sigma
        )
        self.assertFalse(accepted)
        self.assertGreater(nis, s.NIS_GATE)

    def test_joseph_update_is_symmetric_psd(self):
        measurement = s.h(self.x, self.tx, self.rx) + 3.0
        _x, posterior, accepted, _nis = s.update(
            self.x, self.P, measurement, self.tx, self.rx, self.sigma
        )
        self.assertTrue(accepted)
        np.testing.assert_allclose(posterior, posterior.T, rtol=0.0, atol=1e-13)
        self.assertGreaterEqual(float(np.min(np.linalg.eigvalsh(posterior))), -1e-12)

    def test_post_trace_matches_zero_innovation_joseph_update(self):
        expected = s.post_trace(self.x, self.P, self.tx, self.rx, self.sigma)
        _x, posterior, accepted, _nis = s.update(
            self.x,
            self.P,
            s.h(self.x, self.tx, self.rx),
            self.tx,
            self.rx,
            self.sigma,
        )
        self.assertTrue(accepted)
        self.assertAlmostEqual(expected, float(np.trace(posterior[:2, :2])), places=10)

    def test_paired_world_is_deterministic(self):
        first = s.run_world_all(
            12345,
            duration=10,
            n_donors=4,
            model_version=s.CANDIDATE_MODEL_VERSION,
        )
        second = s.run_world_all(
            12345,
            duration=10,
            n_donors=4,
            model_version=s.CANDIDATE_MODEL_VERSION,
        )
        self.assertEqual(first, second)
        self.assertEqual(len(first), len(s.POLICIES))

    def test_event_input_order_does_not_change_results(self):
        world = s.generate_world(54321, duration=12, n_donors=6)
        shuffled = copy.deepcopy(world)
        shuffled["events"] = list(reversed(shuffled["events"]))
        for model_version in s.MODEL_VERSIONS:
            for policy in s.POLICIES:
                self.assertEqual(
                    s.replay(world, policy, model_version=model_version),
                    s.replay(shuffled, policy, model_version=model_version),
                )

    def test_replay_does_not_mutate_world(self):
        world = s.generate_world(24680, duration=8, n_donors=5)
        before = pickle.dumps(world, protocol=5)
        s.replay(world, "RANDOM", model_version=s.CANDIDATE_MODEL_VERSION)
        self.assertEqual(before, pickle.dumps(world, protocol=5))

    def test_candidate_rejected_event_is_propagation_neutral(self):
        world = s.generate_world(8080, duration=2, n_donors=0)
        world["events"] = [
            {
                "t": 0.4,
                "donor_id": 0,
                "mode": "S1",
                "snr": 80.0,
                "tx_true": np.array([8000.0, -3000.0]),
                "tx_est": np.array([8000.0, -3000.0]),
                "z": 1e12,
                "assoc_bad": False,
                "outlier": True,
            }
        ]
        no_event = s.replay(
            world, "NO_PASSIVE", model_version=s.CANDIDATE_MODEL_VERSION
        )
        rejected = s.replay(
            world, "HIGHEST_SNR", model_version=s.CANDIDATE_MODEL_VERSION
        )
        self.assertEqual(rejected["rejected_measurements"], 1)
        self.assertEqual(
            rejected["position_error_final_m"], no_event["position_error_final_m"]
        )
        self.assertEqual(
            rejected["velocity_error_final_mps"], no_event["velocity_error_final_mps"]
        )
        self.assertEqual(
            rejected["position_sigma_final_m"], no_event["position_sigma_final_m"]
        )

        legacy_no_event = s.replay(
            world, "NO_PASSIVE", model_version=s.LEGACY_MODEL_VERSION
        )
        legacy_rejected = s.replay(
            world, "HIGHEST_SNR", model_version=s.LEGACY_MODEL_VERSION
        )
        self.assertNotEqual(
            legacy_rejected["position_sigma_final_m"],
            legacy_no_event["position_sigma_final_m"],
        )

    def test_unknown_policy_is_rejected(self):
        world = s.generate_world(1, duration=2, n_donors=0)
        with self.assertRaises(ValueError):
            s.replay(world, "SECRET_OPTIMIZER")

    def test_legacy_first_world_golden(self):
        rows = s.run_world_all(260901, model_version=s.LEGACY_MODEL_VERSION)
        expected = {
            "NO_PASSIVE": 348.0688789779367,
            "RANDOM": 4.235183755250229,
            "HIGHEST_SNR": 2.995475863688132,
            "SHORTEST_PULSE": 13.174307899713622,
            "METROLOGY_CONDITIONED_EIG": 18.283662237075742,
        }
        self.assertEqual([row["policy"] for row in rows], s.POLICIES)
        for row in rows:
            self.assertEqual(row["position_error_final_m"], expected[row["policy"]])


if __name__ == "__main__":
    unittest.main()
