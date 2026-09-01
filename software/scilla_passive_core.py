"""Deterministic SCILLA PASSIVE simulation core.

Two process-model versions are deliberately supported:

``1.0.0``
    The exact process-noise and rejected-event behaviour used by the immutable
    Zenodo release. It is retained so the published evidence stays reproducible.

``1.1.0-candidate``
    A corrected continuous-white-noise-acceleration (CWNA) process model. Its
    covariance propagation is invariant to artificial time partitioning, and a
    rejected observation cannot alter the trajectory merely by adding an event
    timestamp.

The candidate is the default for library calls. Publication runners must still
select a model explicitly; see ``software/run_release.py``.
"""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

import numpy as np


C = 299_792_458.0
FC = 3e9
K = 1.380649e-23
T0 = 290.0
PT_W = 30_000.0
GT_DBI = 28.0
GR_DBI = 15.0
BEAM_DEG = 1.8
RPM = 24.0
SCAN_PERIOD = 60 / RPM
NF_DB = 4.0
LOSS_DB = 10.0
PROC_LOSS_DB = 3.0
THRESH_DB = 13.0
ASYNC_SIGMA_M = 20.0
TX_H_M = 25.0
RX_H_M = 30.0
TARGET_H_M = 10.0
K_EARTH = 4 / 3

MODES = {
    "S1": (0.07, 3000),
    "S2": (0.15, 3000),
    "M1": (0.30, 1500),
    "M2": (0.50, 1200),
    "M3": (0.70, 1000),
    "L": (1.20, 600),
}
MODE_NAMES = list(MODES)
POLICIES = [
    "NO_PASSIVE",
    "RANDOM",
    "HIGHEST_SNR",
    "SHORTEST_PULSE",
    "METROLOGY_CONDITIONED_EIG",
]
NIS_GATE = 6.63

LEGACY_MODEL_VERSION = "1.0.0"
CANDIDATE_MODEL_VERSION = "1.1.0-candidate"
MODEL_VERSIONS = (LEGACY_MODEL_VERSION, CANDIDATE_MODEL_VERSION)
DEFAULT_MODEL_VERSION = CANDIDATE_MODEL_VERSION
MODELS = {
    LEGACY_MODEL_VERSION: "published-frozen",
    CANDIDATE_MODEL_VERSION: "corrected-candidate",
}

GEOMETRY_EPS_M = 1e-9
PSD_ABS_TOL = 1e-8
PSD_REL_TOL = 1e-12


class GeometryError(ValueError):
    """A requested Jacobian is undefined at singular geometry."""


class CovarianceError(ValueError):
    """A covariance is malformed, non-finite, or materially non-PSD."""


def _validate_model_version(model_version: str) -> str:
    if model_version not in MODEL_VERSIONS:
        raise ValueError(
            f"unknown model_version {model_version!r}; expected one of {MODEL_VERSIONS}"
        )
    return model_version


def _validate_policy(policy: str) -> str:
    if policy not in POLICIES:
        raise ValueError(f"unknown policy {policy!r}; expected one of {tuple(POLICIES)}")
    return policy


def _validate_covariance(P: np.ndarray, *, name: str = "P") -> np.ndarray:
    arr = np.asarray(P, dtype=float)
    if arr.shape != (4, 4):
        raise CovarianceError(f"{name} must have shape (4, 4), got {arr.shape}")
    if not np.all(np.isfinite(arr)):
        raise CovarianceError(f"{name} contains a non-finite value")
    scale = max(1.0, float(np.max(np.abs(arr))))
    tolerance = PSD_ABS_TOL + PSD_REL_TOL * scale
    if not np.allclose(arr, arr.T, rtol=0.0, atol=tolerance):
        raise CovarianceError(f"{name} is not symmetric within numerical tolerance")
    eig_min = float(np.min(np.linalg.eigvalsh(0.5 * (arr + arr.T))))
    if eig_min < -tolerance:
        raise CovarianceError(f"{name} is not positive semidefinite (min eigenvalue={eig_min})")
    return arr


def _finite_vector(value: Any, *, min_length: int, name: str) -> np.ndarray:
    arr = np.asarray(value, dtype=float)
    if arr.ndim != 1 or arr.size < min_length:
        raise ValueError(f"{name} must be a one-dimensional vector of length >= {min_length}")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} contains a non-finite value")
    return arr


