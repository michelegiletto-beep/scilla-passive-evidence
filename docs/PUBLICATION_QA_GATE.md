# Publication QA Gate — SCILLA PASSIVE

## A. Canonical Zenodo `1.0.0`

- [x] DOI is live: [10.5281/zenodo.22229086](https://doi.org/10.5281/zenodo.22229086).
- [x] Resource type is Software.
- [x] Version is `1.0.0` and publication date is 2026-09-01.
- [x] Creator is Michele Giletto.
- [x] Visibility is Public.
- [x] Archive contains the strict custom all-rights-reserved notice.
- [x] Technical report and industrial brief are included.
- [x] No measured RF, operational range, customer, patentability, or acquisition claim is made.

**Gate A:** `PASS — PUBLISHED AND IMMUTABLE`

## B. Scientific evidence boundary

- [x] Same simulated worlds are replayed across policies.
- [x] 300 nominal worlds per policy are frozen.
- [x] Nominal median intervals are reported as published values.
- [x] Historical bootstrap provenance is explicitly `NOT_IDENTIFIABLE_FROM_RELEASE_ARTIFACTS`.
- [x] New declared audit uses PCG64, seed `20260901`, 10,000 resamples, percentile median CI 95%, `linear` quantiles, and policy-separated `SeedSequence` streams.
- [x] Declared bootstrap audit returns `PASS_WITH_PROVENANCE_LIMITATION` without claiming historical reconstruction.
- [x] 54 physics cells × 30 worlds are frozen.
- [x] 27 integrity cells × 30 worlds are frozen.
- [x] Failed policy and failure cells are preserved.
- [x] Optimizer moat is explicitly rejected.
- [x] Post-publication process-noise partition defect is disclosed.
- [x] `1.0.0` remains reproducible and is not silently rewritten.
- [x] `1.1.0-candidate` is labeled unpromoted.

**Gate B:** `PASS WITH DISCLOSED LEGACY LIMITATION`

## C. Maintained repository content

- [x] Zenodo tree is preserved as the first Git commit.
- [x] Annotated tag `v1.0.0` identifies the immutable archive boundary.
- [x] Report figure paths are repository-relative.
- [x] Maintained license and archive rights are clearly separated.
- [x] Frozen and candidate runner paths are explicitly separated.
- [x] Full stress regeneration/verification path is documented.
- [x] Maintained local suite passes: 48 tests.
- [x] Five legacy stress CSVs reproduce byte-exactly.
- [x] Clean local clone passes the maintained suite and reproduction gates.
- [x] GitHub Actions CI passes on current public `main`.
- [x] Frozen quick and 300-world nominal replay pass locally.
- [x] Both PDF sources compile locally from repository-relative paths.
- [x] Manifest integrity and credential/local-path scans pass locally.

**Gate C:** `PASS WITH PROVENANCE LIMITATION — LOCAL AND PUBLIC REMOTE QA COMPLETE`

## D. GitHub publication

- [x] Target repository exists: `michelegiletto-beep/scilla-passive-evidence`.
- [x] GitHub account session resolves to `michelegiletto-beep`.
- [x] GitHub App installation exposes `scilla-passive-evidence` to the connector.
- [x] Archive commit, annotated `v1.0.0` tag, and maintained `main` are present remotely.
- [x] Tag target is verified against archive tree `8ef47dd2f3fde8ebaf48919cf8338d62f9f31141`.
- [x] CI passes on current GitHub `main`.
- [x] Repository homepage points to the DOI.
- [x] Topics and repository description are set.
- [x] Public visibility received a final explicit action check.
- [x] Anonymous HTTPS access resolves `main`, `v1.0.0`, the README, and its DOI link.

**Gate D:** `PASS — PUBLIC, METADATA COMPLETE, ANONYMOUS ACCESS VERIFIED`

## E. Candidate promotion

- [x] Candidate is named `1.1.0-candidate`.
- [x] Legacy and candidate semantics are independently selectable.
- [x] Candidate process covariance has a defined partition-invariance test.
- [x] Rejected-event equivalence has a defined test.
- [x] Candidate 300-world nominal rerun is frozen.
- [x] Candidate physics and integrity stress reruns are frozen.
- [x] Corrected-model audit reports `PASS_CANDIDATE_NOT_PROMOTED`.
- [x] Architecture gate is unchanged in all 54 physics and 27 integrity cells.
- [ ] Paired impact and intervals are independently reviewed.
- [ ] Technical report/model card are versioned for the candidate result.
- [ ] New release archive and version DOI are prepared.

**Gate E:** `HOLD — CANDIDATE UNPROMOTED`

## F. External evidence

- [ ] Independent third-party reproduction.
- [ ] Customer-data replay.
- [ ] Partner-sponsored calibrated RF bench.
- [ ] Truth-referenced repeated field observations.

**Gate F:** `NOT STARTED`

## Director decision

Zenodo `1.0.0` remains the public scientific record. Maintained QA is `PASS_WITH_PROVENANCE_LIMITATION`: 48 tests pass, legacy stress evidence reproduces byte-exactly, the historical bootstrap procedure remains non-identifiable, and the corrected candidate preserves the qualitative architecture conclusion across the complete frozen nominal and stress design. The next downstream gate is independent review and partner-sponsored replay or measurement; do not claim recovered bootstrap provenance, a corrected released version, or measured RF performance.
