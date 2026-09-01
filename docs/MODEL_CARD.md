# Model Card and Failure Boundary

## Intended use
Research evaluation of cue-driven opportunistic passive second-observation architectures.

## Non-intended use
Operational navigation, collision avoidance, weapons targeting, certified surveillance, or any claim of field detection range.

## Estimator
Conventional four-state constant-velocity EKF with Joseph-form covariance update and a 1-DoF normalized-innovation-squared gate of 6.63. The estimator is a baseline, not a novelty claim.

## Key model assumptions
- flat 2-D local Cartesian state;
- 4/3-effective-Earth horizon gate;
- donor ships follow constant velocity;
- target can be stressed with a discrete heading change;
- radar pulse mode drawn from a public commercial S-band family;
- RCS is a sensitivity parameter, not a truth model;
- residual clutter is represented as a scalar link-budget penalty plus optional delay outliers;
- donor association error is explicitly injected in integrity stress tests;
- maximum one processed passive candidate per one-second decision bucket.

## Hard limits
The simulator does not model detailed sea-spectrum statistics, multipath channel impulse responses, antenna sidelobe structure, pulse-to-pulse magnetron phase noise, receiver ADC saturation, direct-path cancellation residuals, polarization mismatch, ship-aspect RCS dynamics, dense-emitter deinterleaving or regulatory constraints.

## Preserved failures
The initial policy version produced a nominal median error of 36.5 m and beat the best simple baseline in only 13.9% of its original robustness cells. It is retained in `results/PRESERVED_FAILURE_v0.json`.

The audited physics grid also preserves 3 cells where the passive architecture provides no median benefit over propagation-only.

## Primary falsifiers for external work
1. Measured residual clutter/direct-path interference removes the simulated SNR margin.
2. Emitter association error is not rejectable with practical metadata/reference processing.
3. Real bistatic RCS is too weak/variable in the target classes of interest.
4. Real passive measurements do not improve a cue-only/classical replay.
5. Integration cost exceeds the active/EO observation cost it is supposed to save.