def _unit(vector: np.ndarray, *, context: str) -> np.ndarray:
    norm = float(np.linalg.norm(vector))
    if not math.isfinite(norm) or norm <= GEOMETRY_EPS_M:
        raise GeometryError(f"undefined Jacobian at singular geometry: {context}")
    return vector / norm


def radar_horizon_km(h1: float, h2: float) -> float:
    if not (math.isfinite(h1) and math.isfinite(h2)) or h1 < 0 or h2 < 0:
        raise ValueError("antenna/target heights must be finite and non-negative")
    effective_radius = 6_371_000 * K_EARTH
    return (
        math.sqrt(2 * effective_radius * h1)
        + math.sqrt(2 * effective_radius * h2)
    ) / 1000


H_TX_TGT = radar_horizon_km(TX_H_M, TARGET_H_M)
H_RX_TGT = radar_horizon_km(RX_H_M, TARGET_H_M)
H_TX_RX = radar_horizon_km(TX_H_M, RX_H_M)


def dwell_s() -> float:
    return BEAM_DEG / (RPM * 6)


def rx_power_w(Rt: float, Rr: float, sigma_b: float) -> float:
    if Rt <= 0 or Rr <= 0 or sigma_b < 0:
        raise ValueError("ranges must be positive and bistatic RCS must be non-negative")
    lam = C / FC
    gain_tx = 10 ** (GT_DBI / 10)
    gain_rx = 10 ** (GR_DBI / 10)
    loss = 10 ** (LOSS_DB / 10)
    return (
        PT_W
        * gain_tx
        * gain_rx
        * lam**2
        * sigma_b
        / ((4 * math.pi) ** 3 * Rt**2 * Rr**2 * loss)
    )


def snr_db(Rt: float, Rr: float, mode: str, sigma_b: float, clutter_db: float) -> float:
    if mode not in MODES:
        raise ValueError(f"unknown radar mode {mode!r}")
    pulse_us, prf = MODES[mode]
    noise_factor = 10 ** (NF_DB / 10)
    pulses = prf * dwell_s()
    signal = (
        rx_power_w(Rt, Rr, sigma_b)
        * (pulse_us * 1e-6)
        * pulses
        / (K * T0 * noise_factor)
    )
    return 10 * math.log10(max(signal, 1e-30)) - PROC_LOSS_DB - clutter_db


def base_meas_sigma(mode: str) -> float:
    if mode not in MODES:
        raise ValueError(f"unknown radar mode {mode!r}")
    pulse_us, _ = MODES[mode]
    cell = C * pulse_us * 1e-6 / math.sqrt(12)
    return math.sqrt(cell * cell + ASYNC_SIGMA_M**2)


def donor_jacobian(state: np.ndarray, tx: np.ndarray, rx: np.ndarray) -> np.ndarray:
    """Derivative of bistatic excess path with respect to donor position."""

    p = _finite_vector(state, min_length=2, name="state")[:2]
    txp = _finite_vector(tx, min_length=2, name="tx")[:2]
    rxp = _finite_vector(rx, min_length=2, name="rx")[:2]
    return _unit(txp - p, context="target coincident with donor") - _unit(
        txp - rxp, context="donor coincident with receiver"
    )


def effective_sigma(
    state: np.ndarray,
    tx: np.ndarray,
    rx: np.ndarray,
    mode: str,
    donor_sigma: float,
) -> float:
    if not math.isfinite(donor_sigma) or donor_sigma < 0:
        raise ValueError("donor_sigma must be finite and non-negative")
    jacobian = donor_jacobian(state, tx, rx)
    base = base_meas_sigma(mode)
    variance = base * base + donor_sigma * donor_sigma * float(jacobian @ jacobian)
    if not math.isfinite(variance) or variance <= 0:
        raise ValueError("effective measurement variance is not positive and finite")
    return math.sqrt(variance)


def h(x: np.ndarray, tx: np.ndarray, rx: np.ndarray) -> float:
    state = _finite_vector(x, min_length=2, name="x")
    p = state[:2]
    txp = _finite_vector(tx, min_length=2, name="tx")[:2]
    rxp = _finite_vector(rx, min_length=2, name="rx")[:2]
    return float(
        np.linalg.norm(p - txp)
        + np.linalg.norm(p - rxp)
        - np.linalg.norm(txp - rxp)
    )


