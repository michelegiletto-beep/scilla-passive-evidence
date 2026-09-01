# Process-model versioning and scientific boundary

## Immutable published model — `1.0.0`

DOI [`10.5281/zenodo.22229086`](https://doi.org/10.5281/zenodo.22229086) and Git tag
`v1.0.0` describe an immutable historical simulation. Its process covariance is

\[
Q_{1.0.0}(\Delta t)=G(\Delta t)q^2I G(\Delta t)^T,
\qquad
G=\begin{bmatrix}
\Delta t^2/2&0\\0&\Delta t^2/2\\\Delta t&0\\0&\Delta t
\end{bmatrix}.
\]

This formulation is retained in software solely for exact numerical
reproduction. Because it injects one independent acceleration draw per call,
splitting one interval into sub-intervals changes the accumulated covariance.
The historical replay also keeps the event-time split after a NIS-rejected
measurement. Consequently, a rejected observation can change covariance only
because its timestamp partitions propagation. That is a model defect, not
physical evidence.

## Corrected, unpromoted candidate — `1.1.0-candidate`

The candidate uses the continuous-white-noise-acceleration covariance

\[
Q_c(\Delta t)=q^2\begin{bmatrix}
\Delta t^3/3&0&\Delta t^2/2&0\\
0&\Delta t^3/3&0&\Delta t^2/2\\
\Delta t^2/2&0&\Delta t&0\\
0&\Delta t^2/2&0&\Delta t
\end{bmatrix}.
\]

It satisfies the covariance semigroup relation (up to floating-point error).
If the NIS gate rejects an event, replay explicitly restores the pre-event
trajectory before continuing, making rejection propagation-neutral.

`1.1.0-candidate` is a corrected simulation model, **not** a correction silently
inserted into the DOI record, not measured RF evidence, and not yet a promoted
release. Candidate outputs must use a separate output directory and must carry
their model identifier.

## Reproduction rule

The runner requires an explicit choice:

```bash
# Reproduce the historical DOI model
python software/run_release.py --mode quick --model-version 1.0.0 --out reproduction_legacy

# Evaluate the corrected candidate
python software/run_release.py --mode quick --model-version 1.1.0-candidate --out reproduction_candidate
```

Existing output files are refused unless `--force` is supplied; replacement is
atomic and limited to `nominal_trials.csv` and `summary.json`.

Never mix candidate rows, figures, medians, or stress flags with claims labelled
as v1.0.0/DOI evidence. A future promoted release requires a complete nominal and
stress rerun, independent QA, updated figures and report language, and an
explicit versioned archive.
