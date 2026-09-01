# SCILLA PASSIVE - Public Evidence Release 1.0.0

**Cue-Driven Opportunistic Maritime Verification Using Non-Cooperative Merchant-Radar Illumination**

**DOI:** `10.5281/zenodo.22229086`

> Status: FINAL PUBLICATION PACKAGE. Reserved DOI: 10.5281/zenodo.22229086. No measured RF performance is claimed.

## Central result
The audited simulator supports an **architecture** claim, not an optimizer claim.

In 300 paired nominal simulated worlds:

| Policy | Median final position error | 95% bootstrap CI |
|---|---:|---:|
| No passive | 351.5 m | 327.2-396.4 m |
| Highest SNR | 25.8 m | 22.5-28.0 m |
| Random usable donor | 21.8 m | 18.9-23.8 m |
| Shortest pulse | 19.5 m | 17.4-22.2 m |
| Metrology-conditioned EIG | 19.2 m | 16.9-21.8 m |

Metrology-conditioned EIG beats shortest-pulse in only **49.7%** of paired worlds and has a paired median difference of **0.0 m**. Therefore **a donor-selection algorithmic moat is not demonstrated**.

Across 54 physics stress cells, the passive architecture beats no-passive in **94.4%**, with three failure cells preserved.

## Start here
1. `docs/EXECUTIVE_TECHNICAL_BRIEF.md`
2. `docs/SCILLA_PASSIVE_TECHNICAL_REPORT_v1.0.0.pdf`
3. `docs/MODEL_CARD.md`
4. `docs/CLAIM_HIERARCHY.md`
5. `docs/INDEPENDENT_REPRODUCTION_PROTOCOL.md`
6. `docs/PUBLICATION_QA_GATE.md`

## Reproduce
```bash
pip install -r requirements.txt
make test
make quick
```

## Evidence status
MEASURED SCILLA PASSIVE RF evidence: **none**.

The next external gate is independent reproduction, customer replay, or partner-sponsored RF validation.