def H(x: np.ndarray, tx: np.ndarray, rx: np.ndarray) -> np.ndarray:
    state = _finite_vector(x, min_length=4, name="x")
    p = state[:2]
    txp = _finite_vector(tx, min_length=2, name="tx")[:2]
    rxp = _finite_vector(rx, min_length=2, name="rx")[:2]
    result = np.zeros((1, 4))
    result[0, :2] = _unit(p - txp, context="target coincident with donor") + _unit(
        p - rxp, context="target coincident with receiver"
    )
    return result


def _transition(dt: float) -> np.ndarray:
    return np.array(
        [[1, 0, dt, 0], [0, 1, 0, dt], [0, 0, 1, 0], [0, 0, 0, 1.0]],
        float,
    )


def process_noise(
    dt: float,
    q: float = 0.12,
    *,
    model_version: str = DEFAULT_MODEL_VERSION,
) -> np.ndarray:
    """Return the declared process covariance for a time interval."""

    _validate_model_version(model_version)
    if not math.isfinite(dt) or dt < 0:
        raise ValueError("dt must be finite and non-negative")
    if not math.isfinite(q) or q < 0:
        raise ValueError("q must be finite and non-negative")

    if model_version == LEGACY_MODEL_VERSION:
        # Preserve expression order from the immutable v1.0.0 source.
        gain = np.array(
            [[0.5 * dt * dt, 0], [0, 0.5 * dt * dt], [dt, 0], [0, dt]],
            float,
        )
        return gain @ (q * q * np.eye(2)) @ gain.T

    q2 = q * q
    dt2 = dt * dt
    dt3 = dt2 * dt
    return q2 * np.array(
        [
            [dt3 / 3.0, 0.0, dt2 / 2.0, 0.0],
            [0.0, dt3 / 3.0, 0.0, dt2 / 2.0],
            [dt2 / 2.0, 0.0, dt, 0.0],
            [0.0, dt2 / 2.0, 0.0, dt],
        ],
        dtype=float,
    )


def predict(
    x: np.ndarray,
    P: np.ndarray,
    dt: float,
    q: float = 0.12,
    *,
    model_version: str = DEFAULT_MODEL_VERSION,
) -> tuple[np.ndarray, np.ndarray]:
    state = _finite_vector(x, min_length=4, name="x")
    if state.shape != (4,):
        raise ValueError(f"x must have shape (4,), got {state.shape}")
    covariance = _validate_covariance(P)
    transition = _transition(dt)
    propagated = transition @ covariance @ transition.T + process_noise(
        dt, q, model_version=model_version
    )
    _validate_covariance(propagated, name="predicted covariance")
    return transition @ state, propagated


def innovation_stats(
    x: np.ndarray,
    P: np.ndarray,
    z: float,
    tx: np.ndarray,
    rx: np.ndarray,
    sigma: float,
) -> tuple[float, float, np.ndarray]:
    covariance = _validate_covariance(P)
    if not math.isfinite(z):
        raise ValueError("z must be finite")
    if not math.isfinite(sigma) or sigma <= 0:
        raise ValueError("sigma must be finite and positive")
    jacobian = H(x, tx, rx)
    innovation = float(z - h(x, tx, rx))
    innovation_variance = (jacobian @ covariance @ jacobian.T).item() + sigma * sigma
    if not math.isfinite(innovation_variance) or innovation_variance <= 0:
        raise CovarianceError("innovation variance must be positive and finite")
    return innovation, innovation_variance, jacobian


def update(
    x: np.ndarray,
    P: np.ndarray,
    z: float,
    tx: np.ndarray,
    rx: np.ndarray,
    sigma: float,
) -> tuple[np.ndarray, np.ndarray, bool, float]:
    covariance = _validate_covariance(P)
    innovation, innovation_variance, jacobian = innovation_stats(
        x, covariance, z, tx, rx, sigma
    )
    nis = innovation * innovation / innovation_variance
    if nis > NIS_GATE:
        return np.asarray(x, dtype=float), covariance, False, nis
    gain = (covariance @ jacobian.T) / innovation_variance
    updated_state = np.asarray(x, dtype=float) + gain[:, 0] * innovation
    identity = np.eye(4)
    residual_projection = identity - gain @ jacobian
    updated_covariance = (
        residual_projection @ covariance @ residual_projection.T
        + (gain @ gain.T) * (sigma * sigma)
    )
    updated_covariance = 0.5 * (updated_covariance + updated_covariance.T)
    _validate_covariance(updated_covariance, name="updated covariance")
    return updated_state, updated_covariance, True, nis


