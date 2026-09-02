# Integration Contract

## Product surface under test

SCILLA PASSIVE is evaluated as an uncertainty-bearing measurement service
inside an existing maritime fusion workflow. It is not evaluated as a
replacement radar, a blind-search sensor or an autonomous target declaration.

The service receives an external cue and a candidate non-cooperative
illumination opportunity. It returns either one bounded observation or an
explicit rejection reason.

## Minimum input contract

```json
{
  "cue": {
    "track_id": "partner-defined",
    "timestamp_utc": "ISO-8601",
    "state_xy_vx_vy": [0.0, 0.0, 0.0, 0.0],
    "covariance_4x4": [[0.0, 0.0, 0.0, 0.0]]
  },
  "receiver": {
    "position_xy_m": [0.0, 0.0],
    "covariance_2x2": [[0.0, 0.0]],
    "timing_sigma_s": 0.0
  },
  "donor": {
    "emitter_id": "partner-defined",
    "position_xy_m": [0.0, 0.0],
    "covariance_2x2": [[0.0, 0.0]],
    "pulse_mode": "declared-or-unknown",
    "association_confidence": 0.0
  },
  "candidate": {
    "excess_path_m": 0.0,
    "measurement_sigma_m": 0.0,
    "snr_or_detection_metric": 0.0,
    "integrity_flags": []
  }
}
```

Coordinates, reference frames, units, covariance convention and time bases
must be frozen in the interface-control document. Placeholder zeroes above are
schema examples, not operational values.

## Output contract

```json
{
  "observation_id": "stable-id",
  "decision": "ADMIT | REJECT | INSUFFICIENT_EVIDENCE",
  "excess_path_m": 0.0,
  "effective_variance_m2": 0.0,
  "innovation": 0.0,
  "nis": 0.0,
  "reason_codes": [],
  "provenance": {
    "software_commit": "git-sha",
    "model_version": "explicit-version",
    "calibration_id": "partner-defined",
    "input_hash": "sha256"
  }
}
```

The output never claims that a target exists independently of the cue. An
`ADMIT` decision means only that the candidate observation satisfies the frozen
measurement and integrity contract.

## Required reason codes

- `NO_USABLE_DONOR`
- `ASSOCIATION_AMBIGUOUS`
- `GEOMETRY_DEGENERATE`
- `TIMING_UNBOUNDED`
- `REFERENCE_SATURATED`
- `SURVEILLANCE_SNR_INSUFFICIENT`
- `DIRECT_PATH_OR_CLUTTER_DOMINANT`
- `NIS_OUTLIER`
- `CALIBRATION_INVALID`
- `INSUFFICIENT_TRUTH`

Partner-specific codes may be added without removing the common set.

## Integration points

| Existing system | SCILLA PASSIVE role | Required boundary |
|---|---|---|
| Track manager | Supplies cue and covariance | No silent overwrite of track state |
| Radar/reference processor | Supplies donor timing and association evidence | Association confidence retained |
| Signal processor | Produces candidate delay and uncertainty | Calibration and rejection record retained |
| Fusion engine | Accepts or rejects bounded observation | Baseline replay remains available |
| Operator/HMI | Shows evidence state and reason codes | Simulation, replay and measured states visually distinct |
| Evidence store | Preserves inputs, outputs and hashes | Reproducible audit trail |

## Non-functional requirements

- deterministic replay from frozen inputs;
- explicit model and software version on every output;
- no candidate result relabelled as DOI `1.0.0` evidence;
- bounded latency and throughput measured in the partner environment;
- failure-safe rejection when covariance, timing or association is absent;
- no intentional transmission by the SCILLA PASSIVE receiver chain;
- access, retention and export controlled by the partner's data policy.

## Commercial diligence questions

The integration is worth advancing only when a partner can answer:

1. Which existing decision becomes materially better?
2. What observation or operational action does the passive update replace or
   defer?
3. What is the cost of one accepted observation, including calibration and
   rejected candidates?
4. What is the tolerated false-association and missed-opportunity cost?
5. Can the interface be integrated without changing a safety-critical control
   loop?
6. Is the evidence corpus and know-how cheaper to license or acquire than to
   rebuild and revalidate independently?

The sixth question is a transaction hypothesis, not an acquisition claim. It
becomes meaningful only after the preceding technical and economic gates are
answered with partner data.
