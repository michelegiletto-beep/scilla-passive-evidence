# SCILLA PASSIVE

**Cue-Driven Opportunistic Maritime Verification Using Non-Cooperative Merchant-Radar Illumination**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22229086.svg)](https://doi.org/10.5281/zenodo.22229086)

SCILLA PASSIVE is a reproducible simulation study of a narrow question: can a valid opportunistic bistatic second observation improve an already uncertain maritime track? The public evidence supports an **architecture hypothesis**, not a unique-radar, field-performance, or optimizer-moat claim.

> **Evidence boundary:** all SCILLA PASSIVE performance results in release `1.0.0` are **SIMULATED**. There is no measured RF result, operational detection-range claim, customer validation, patentability opinion, or acquisition claim.

## Release and branch boundary

| Object | Status | Role | Rights |
|---|---|---|---|
| [Zenodo `1.0.0`](https://doi.org/10.5281/zenodo.22229086) | Published and immutable | Canonical public evidence archive | Strict all-rights-reserved notice contained in the archive |
| Git tag `v1.0.0` | Immutable | Git representation of the DOI release | Same strict notice as the archive |
| `main` | Maintained | Portability, QA, reproduction tooling, and explicitly identified candidate corrections | Limited source-available license in the current `LICENSE` |
| `1.1.0-candidate` model | Unpromoted | Corrected process-model candidate for falsification | Not a released scientific result |

The DOI archive is not retroactively relicensed or changed by later commits on `main`. The GitHub repository has passed private content, lineage, and CI verification; public visibility remains a separate publication gate. The Zenodo record is already the live public citation target.

## Audited `1.0.0` result

In 300 paired nominal simulated worlds:

| Policy | Median final position error | Published 95% bootstrap CI* |
|---|---:|---:|
| No passive | 351.5 m | 327.2–396.4 m |
| Highest SNR | 25.8 m | 22.5–28.0 m |
| Random usable donor | 21.8 m | 18.9–23.8 m |
| Shortest pulse | 19.5 m | 17.4–22.2 m |
| Metrology-conditioned EIG | 19.2 m | 16.9–21.8 m |

\*The release stores these interval endpoints but not enough metadata to identify the historical bootstrap generator, seed/state, resample count, policy-stream allocation, or quantile implementation. Their provenance status is therefore **`NOT_IDENTIFIABLE_FROM_RELEASE_ARTIFACTS`**. They remain published `1.0.0` values, but must not be presented as exactly reconstructable from the archive.

### Declared bootstrap audit on `main`

Maintained `main` adds a new sensitivity audit with a fully declared procedure:

- NumPy `PCG64`;
- base seed `20260901`;
- `10,000` nonparametric resamples per policy;
- percentile 95% confidence interval of the sample median;
- NumPy quantile method `linear`;
- policy-separated streams from `SeedSequence([base_seed, fixed_policy_index])`.

The audit verifies the frozen input hashes, paired seeds, and all non-bootstrap summary statistics, then computes new intervals. It does **not** claim to recover the historical bootstrap. The audit result is **`PASS_WITH_PROVENANCE_LIMITATION`**; its endpoints are close to, but do not all exactly match, the published endpoints.

Metrology-conditioned EIG beats shortest-pulse in only **49.7%** of paired worlds, with a paired median difference of approximately **0.0 m**. Across 54 physics stress cells, the passive architecture beats no-passive in **94.4%** of cells, while the metrology-conditioned policy beats the best simple baseline in only **33.3%**.

The defensible conclusion is therefore:

> In the declared simulation, obtaining a valid opportunistic second observation is often useful; a sophisticated donor-selection advantage is not demonstrated.

## Maintained-model disclosure

Post-publication QA identified that the `1.0.0` process-noise discretization can depend on how an interval is partitioned by candidate-event times. A rejected observation can therefore alter legacy covariance propagation solely because it splits a propagation interval. The immutable release is preserved so its published results remain reproducible and auditable.

`main` carries an explicitly named `1.1.0-candidate` correction based on continuous-white-acceleration discretization and rejection-safe propagation. It is **not promoted**, does not replace the DOI evidence, and must not be cited as a validated release until its full nominal, stress, editorial, and archive gates pass.

## Start here

1. [Technical report](docs/SCILLA_PASSIVE_TECHNICAL_REPORT_v1.0.0.pdf)
2. [Executive technical brief](docs/EXECUTIVE_TECHNICAL_BRIEF.md)
3. [Model card](docs/MODEL_CARD.md)
4. [Claim hierarchy](docs/CLAIM_HIERARCHY.md)
5. [Independent reproduction protocol](docs/INDEPENDENT_REPRODUCTION_PROTOCOL.md)
6. [Industrial diligence brief](docs/INDUSTRIAL_DILIGENCE_BRIEF.md)
7. [Publication QA gate](docs/PUBLICATION_QA_GATE.md)

## Reproduction tracks

From the maintained branch:

```bash
python -m venv .venv
python -m pip install -r requirements.txt
make test
make frozen-quick
make frozen-nominal
python software/bootstrap_nominal.py
make stress-all
```

The `frozen-*` and stress-verification paths target the published `1.0.0` semantics. The ordinary `quick` and `nominal` targets exercise `1.1.0-candidate`; their outputs are candidate evidence only. See the independent protocol before comparing results.

Current maintained-branch QA: **47 tests passed**, all five legacy stress CSVs reproduced **byte-exactly**, the private GitHub lineage was verified, and clean-checkout GitHub Actions passed. Public visibility remains pending. The `1.1.0-candidate` model remains unpromoted.

To reproduce directly from the immutable tag, check out `v1.0.0` and use that tag's documented `make test`, `make quick`, and `make nominal` targets.

## Citation

Giletto, M. (2026). *SCILLA PASSIVE: Cue-Driven Opportunistic Maritime Verification Using Non-Cooperative Merchant-Radar Illumination* (Version 1.0.0). Zenodo. [https://doi.org/10.5281/zenodo.22229086](https://doi.org/10.5281/zenodo.22229086)

## Rights

The maintained branch is source-available under the narrow grant in [LICENSE](LICENSE): one unmodified local copy may be executed for non-commercial scientific evaluation, subject to its conditions. Modification, redistribution, derivative works, sublicensing, sale, production use, and other commercial use are not granted.

The Zenodo `1.0.0` archive and Git tag `v1.0.0` retain their original stricter all-rights-reserved notice. See [RIGHTS_AND_DISCLOSURE.md](RIGHTS_AND_DISCLOSURE.md) for the non-retroactivity and disclosure boundary.
