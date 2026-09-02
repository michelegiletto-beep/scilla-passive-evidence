# Release Index — SCILLA PASSIVE

## Canonical public release

- **Version:** `1.0.0`
- **DOI:** [10.5281/zenodo.22229086](https://doi.org/10.5281/zenodo.22229086)
- **Status:** published, public, immutable
- **Git boundary:** tag `v1.0.0`
- **Archive SHA-256:** `a28ed77b36eea3d41788a4cfd46d1fb3120823afeab57367b1948e8f1df61805`
- **Rights:** strict all-rights-reserved notice contained in the archive

The DOI archive is the citation authority for release `1.0.0`. Maintained-branch changes are not part of that archive unless published later as a separately versioned release.

## Maintained repository

- **Repository:** [michelegiletto-beep/scilla-passive-evidence](https://github.com/michelegiletto-beep/scilla-passive-evidence)
- **Branch:** `main`
- **Current handoff:** public repository live; lineage, DOI metadata, anonymous HTTPS access, and GitHub Actions verified
- **Rights:** limited source-available license in the current `LICENSE`
- **Candidate model:** `1.1.0-candidate`, unpromoted
- **Local test status:** 47 tests passed
- **Legacy stress status:** five frozen CSVs reproduced byte-exactly
- **Bootstrap provenance:** `NOT_IDENTIFIABLE_FROM_RELEASE_ARTIFACTS`
- **Declared audit:** `PASS_WITH_PROVENANCE_LIMITATION`
- **Public GitHub CI:** PASS on current `main`

## Entry points

| Path | Purpose |
|---|---|
| `README.md` | Evidence, release, model-version, and rights boundary |
| `docs/SCILLA_PASSIVE_TECHNICAL_REPORT_v1.0.0.pdf` | Canonical publication-grade report |
| `docs/SCILLA_PASSIVE_INDUSTRIAL_BRIEF_v1.0.0.pdf` | One-page evidence brief |
| `docs/EXECUTIVE_TECHNICAL_BRIEF.md` | Executive evidence summary |
| `docs/MODEL_CARD.md` | Assumptions, omissions, and falsifiers |
| `docs/CLAIM_HIERARCHY.md` | Permitted and prohibited claims |
| `docs/INDEPENDENT_REPRODUCTION_PROTOCOL.md` | Frozen and candidate reproduction paths |
| `docs/INDUSTRIAL_DILIGENCE_BRIEF.md` | Technical diligence map and external gates |
| `docs/PUBLICATION_QA_GATE.md` | Publication and repository gate status |
| `software/scilla_passive_core.py` | Simulation core |
| `software/run_release.py` | Version-explicit nominal runner |
| `software/bootstrap_nominal.py` | Declared bootstrap sensitivity/provenance audit |
| `tests/test_bootstrap_reproduction.py` | Bootstrap audit and provenance guards |
| `results/AUDIT_SUMMARY.json` | Frozen `1.0.0` audit summary |
| `results/nominal_policy_summary.csv` | 300-world nominal benchmark and intervals |
| `results/physics_robustness_scenario_summary.csv` | 54 physics stress cells |
| `results/integrity_stress_scenario_summary.csv` | 27 integrity stress cells |
| `results/PRESERVED_FAILURE_v0.json` | Preserved failed model |
| `data/EVIDENCE_LEDGER.csv` | Evidence classification |
| `data/CLAIM_HIERARCHY.csv` | Machine-readable claim boundary |
| `data/TECHNICAL_SOURCE_LEDGER.csv` | Technical source ledger |
| `CITATION.cff` | Citation metadata |
| `LICENSE` | Maintained-branch source-available terms |
| `RIGHTS_AND_DISCLOSURE.md` | Archive/branch non-retroactivity and disclosure notice |

## Version rule

Results generated with `1.0.0` semantics may be compared with the DOI evidence. Results generated with `1.1.0-candidate` must be labeled candidate evidence and cannot be substituted into the `1.0.0` record. A future promoted version requires a new QA gate, changelog entry, immutable tag, and version DOI.

The published confidence-interval endpoints remain part of `1.0.0`, but their historical bootstrap procedure is not identifiable from the release artifacts. The maintained PCG64/seed-`20260901`/10,000-resample audit is a newly declared sensitivity check, not a recovered provenance claim.
