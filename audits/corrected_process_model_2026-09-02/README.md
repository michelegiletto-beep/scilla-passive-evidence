# Corrected Process-Model Audit — 2026-09-02

This directory freezes a complete **simulation-only** audit of
`1.1.0-candidate`, the corrected continuous-white-noise-acceleration process
model carried on maintained `main`.

The audit was created because the immutable DOI release `1.0.0` uses a
partition-dependent process-noise formulation. The historical model remains
available for exact reproduction; it has not been silently rewritten.

## Headline result

The corrected model preserves the qualitative architecture conclusion on the
same nominal seeds and stress grids:

| Gate | Corrected candidate | Change in architecture gate vs `1.0.0` |
|---|---:|---:|
| Nominal no-passive median | 351.50 m | 0.00 m |
| Nominal metrology-EIG median | 19.21 m | +0.04 m |
| Nominal shortest-pulse median | 19.46 m | -0.07 m |
| Physics cells: architecture beats no-passive | 51 / 54 | 0 cells |
| Integrity cells: architecture beats no-passive | 27 / 27 | 0 cells |

The donor-optimizer moat remains unsupported:

- EIG beats shortest-pulse in 147 of 300 paired nominal worlds (49.0%);
- paired median difference is 0.0 m;
- the declared audit-bootstrap interval for the paired median spans zero;
- EIG beats the best simple baseline in 19 of 54 physics cells and 10 of 27
  integrity cells.

## Status

`PASS_CANDIDATE_NOT_PROMOTED`

This status means the process correction did not overturn the architecture
conclusion on the declared simulated fixtures. It does **not** mean that the
candidate is a released model, that RF feasibility has been measured, or that
operational or customer value has been demonstrated.

## Contents

- `CORRECTED_MODEL_AUDIT.json` — machine-readable conclusion, intervals,
  comparisons and input hashes;
- `nominal/` — 300 paired worlds per policy and runner summary;
- `stress/` — full 54-cell physics and 27-cell integrity outputs, 30 worlds per
  cell;
- `SHA256SUMS.txt` — hashes for every frozen file in this directory.

## Reproduce

From maintained `main`:

```bash
python software/run_release.py \
  --mode nominal \
  --model-version 1.1.0-candidate \
  --out candidate_nominal \
  --force

python software/run_stress.py \
  --suite all \
  --model-version 1.1.0-candidate \
  --out candidate_stress

python software/audit_candidate.py \
  --nominal-dir candidate_nominal \
  --stress-dir candidate_stress \
  --legacy-dir results \
  --out candidate_audit/CORRECTED_MODEL_AUDIT.json
```

The canonical published release remains
[`10.5281/zenodo.22229086`](https://doi.org/10.5281/zenodo.22229086).