def post_trace(
    x: np.ndarray,
    P: np.ndarray,
    tx: np.ndarray,
    rx: np.ndarray,
    sigma: float,
) -> float:
    """Expected posterior position trace used by the EIG selector."""

    covariance = _validate_covariance(P)
    if not math.isfinite(sigma) or sigma <= 0:
        raise ValueError("sigma must be finite and positive")
    jacobian = H(x, tx, rx)
    innovation_variance = (jacobian @ covariance @ jacobian.T).item() + sigma * sigma
    if not math.isfinite(innovation_variance) or innovation_variance <= 0:
        raise CovarianceError("innovation variance must be positive and finite")
    gain = (covariance @ jacobian.T) / innovation_variance
    # Simplified expression retained to preserve legacy donor ranking exactly.
    posterior = (np.eye(4) - gain @ jacobian) @ covariance
    trace = float(np.trace(posterior[:2, :2]))
    tolerance = PSD_ABS_TOL + PSD_REL_TOL * max(1.0, float(np.max(np.abs(covariance))))
    if not math.isfinite(trace) or trace < -tolerance:
        raise CovarianceError(f"posterior position trace is invalid: {trace}")
    return max(0.0, trace)


def truth_at(world: dict[str, Any], t: float) -> np.ndarray:
    p0 = world["truth_p0"]
    v0 = world["truth_v0"]
    maneuver_time = world["maneuver_time_s"]
    theta = world["maneuver_deg"] * math.pi / 180
    if theta == 0 or t <= maneuver_time:
        return np.r_[p0 + v0 * t, v0]
    position_at_maneuver = p0 + v0 * maneuver_time
    cosine, sine = math.cos(theta), math.sin(theta)
    rotation = np.array([[cosine, -sine], [sine, cosine]])
    v1 = rotation @ v0
    return np.r_[position_at_maneuver + v1 * (t - maneuver_time), v1]


