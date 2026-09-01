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
- [x] Maintained local suite passes: 47 tests.
- [x] Five legacy stress CSVs reproduce byte-exactly.
- [x] Clean local clone passes the maintained suite and reproduction gates.
- [x] GitHub Actions CI passes on the private remote (`33561597607`).
- [x] Frozen quick and 300-world nominal replay pass locally.
- [x] Both PDF sources compile locally from repository-relative paths.
- [x] Manifest integrity and credential/local-path scans pass locally.

**Gate C:** `PASS WITH PROVENANCE LIMITATION — LOCAL AND PRIVATE REMOTE QA COMPLETE`

## D. GitHub publication

- [x] Target repository exists: `michelegiletto-beep/scilla-passive-evidence`.
- [x] GitHub account session resolves to `michelegiletto-beep`.
- [x] GitHub App installation exposes `scilla-passive-evidence` to the connector.
- [x] Archive commit, annotated `v1.0.0` tag, and maintained `main` are present remotely.
- [x] Tag target is verified against archive tree `8ef47dd2f3fde8ebaf48919cf8338d62f9f31141`.
- [x] CI passes on GitHub (`33561597607`).
- [ ] Repository homepage points to the DOI.
- [ ] Topics and repository description are set.
- [ ] Public visibility receives a final explicit action check.
- [ ] Public anonymous links resolve.

**Gate D:** `READY FOR FINAL METADATA AND PUBLIC-VISIBILITY GATE`

## E. Candidate promotion

- [x] Candidate is named `1.1.0-candidate`.
- [x] Legacy and candidate semantics are independently selectable.
- [x] Candidate process covariance has a defined partition-invariance test.
- [x] Rejected-event equivalence has a defined test.
- [ ] Candidate 300-world nominal rerun is frozen.
- [ ] Candidate physics and integrity stress reruns are frozen.
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

Zenodo `1.0.0` remains the public scientific record. Maintained QA is `PASS_WITH_PROVENANCE_LIMITATION`: 47 tests pass, legacy stress evidence reproduces byte-exactly, the historical bootstrap procedure remains non-identifiable, and private GitHub lineage plus CI are verified. Advance through the explicit public-visibility and anonymous-access gates only. Do not launch broader promotion, claim recovered bootstrap provenance, claim a corrected release, or promote `1.1.0-candidate` until its own gates pass.
