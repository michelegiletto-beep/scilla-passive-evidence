#!/usr/bin/env python3
import argparse, json, csv, sys, time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
import scilla_passive_core as core

def job(x): seed,kw=x; return core.run_world_all(seed,**kw)
def flat(x): return [r for rr in x for r in rr]
def summarize(rows):
    out={}
    for p in core.POLICIES:
        g=[r for r in rows if r['policy']==p]
        out[p]={
          'n':len(g),
          'median_position_error_m':float(np.median([r['position_error_final_m'] for r in g])),
          'p90_position_error_m':float(np.quantile([r['position_error_final_m'] for r in g],.9)),
          'median_velocity_error_mps':float(np.median([r['velocity_error_final_mps'] for r in g])),
          'median_used_measurements':float(np.median([r['used_measurements'] for r in g]))}
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mode',choices=['quick','nominal'],default='quick')
    ap.add_argument('--out',default='reproduction_output')
    args=ap.parse_args(); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    n=60 if args.mode=='quick' else 300
    jobs=[(260901+k,{}) for k in range(n)]
    t=time.time()
    with ProcessPoolExecutor(max_workers=min(8,(__import__('os').cpu_count() or 2))) as ex:
        rows=flat(list(ex.map(job,jobs,chunksize=5)))
    with (out/'nominal_trials.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    s={'mode':args.mode,'elapsed_s':time.time()-t,'summary':summarize(rows)}
    (out/'summary.json').write_text(json.dumps(s,indent=2))
    print(json.dumps(s,indent=2))
if __name__=='__main__': main()