def generate_world(
    seed: int,
    duration: int = 60,
    n_donors: int = 12,
    rcs: float = 100,
    clutter_db: float = 10,
    donor_sigma: float = 30,
    active_prob: float = 0.75,
    maneuver_deg: float = 0,
    assoc_error_prob: float = 0,
    outlier_prob: float = 0,
) -> dict[str, Any]:
    if duration <= 0 or int(duration) != duration:
        raise ValueError("duration must be a positive whole number of seconds")
    if n_donors < 0 or int(n_donors) != n_donors:
        raise ValueError("n_donors must be a non-negative integer")
    for name, probability in (
        ("active_prob", active_prob),
        ("assoc_error_prob", assoc_error_prob),
        ("outlier_prob", outlier_prob),
    ):
        if not math.isfinite(probability) or not 0 <= probability <= 1:
            raise ValueError(f"{name} must be in [0, 1]")
    if rcs < 0 or donor_sigma < 0:
        raise ValueError("rcs and donor_sigma must be non-negative")

    rng = np.random.default_rng(seed)
    rx = np.array([0.0, 0.0])
    r0 = rng.uniform(8e3, 18e3)
    a0 = rng.uniform(0, 2 * np.pi)
    speed = rng.uniform(3, 8)
    heading = rng.uniform(0, 2 * np.pi)
    p0 = np.array([r0 * np.cos(a0), r0 * np.sin(a0)])
    v0 = np.array([speed * np.cos(heading), speed * np.sin(heading)])
    cue = np.r_[p0 + rng.normal(0, 300, 2), v0 + rng.normal(0, 1.5, 2)]
    donors: list[dict[str, Any]] = []
    for _ in range(n_donors):
        radius = rng.uniform(5e3, 35e3)
        angle = rng.uniform(0, 2 * np.pi)
        donor_speed = rng.uniform(2, 9)
        donor_heading = rng.uniform(0, 2 * np.pi)
        donors.append(
            {
                "p0": np.array([radius * np.cos(angle), radius * np.sin(angle)]),
                "v": np.array(
                    [donor_speed * np.cos(donor_heading), donor_speed * np.sin(donor_heading)]
                ),
                "phase": rng.uniform(0, SCAN_PERIOD),
                "mode": rng.choice(MODE_NAMES),
                "active": rng.random() < active_prob,
            }
        )

    world: dict[str, Any] = {
        "seed": seed,
        "duration": duration,
        "rx": rx,
        "truth_p0": p0,
        "truth_v0": v0,
        "cue": cue,
        "donors": donors,
        "maneuver_time_s": duration * 0.5,
        "maneuver_deg": maneuver_deg,
        "events": [],
        "donor_sigma": donor_sigma,
    }
    events: list[dict[str, Any]] = []
    for donor_id, donor in enumerate(donors):
        t = donor["phase"]
        while t < duration:
            truth = truth_at(world, t)
            tx = donor["p0"] + donor["v"] * t
            Rt = np.linalg.norm(truth[:2] - tx)
            Rr = np.linalg.norm(truth[:2] - rx)
            Rtr = np.linalg.norm(tx - rx)
            los = (
                Rt / 1000 <= H_TX_TGT
                and Rr / 1000 <= H_RX_TGT
                and Rtr / 1000 <= H_TX_RX
            )
            signal_db = (
                snr_db(Rt, Rr, donor["mode"], rcs, clutter_db)
                if los and donor["active"]
                else -999
            )
            probability = (
                1 / (1 + math.exp(-(signal_db - THRESH_DB) / 2))
                if signal_db > -100
                else 0
            )
            if rng.random() < probability:
                tx_est = tx + rng.normal(0, donor_sigma, 2)
                assoc_bad = rng.random() < assoc_error_prob and len(donors) > 1
                if assoc_bad:
                    choices = [j for j in range(len(donors)) if j != donor_id]
                    associated_id = int(rng.choice(choices))
                    tx_est = (
                        donors[associated_id]["p0"]
                        + donors[associated_id]["v"] * t
                        + rng.normal(0, donor_sigma, 2)
                    )
                z = h(truth, tx, rx) + rng.normal(0, base_meas_sigma(donor["mode"]))
                outlier = rng.random() < outlier_prob
                if outlier:
                    z += rng.choice([-1, 1]) * rng.uniform(150, 800)
                events.append(
                    {
                        "t": t,
                        "donor_id": donor_id,
                        "mode": donor["mode"],
                        "snr": signal_db,
                        "tx_true": tx,
                        "tx_est": tx_est,
                        "z": z,
                        "assoc_bad": assoc_bad,
                        "outlier": outlier,
                    }
                )
            t += SCAN_PERIOD
    world["events"] = events
    return world


def _event_key(event: dict[str, Any]) -> tuple[Any, ...]:
    """Canonical order equal to generator order but invariant to list shuffling."""

    return (int(event["donor_id"]), float(event["t"]), str(event["mode"]))


def _position_sigma(P: np.ndarray) -> float:
    covariance = _validate_covariance(P, name="final covariance")
    trace = float(np.trace(covariance[:2, :2]))
    tolerance = PSD_ABS_TOL + PSD_REL_TOL * max(1.0, float(np.max(np.abs(covariance))))
    if not math.isfinite(trace) or trace < -tolerance:
        raise CovarianceError(f"final position covariance trace is invalid: {trace}")
    return math.sqrt(max(0.0, trace))


