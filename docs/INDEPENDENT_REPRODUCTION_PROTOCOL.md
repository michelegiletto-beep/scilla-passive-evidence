# Independent Reproduction Protocol

## Purpose

This protocol separates three objects that must not be conflated:

1. the immutable, published `1.0.0` evidence at [doi:10.5281/zenodo.22229086](https://doi.org/10.5281/zenodo.22229086);
2. the maintained repository's reproduction of `1.0.0` semantics; and
3. the unpromoted `1.1.0-candidate` process model.

Every external report should record the Git commit, model version, command, Python and NumPy versions, seed range, output hashes, and any deviation from this protocol.

The published median-confidence-interval endpoints have a distinct provenance limitation: release `1.0.0` does not record the historical bootstrap program, PRNG family/state, seed, resample count, policy-stream allocation, or quantile convention. The historical procedure is therefore **`NOT_IDENTIFIABLE_FROM_RELEASE_ARTIFACTS`** and must not be reverse-inferred from its ten endpoints.

## Environment

- Python 3.11 or newer;
- an isolated virtual environment;
- dependencies from `requirements.txt` (or the maintained lock file when present);
- sufficient storage for the nominal and stress CSV outputs;
- no edits to tracked evidence files.

```bash
git clone https://github.com/michelegiletto-beep/scilla-passive-evidence.git
cd scilla-passive-evidence
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The GitHub repository may remain private during handoff. Until it is made public, use the DOI archive or an authorized private checkout.

## Track A — reproduce the immutable tag directly

This is the simplest historical reproduction path. The tag contains the original command names and strict rights notice.

```bash
git checkout v1.0.0
make test
make quick
make nominal
```

The tag's `quick` and `nominal` targets use the published `1.0.0` semantics. They do not exercise later candidate corrections.

## Track B — reproduce `1.0.0` from maintained `main`

Return to `main`, then invoke targets whose names make the legacy boundary explicit:

```bash
git checkout main
make test
make frozen-quick
make frozen-nominal
python software/bootstrap_nominal.py
make stress-all
```

Expected target meanings:

| Target | Model | Purpose |
|---|---|---|
| `frozen-quick` | `1.0.0` | Small deterministic legacy check |
| `frozen-nominal` | `1.0.0` | Full 300-world nominal legacy replay |
| `stress-physics` | `1.0.0` | Regenerate 54 physics cells × 30 worlds |
| `stress-integrity` | `1.0.0` | Regenerate 27 integrity cells × 30 worlds |
| `stress-verify` | `1.0.0` | Compare five regenerated stress CSVs with frozen evidence |
| `stress-figures` | `1.0.0` | Regenerate Figures 03–05 for scientific comparison |
| `stress-all` | `1.0.0` | Run all maintained stress-reproduction gates |

The stress verifier is the acceptance authority for the five frozen CSVs:

- `physics_robustness_trials.csv`;
- `physics_robustness_scenario_summary.csv`;
- `integrity_stress_trials.csv`;
- `integrity_stress_scenario_summary.csv`;
- `integrity_gate_statistics.csv`.

Regenerated figures need scientific equivalence, not byte identity, because plotting-library and metadata differences can change PNG bytes without changing plotted data.

## Nominal bootstrap provenance audit

Run:

```bash
python software/bootstrap_nominal.py
```

The maintained audit has a declared, deterministic contract:

| Parameter | Declared value |
|---|---|
| Purpose | Sensitivity check, not recovered historical provenance |
| Algorithm | Nonparametric percentile bootstrap of the sample median |
| Bit generator | NumPy `PCG64` |
| Base seed | `20260901` |
| Resamples | `10,000` per policy |
| Confidence level | 95% |
| Quantile method | `linear` |
| Policy streams | `SeedSequence([base_seed, fixed_policy_index])` |

The script first verifies SHA-256 for the frozen nominal trials and summary, confirms the paired 300-world seed sets, and reproduces all non-bootstrap statistics. It then computes new audit intervals. The declared outcome is **`PASS_WITH_PROVENANCE_LIMITATION`** because the audit is deterministic and the frozen evidence is internally consistent, while the historical bootstrap provenance remains **`NOT_IDENTIFIABLE_FROM_RELEASE_ARTIFACTS`**.

The new endpoints do not all exactly equal the published endpoints. This is not repaired, rounded away, or described as historical reconstruction. Endpoint proximity alone cannot identify an unrecorded bootstrap procedure.

## Track C — candidate falsification

On maintained `main`:

```bash
make quick
make nominal
```

These targets exercise `1.1.0-candidate`. The runner requires an explicit model-version internally and refuses to overwrite an existing output directory unless the caller deliberately opts into replacement.

Candidate outputs must be stored outside frozen `results/`, labeled `1.1.0-candidate`, and reported separately. They are not a correction to the DOI record and are not suitable for citation as a released result.

## Acceptance criteria

A `1.0.0` reproduction passes only if:

- the unit suite passes;
- the requested runner reports model version `1.0.0`;
- the nominal seed set and policy set match the frozen configuration;
- no tracked source, configuration, or evidence file is modified;
- the stress verifier accepts all five frozen CSVs;
- `software/bootstrap_nominal.py` reports `PASS_WITH_PROVENANCE_LIMITATION`;
- the report preserves `NOT_IDENTIFIABLE_FROM_RELEASE_ARTIFACTS` rather than claiming exact historical-bootstrap provenance;
- no-passive remains materially worse than the passive policies in the declared nominal simulation;
- shortest-pulse and metrology-conditioned policies remain close; and
- the negative optimizer conclusion is preserved.

A candidate run is technically valid only if:

- it reports `1.1.0-candidate` explicitly;
- process covariance remains symmetric positive semidefinite;
- propagation is invariant, within numerical tolerance, to an equivalent partition of the same interval;
- a rejected observation produces the same final propagation as if the observation had not been applied; and
- it does not overwrite or relabel frozen evidence.

## Failure and stop conditions

Stop and report rather than rationalize the result if any of the following occurs:

- model version is absent or ambiguous;
- frozen files are modified;
- a seed, schema, row order, or policy differs unexpectedly;
- stress verification fails;
- the audit bootstrap is described as the recovered historical bootstrap;
- published and newly audited interval endpoints are silently interchanged;
- a candidate output is presented as `1.0.0`;
- a passive policy no longer materially improves the nominal propagation-only baseline;
- a claimed optimizer advantage depends on post-hoc policy selection; or
- an RF, range, customer, or operational claim is inferred from simulation.

## Minimal external report

```text
Repository commit:
Git tag (if any):
Model version:
Command:
Python / NumPy:
Seed range:
Tests:
Frozen stress verification:
Bootstrap provenance status:
Declared audit-bootstrap status:
Output SHA-256:
Observed headline metrics:
Deviations:
Conclusion:
```

An independent result should be described as **reproduced simulation evidence**, never as measured SCILLA PASSIVE performance or author endorsement.
