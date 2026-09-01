# Independent Reproduction Protocol

## Five-minute path
1. Python 3.11+ recommended.
2. `python -m venv .venv`
3. activate environment.
4. `pip install -r requirements.txt`
5. `make test`
6. `make quick`

`make quick` runs 60 paired worlds per policy using the same frozen model and should reproduce the qualitative ordering. The frozen public evidence tables were generated from the larger 300-world nominal audit and 30-world-per-cell stress grids.

## Full nominal audit
`make nominal`

## Reproduction success
- all unit tests pass;
- no-passive median error remains substantially above passive policies;
- shortest-pulse and metrology-conditioned policies remain close;
- no code/data files are modified during execution.

Exact floating-point hashes are not required across Python/Numpy builds; seeds and formulas are frozen and results should agree within ordinary floating-point/statistical tolerance.
