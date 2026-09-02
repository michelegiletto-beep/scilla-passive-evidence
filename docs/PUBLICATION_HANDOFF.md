# Publication Handoff

## Completed canonical publication

Zenodo release `1.0.0` is live and citable:

- **DOI:** [10.5281/zenodo.22229086](https://doi.org/10.5281/zenodo.22229086)
- **Resource type:** Software
- **Version:** `1.0.0`
- **Publication date:** 2026-09-01
- **Creator:** Michele Giletto
- **Visibility:** Public
- **Archive rights:** strict custom all-rights-reserved notice
- **Archive SHA-256:** `a28ed77b36eea3d41788a4cfd46d1fb3120823afeab57367b1948e8f1df61805`

The DOI is registered, not merely reserved. Do not edit documentation to describe it as pending.

## Git handoff design

Repository: [michelegiletto-beep/scilla-passive-evidence](https://github.com/michelegiletto-beep/scilla-passive-evidence)

The required history is:

1. first Git commit contains the exact `1.0.0` Zenodo release tree;
2. annotated tag `v1.0.0` points to that commit and remains immutable;
3. subsequent `main` commit contains portability, QA, reproduction, disclosure, and license maintenance;
4. no force-push or retagging changes the `v1.0.0` boundary;
5. repository remained private until content, tag, CI, and rights were verified;
6. visibility changed only after Michele's explicit final publication instruction.

The repository is now public. The archive tree, annotated tag, maintained history, clean-checkout GitHub Actions run, DOI homepage, topics, and anonymous HTTPS access have been verified. Anonymous checks included remote discovery of `main` and `v1.0.0` plus a clean clone containing the public README and DOI link.

## Rights split

The Zenodo archive and `v1.0.0` tag retain the original strict all-rights-reserved notice. The maintained `main` branch uses a narrow source-available license allowing one unmodified local copy and non-commercial scientific execution. This later license is not retroactive.

Do not replace the Zenodo file or metadata with the maintained branch. A scientifically promoted correction requires a new version and a new version DOI under the existing Zenodo concept record.

## Candidate boundary

`1.1.0-candidate` corrects the process-noise/rejected-event semantics identified after publication. It remains unpromoted. Candidate output must:

- be version-labeled;
- remain outside frozen evidence paths;
- pass nominal, stress, invariance, editorial, and archive QA;
- never be presented as a silent correction to `1.0.0`.

## Repository settings

- default branch: `main`;
- Issues: enabled;
- Wiki, Projects, Discussions: disabled unless a need is demonstrated;
- homepage: `https://doi.org/10.5281/zenodo.22229086`;
- do not enable automatic Zenodo archiving for `v1.0.0`, which would create a duplicate archive workflow;
- preserve branch/tag history;
- require CI to pass before any future release tag.

Suggested topics:

`passive-radar`, `bistatic-radar`, `marine-radar`, `maritime-surveillance`, `maritime-domain-awareness`, `sensor-fusion`, `extended-kalman-filter`, `reproducible-research`, `research-software`, `simulation`

## Completed GitHub publication sequence

1. Preserved the verified archive commit and immutable `v1.0.0` tag.
2. Preserved maintained `main` and its passing GitHub Actions contract.
3. Received an explicit publication instruction and made the repository public.
4. Confirmed anonymous HTTPS access to `main`, `v1.0.0`, the README, and its DOI link.
5. Added the DOI homepage and approved research topics in repository metadata.
6. Systems Lab, LinkedIn, and targeted industrial distribution remain separate downstream gates.

## Stop conditions

Stop publication if the DOI tag differs from the archive, CI does not reproduce the frozen contract, candidate results appear in the `1.0.0` evidence paths, rights notices conflict, credentials or local absolute paths are present, or any measured/operational claim is implied.
