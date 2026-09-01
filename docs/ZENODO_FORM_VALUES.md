# Zenodo Record — Published Values

This is the audit card for the already published record. It is not a pending-upload instruction.

| Field | Published value |
|---|---|
| DOI | `10.5281/zenodo.22229086` |
| DOI URL | [https://doi.org/10.5281/zenodo.22229086](https://doi.org/10.5281/zenodo.22229086) |
| Resource type | Software |
| Title | SCILLA PASSIVE: Cue-Driven Opportunistic Maritime Verification Using Non-Cooperative Merchant-Radar Illumination |
| Publication date | 2026-09-01 |
| Creator | Michele Giletto |
| Version | `1.0.0` |
| Language | English |
| Visibility | Public |
| Rights | Custom strict all-rights-reserved notice |

## Published abstract

SCILLA PASSIVE studies a narrow maritime sensing question: when an uncertain track already exists, can mechanically scanning commercial marine radars be treated as moving non-cooperative illuminators that occasionally provide a useful passive second observation? The release models bistatic path-sum measurements, commercial S-band pulse modes, moving donor ephemerides, radar-horizon constraints, donor-position uncertainty, clutter sensitivity, and a classical extended Kalman filter. It deliberately treats generic passive radar and illuminator selection as prior art. In a 300-world nominal paired simulation, passive updates reduce median final track-position error from 351.5 m without passive observations to 19.2 m using a transparent metrology-conditioned selection rule; however, that rule does not robustly outperform a simple shortest-pulse baseline (19.5 m), and the paired median difference is approximately zero. Across 54 physics stress scenarios, the passive architecture beats the no-passive baseline in 94.4% of cells, while beating the best simple donor-selection baseline in only 33.3%. The principal result is therefore architectural rather than algorithmic: opportunistic passive second observations appear useful in many modeled regimes, while a sophisticated donor-selection moat is not demonstrated. No measured RF performance, operational detection range, patentability, or customer value is claimed.

## Published keywords

- passive bistatic radar
- maritime surveillance
- illuminators of opportunity
- commercial marine radar
- multistatic geometry
- sensor tasking
- direct-georeferencing uncertainty
- opportunistic sensing
- maritime domain awareness
- reproducible simulation

## Published custom rights notice

**Title:** `All rights reserved - Michele Giletto (2026)`

**Description:** `Publicly available for scientific review, citation and industrial diligence. No permission is granted to copy, modify, distribute, sublicense, sell or create derivative works except where required by applicable law or hosting-platform terms. See the LICENSE and RIGHTS_AND_DISCLOSURE files in the release.`

## Archive integrity

- **Uploaded archive:** `SCILLA_PASSIVE_PUBLIC_EVIDENCE_RELEASE_v1.0.0_2026-09-01.zip`
- **SHA-256:** `a28ed77b36eea3d41788a4cfd46d1fb3120823afeab57367b1948e8f1df61805`
- **MD5:** `cd7a2311122596269ddda4aea2650a87`

## Non-retroactivity rule

The later source-available license on maintained GitHub `main` does not alter this strict archive. Do not replace the Zenodo file with maintained-branch content. A corrected promoted model must be deposited as a new semantic version under a new version DOI, preserving `1.0.0`.
