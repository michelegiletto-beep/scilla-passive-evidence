# Changelog

All notable repository changes are recorded here. The Zenodo `1.0.0` archive and Git tag `v1.0.0` are immutable; entries under **Unreleased** apply only to maintained `main`.

## Unreleased — maintained `main`

### Added

- Explicit legacy/candidate model-version boundary: `1.0.0` and `1.1.0-candidate`.
- Frozen-release reproduction targets distinct from candidate-run targets.
- Full physics and integrity stress-grid regeneration and verification tooling.
- Nominal bootstrap provenance auditor with frozen-input hash guards and deterministic policy-separated streams.
- CI, manifest, portability, and repository QA controls.
- Limited source-available grant for one unmodified local copy and non-commercial scientific execution.

### Changed

- Made report figure paths repository-relative.
- Hardened output handling and metadata so generated evidence cannot silently overwrite frozen results.
- Updated publication metadata to identify the DOI as live rather than reserved.
- Expanded the maintained suite to 47 passing tests; verified all five legacy stress CSVs byte-exactly.

### Scientific disclosure

- Post-publication QA identified partition-dependent process-noise behavior in the legacy `1.0.0` model: candidate-event timing can split propagation intervals, and a rejected observation can therefore change legacy covariance propagation.
- `1.0.0` remains preserved and reproducible. It has not been silently rewritten.
- `1.1.0-candidate` introduces continuous-white-acceleration process-noise discretization and rejection-safe propagation. It remains unpromoted pending complete nominal, stress, editorial, and release gates.
- No optimizer moat is claimed for either model.
- Historical bootstrap provenance is `NOT_IDENTIFIABLE_FROM_RELEASE_ARTIFACTS`: the archive stores interval endpoints but omits the generator, seed/state, resample count, stream allocation, and quantile implementation.
- A new, explicitly non-historical audit uses NumPy PCG64, seed `20260901`, 10,000 policy-separated resamples, percentile median CI at 95%, `linear` quantiles, and `SeedSequence([base_seed, fixed_policy_index])` streams.
- The new audit result is `PASS_WITH_PROVENANCE_LIMITATION`; it verifies frozen hashes/pairing/non-bootstrap statistics but does not claim exact recovery of the published interval procedure.

## 1.0.0 — 2026-09-01 — published

- Published canonical archive at [doi:10.5281/zenodo.22229086](https://doi.org/10.5281/zenodo.22229086).
- Hardened paired-world simulation with 300 nominal worlds per policy.
- Added 54-cell physics robustness grid and 27-cell integrity stress grid.
- Added radar-horizon gating, Joseph covariance update, NIS outlier gate, maneuver, association-error, and outlier stress.
- Preserved the earlier failed policy and explicit failure regimes.
- Rejected a sophisticated donor-selection moat as unsupported by the evidence.
- Added publication and industrial-diligence documentation.
- Distributed under the strict all-rights-reserved notice included in the archive.
