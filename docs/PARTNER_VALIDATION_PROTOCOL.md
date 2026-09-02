# Partner Validation Protocol

## Purpose

This protocol converts SCILLA PASSIVE from a simulation-supported architecture
hypothesis into a bounded external decision. It is designed for a radar OEM,
surveillance integrator, maritime operator, university laboratory or sensor
company that already controls suitable hardware or data.

The partner is not asked to fund a new surveillance programme. The partner is
asked to determine whether one declared second observation exists, repeats and
changes a real tracking decision.

## Validation question

> Can a receive-only, coherently captured merchant-radar opportunity produce a
> geometry-consistent excess-path observation with a defensible uncertainty,
> and does admitting that observation improve an existing track relative to
> the partner's frozen baseline?

## Two admissible tracks

### Track A — coherent capture

Minimum partner-controlled assets:

- coherent dual-receiver chain covering the relevant marine S-band channel;
- reference view of the donor pulse train and surveillance view of the target
  sector;
- known donor identity or independently bounded donor-position uncertainty;
- timestamped receiver position and timing state;
- truth-referenced or independently tracked target;
- site authority and receive-only regulatory clarification.

The first useful observation is not a range demonstration. It is the same known
target in at least **10 independent sweeps**, with measured delay compatible
with

\[
\rho(t)=|X-T|+|X-R|-|T-R|.
\]

### Track B — frozen maritime replay

Minimum partner-controlled data:

- time-aligned existing track state and covariance;
- donor position, pulse-mode or reference-channel metadata sufficient for
  association;
- receiver state and timing uncertainty;
- candidate passive measurements or retained signal data;
- a truth or adjudication source unavailable to the algorithm during replay;
- the partner's current operational baseline and decision metric.

Track B is acceptable when hardware access is unavailable. It must remain a
frozen replay: acceptance metrics and exclusions are agreed before results are
inspected.

## Measurement record

Every candidate observation must carry:

| Field | Requirement |
|---|---|
| `observation_id` | Stable identifier |
| `timestamp_utc` | Absolute or explicitly relative time base |
| `receiver_state` | Position plus declared covariance |
| `donor_state` | Position, identity confidence and covariance |
| `target_cue` | Predicted state and covariance before passive admission |
| `excess_path_m` | Estimated bistatic excess path |
| `variance_m2` | Total admitted measurement variance |
| `association_score` | Declared association evidence or reason for rejection |
| `integrity_flags` | Timing, saturation, cancellation, geometry and outlier flags |
| `decision` | `ADMIT`, `REJECT` or `INSUFFICIENT_EVIDENCE` |

Raw IQ may remain partner-controlled. A reproducible result still requires
frozen derived records, processing version, calibration state and hashes.

## Acceptance ladder

### Gate 0 — calibration

- dual-channel coherence demonstrated;
- cable/reference delay measured;
- saturation and limiter state recorded;
- timing uncertainty bounded;
- receive-only configuration verified.

Failure outcome: `REDESIGN` or `INSUFFICIENT_EVIDENCE`.

### Gate 1 — donor association

- pulse mode or reference signature is stable enough to identify the donor;
- donor-position uncertainty is propagated through the bistatic Jacobian;
- association confidence is recorded for every admitted sweep.

Failure outcome: `KILL` when reliable association is not technically plausible
in the intended environment.

### Gate 2 — repeatable excess path

- at least 10 independent sweeps contain the same known target;
- delay residual is compatible with declared geometry and uncertainty;
- accepted measurements do not depend on post-hoc threshold selection;
- rejected sweeps remain in the evidence package.

Failure outcome: `KILL` when clutter, cancellation, RCS or dynamic range prevents
repeatability.

### Gate 3 — incremental track value

Replay the same cue with:

1. propagation-only baseline;
2. the partner's current alternative observation, when available;
3. SCILLA PASSIVE observation admission;
4. transparent shortest-pulse selection;
5. metrology-conditioned selection only as a secondary comparison.

Pass only when a predeclared decision metric improves and integrity failures do
not increase beyond the agreed tolerance.

### Gate 4 — integration economics

Estimate, using partner data rather than generic market assumptions:

- engineering hours and interfaces required;
- compute, storage and bandwidth per accepted observation;
- calibration and site-support burden;
- avoided active dwell, electro-optical revisit, operator action or uncertainty
  cost, if any;
- cost of false association and rejected observations.

The programme stops when integration cost exceeds plausible operational value.

## Final decision

| Outcome | Meaning |
|---|---|
| `PASS` | Repeatable observation and incremental decision value justify a larger pilot |
| `REDESIGN` | A bounded technical correction has a credible retest path |
| `KILL` | A declared physical, association or economic falsifier is reached |
| `INSUFFICIENT_EVIDENCE` | Data quality or truth is inadequate; no positive claim is permitted |

## Data, rights and publication

- Partner raw data may remain confidential or on-premises.
- Public release requires explicit partner permission.
- A private diligence report may disclose only agreed derived metrics.
- Background IP, code rights and any evaluation licence must be agreed in
  writing before non-public integration work.
- No partner name, endorsement or result is implied by use of this protocol.
