# Corrected Process-Model Audit

## Decision

The corrected `1.1.0-candidate` process model preserves the principal SCILLA
PASSIVE simulation result: admitting a valid opportunistic second observation
can materially reduce the uncertainty of an already-cued maritime track in the
declared fixtures. The correction does not create an optimizer moat and does
not substitute for RF measurement.

Audit status:

> **PASS_CANDIDATE_NOT_PROMOTED**

## Why the audit was necessary

The immutable DOI release `1.0.0` injects process covariance once per
propagation call. Artificially splitting an interval can therefore change the
legacy covariance, and a NIS-rejected candidate can affect the result solely by
partitioning time. Maintained `main` discloses that defect and supplies a
continuous-white-noise-acceleration candidate whose covariance satisfies the
semigroup relation and whose rejected events are propagation-neutral.

The only defensible response was to rerun the complete evidence ladder rather
than assume the published headline would survive.

## Complete rerun

The candidate audit contains:

- 300 paired nominal worlds for every policy;
- all 54 physics-stress cells with 30 worlds per cell;
- all 27 integrity-stress cells with 30 worlds per cell;
- a declared 10,000-resample percentile bootstrap using NumPy PCG64, base seed
  `20260902`, policy-separated `SeedSequence` streams and `linear` quantiles;
- hashes for the full nominal and stress trial tables.

## Result

| Policy | `1.0.0` median | Corrected candidate median | Candidate audit 95% interval |
|---|---:|---:|---:|
| No passive | 351.50 m | 351.50 m | 326.34–396.29 m |
| Highest SNR | 25.77 m | 24.94 m | 22.43–28.14 m |
| Random usable donor | 21.79 m | 21.96 m | 19.40–23.90 m |
| Shortest pulse | 19.53 m | 19.46 m | 17.48–22.34 m |
| Metrology-conditioned EIG | 19.17 m | 19.21 m | 16.81–21.55 m |

The architecture gate is unchanged in every stress cell:

| Stress family | Architecture beats no-passive | Gate changes vs `1.0.0` |
|---|---:|---:|
| Physics | 51 / 54 (94.4%) | 0 / 54 |
| Integrity | 27 / 27 (100%) | 0 / 27 |

The optimizer conclusion also remains negative:

- EIG beats shortest-pulse in 147 of 300 paired worlds (49.0%);
- 19 worlds are exact ties;
- paired median difference is 0.0 m;
- the audit-bootstrap interval of the paired median is -0.59 to +0.02 m;
- EIG beats the best simple baseline in 19 of 54 physics cells (35.2%) and 10
  of 27 integrity cells (37.0%).

## What this changes

The process-model defect no longer sits underneath an untested assumption. The
corrected candidate independently reproduces the same qualitative separation:

1. the observation architecture carries the simulated signal;
2. sophisticated donor selection does not carry a robust advantage.

This strengthens the rationale for a small external validation gate. It does
not validate range, clutter cancellation, target return, association,
receiver dynamic range, integration economics or customer value.

## Release boundary

- DOI `1.0.0` remains immutable historical evidence.
- The corrected outputs are a maintained-branch audit object.
- `1.1.0-candidate` remains unpromoted pending independent review, versioned
  report/model-card updates and an explicit future archive decision.
- Candidate and DOI numbers must never be mixed without their model labels.

Machine-readable evidence and all trial tables are under
`audits/corrected_process_model_2026-09-02/`.
