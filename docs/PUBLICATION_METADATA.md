# Publication Metadata - Final Release 1.0.0

**Title**  
SCILLA PASSIVE: Cue-Driven Opportunistic Maritime Verification Using Non-Cooperative Merchant-Radar Illumination

**Version**  
1.0.0 - 1 September 2026

**Suggested resource type**  
Software (mixed research release: source code + technical report + frozen simulation data)

**Abstract**  
SCILLA PASSIVE studies a narrow maritime sensing question: when an uncertain track already exists, can mechanically scanning commercial marine radars be treated as moving non-cooperative illuminators that occasionally provide a useful passive second observation? The release models bistatic path-sum measurements, commercial S-band pulse modes, moving donor ephemerides, radar-horizon constraints, donor-position uncertainty, clutter sensitivity and a classical extended Kalman filter. It deliberately treats generic passive radar and illuminator selection as prior art. In a 300-world nominal paired simulation, passive updates reduce median final track-position error from 351.5 m without passive observations to 19.2 m using a transparent metrology-conditioned selection rule; however, that rule does not robustly outperform a simple shortest-pulse baseline (19.5 m), and the paired median difference is approximately zero. Across 54 physics stress scenarios, the passive architecture beats the no-passive baseline in 94.4% of cells, while beating the best simple donor-selection baseline in only 33.3%. The principal result is therefore architectural rather than algorithmic: opportunistic passive second observations appear useful in many modeled regimes, while a sophisticated donor-selection moat is not demonstrated. No measured RF performance, operational detection range, patentability or customer value is claimed.

**Keywords**  
passive bistatic radar; maritime surveillance; illuminators of opportunity; commercial marine radar; multistatic geometry; sensor tasking; direct georeferencing uncertainty; opportunistic sensing; maritime domain awareness; reproducible simulation

**DOI**  
10.5281/zenodo.22229086