def replay(
    world: dict[str, Any],
    policy: str,
    *,
    model_version: str = DEFAULT_MODEL_VERSION,
) -> dict[str, Any]:
    _validate_policy(policy)
    _validate_model_version(model_version)

    rx = np.asarray(world["rx"], dtype=float)
    x = np.asarray(world["cue"], dtype=float).copy()
    P = np.diag([300**2, 300**2, 1.5**2, 1.5**2])
    donor_sigma = world["donor_sigma"]
    by_second: defaultdict[int, list[dict[str, Any]]] = defaultdict(list)
    # v1.0.0 generated donor-major events. This key preserves that order while
    # removing sensitivity to accidental external list shuffling.
    for event in sorted(world["events"], key=_event_key):
        by_second[int(event["t"])].append(event)

    current_time = 0.0
    used = 0
    rejected = 0
    assoc_bad_used = 0
    outlier_used = 0
    for second in range(world["duration"]):
        bucket_start = float(second)
        bucket_end = bucket_start + 1
        if current_time < bucket_start:
            x, P = predict(
                x, P, bucket_start - current_time, model_version=model_version
            )
            current_time = bucket_start

        candidates: list[dict[str, Any]] = []
        for event in by_second.get(second, []):
            event_x, event_P = predict(
                x, P, event["t"] - bucket_start, model_version=model_version
            )
            sigma = effective_sigma(
                event_x, event["tx_est"], rx, event["mode"], donor_sigma
            )
            candidates.append(
                {
                    **event,
                    "sigma": sigma,
                    "trace": post_trace(event_x, event_P, event["tx_est"], rx, sigma),
                    "xe": event_x,
                    "Pe": event_P,
                }
            )

        chosen: dict[str, Any] | None = None
        if candidates and policy != "NO_PASSIVE":
            if policy == "RANDOM":
                rng = np.random.default_rng(world["seed"] + second * 1009 + 17)
                chosen = candidates[int(rng.integers(len(candidates)))]
            elif policy == "HIGHEST_SNR":
                chosen = max(candidates, key=lambda candidate: candidate["snr"])
            elif policy == "SHORTEST_PULSE":
                chosen = min(candidates, key=lambda candidate: candidate["sigma"])
            elif policy == "METROLOGY_CONDITIONED_EIG":
                chosen = min(candidates, key=lambda candidate: candidate["trace"])

        if chosen is not None:
            pre_event_x = x
            pre_event_P = P
            pre_event_time = current_time
            x, P = chosen["xe"], chosen["Pe"]
            current_time = chosen["t"]
            x, P, accepted, _nis = update(
                x,
                P,
                chosen["z"],
                chosen["tx_est"],
                rx,
                chosen["sigma"],
            )
            if accepted:
                used += 1
                assoc_bad_used += int(chosen["assoc_bad"])
                outlier_used += int(chosen["outlier"])
            else:
                rejected += 1
                if model_version == CANDIDATE_MODEL_VERSION:
                    # Rejected data contain no state information. Restore the
                    # pre-event path so their timestamp cannot affect output.
                    x, P, current_time = pre_event_x, pre_event_P, pre_event_time

        if current_time < bucket_end:
            x, P = predict(
                x, P, bucket_end - current_time, model_version=model_version
            )
            current_time = bucket_end

    truth = truth_at(world, world["duration"])
    return {
        "policy": policy,
        "seed": world["seed"],
        "position_error_final_m": float(np.linalg.norm(x[:2] - truth[:2])),
        "velocity_error_final_mps": float(np.linalg.norm(x[2:] - truth[2:])),
        "position_sigma_final_m": float(_position_sigma(P)),
        "used_measurements": used,
        "rejected_measurements": rejected,
        "assoc_bad_accepted": assoc_bad_used,
        "outlier_accepted": outlier_used,
        "eligible_measurements": len(world["events"]),
    }


def run_world_all(
    seed: int,
    *,
    model_version: str = DEFAULT_MODEL_VERSION,
    **kwargs: Any,
) -> list[dict[str, Any]]:
    _validate_model_version(model_version)
    world = generate_world(seed, **kwargs)
    return [replay(world, policy, model_version=model_version) for policy in POLICIES]


__all__ = [
    "ASYNC_SIGMA_M",
    "CANDIDATE_MODEL_VERSION",
    "CovarianceError",
    "DEFAULT_MODEL_VERSION",
    "GeometryError",
    "LEGACY_MODEL_VERSION",
    "MODELS",
    "MODEL_VERSIONS",
    "MODES",
    "NIS_GATE",
    "POLICIES",
    "SCAN_PERIOD",
    "base_meas_sigma",
    "donor_jacobian",
    "effective_sigma",
    "generate_world",
    "h",
    "H",
    "innovation_stats",
    "post_trace",
    "predict",
    "process_noise",
    "replay",
    "run_world_all",
    "truth_at",
    "update",
]
