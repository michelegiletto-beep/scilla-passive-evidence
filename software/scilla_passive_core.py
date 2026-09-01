import math, json, csv
from dataclasses import dataclass
from collections import defaultdict
from pathlib import Path
import numpy as np

C=299_792_458.0; FC=3e9; K=1.380649e-23; T0=290.0
PT_W=30_000.0; GT_DBI=28.0; GR_DBI=15.0; BEAM_DEG=1.8; RPM=24.0; SCAN_PERIOD=60/RPM
NF_DB=4.0; LOSS_DB=10.0; PROC_LOSS_DB=3.0; THRESH_DB=13.0; ASYNC_SIGMA_M=20.0
TX_H_M=25.0; RX_H_M=30.0; TARGET_H_M=10.0; K_EARTH=4/3
MODES={'S1':(0.07,3000),'S2':(0.15,3000),'M1':(0.30,1500),'M2':(0.50,1200),'M3':(0.70,1000),'L':(1.20,600)}
MODE_NAMES=list(MODES)
POLICIES=['NO_PASSIVE','RANDOM','HIGHEST_SNR','SHORTEST_PULSE','METROLOGY_CONDITIONED_EIG']
NIS_GATE=6.63

def radar_horizon_km(h1,h2):
    Re=6_371_000*K_EARTH
    return (math.sqrt(2*Re*h1)+math.sqrt(2*Re*h2))/1000
H_TX_TGT=radar_horizon_km(TX_H_M,TARGET_H_M); H_RX_TGT=radar_horizon_km(RX_H_M,TARGET_H_M); H_TX_RX=radar_horizon_km(TX_H_M,RX_H_M)

def dwell_s(): return BEAM_DEG/(RPM*6)
def rx_power_w(Rt,Rr,sigma_b):
    lam=C/FC; Gt=10**(GT_DBI/10); Gr=10**(GR_DBI/10); L=10**(LOSS_DB/10)
    return PT_W*Gt*Gr*lam**2*sigma_b/((4*math.pi)**3*Rt**2*Rr**2*L)
def snr_db(Rt,Rr,mode,sigma_b,clutter_db):
    pulse_us,prf=MODES[mode]; F=10**(NF_DB/10); Np=prf*dwell_s()
    s=rx_power_w(Rt,Rr,sigma_b)*(pulse_us*1e-6)*Np/(K*T0*F)
    return 10*math.log10(max(s,1e-30))-PROC_LOSS_DB-clutter_db
def base_meas_sigma(mode):
    pulse_us,_=MODES[mode]; cell=C*pulse_us*1e-6/math.sqrt(12)
    return math.sqrt(cell*cell+ASYNC_SIGMA_M**2)
def donor_jacobian(state,tx,rx):
    p=state[:2]; a=tx-p; b=tx-rx
    return a/max(np.linalg.norm(a),1e-9)-b/max(np.linalg.norm(b),1e-9)
def effective_sigma(state,tx,rx,mode,donor_sigma):
    jt=donor_jacobian(state,tx,rx); base=base_meas_sigma(mode)
    return math.sqrt(base*base+donor_sigma*donor_sigma*float(jt@jt))
def h(x,tx,rx):
    p=x[:2]; return np.linalg.norm(p-tx)+np.linalg.norm(p-rx)-np.linalg.norm(tx-rx)
def H(x,tx,rx):
    p=x[:2]; a=p-tx; b=p-rx
    z=np.zeros((1,4)); z[0,:2]=a/max(np.linalg.norm(a),1e-9)+b/max(np.linalg.norm(b),1e-9); return z
def predict(x,P,dt,q=0.12):
    F=np.array([[1,0,dt,0],[0,1,0,dt],[0,0,1,0],[0,0,0,1.]],float)
    G=np.array([[0.5*dt*dt,0],[0,0.5*dt*dt],[dt,0],[0,dt]],float)
    Q=G@(q*q*np.eye(2))@G.T
    return F@x,F@P@F.T+Q
def innovation_stats(x,P,z,tx,rx,sigma):
    HH=H(x,tx,rx); y=float(z-h(x,tx,rx)); S=(HH@P@HH.T).item()+sigma*sigma
    return y,S,HH
def update(x,P,z,tx,rx,sigma):
    y,S,HH=innovation_stats(x,P,z,tx,rx,sigma)
    nis=y*y/S
    if nis>NIS_GATE:
        return x,P,False,nis
    Kg=(P@HH.T)/S; xn=x+Kg[:,0]*y
    I=np.eye(4); A=I-Kg@HH
    Pn=A@P@A.T + (Kg@Kg.T)*(sigma*sigma)
    Pn=0.5*(Pn+Pn.T)
    return xn,Pn,True,nis
def post_trace(x,P,tx,rx,sigma):
    HH=H(x,tx,rx); S=(HH@P@HH.T).item()+sigma*sigma; Kg=(P@HH.T)/S
    Pn=(np.eye(4)-Kg@HH)@P
    return float(np.trace(Pn[:2,:2]))

def truth_at(world,t):
    p0=world['truth_p0']; v0=world['truth_v0']; tm=world['maneuver_time_s']; theta=world['maneuver_deg']*math.pi/180
    if theta==0 or t<=tm:
        return np.r_[p0+v0*t,v0]
    p_m=p0+v0*tm
    c,s=math.cos(theta),math.sin(theta); R=np.array([[c,-s],[s,c]])
    v1=R@v0
    return np.r_[p_m+v1*(t-tm),v1]

def generate_world(seed,duration=60,n_donors=12,rcs=100,clutter_db=10,donor_sigma=30,active_prob=0.75,maneuver_deg=0,assoc_error_prob=0,outlier_prob=0):
    rng=np.random.default_rng(seed); rx=np.array([0.,0.])
    r0=rng.uniform(8e3,18e3); a0=rng.uniform(0,2*np.pi); sp=rng.uniform(3,8); hd=rng.uniform(0,2*np.pi)
    p0=np.array([r0*np.cos(a0),r0*np.sin(a0)]); v0=np.array([sp*np.cos(hd),sp*np.sin(hd)])
    cue=np.r_[p0+rng.normal(0,300,2),v0+rng.normal(0,1.5,2)]
    donors=[]
    for i in range(n_donors):
        rr=rng.uniform(5e3,35e3); aa=rng.uniform(0,2*np.pi); v=rng.uniform(2,9); hh=rng.uniform(0,2*np.pi)
        donors.append({'p0':np.array([rr*np.cos(aa),rr*np.sin(aa)]),'v':np.array([v*np.cos(hh),v*np.sin(hh)]),'phase':rng.uniform(0,SCAN_PERIOD),'mode':rng.choice(MODE_NAMES),'active':rng.random()<active_prob})
    world={'seed':seed,'duration':duration,'rx':rx,'truth_p0':p0,'truth_v0':v0,'cue':cue,'donors':donors,'maneuver_time_s':duration*0.5,'maneuver_deg':maneuver_deg,'events':[],'donor_sigma':donor_sigma}
    events=[]
    for i,d in enumerate(donors):
        t=d['phase']
        while t<duration:
            truth=truth_at(world,t); tx=d['p0']+d['v']*t
            Rt=np.linalg.norm(truth[:2]-tx); Rr=np.linalg.norm(truth[:2]-rx); Rtr=np.linalg.norm(tx-rx)
            los=(Rt/1000<=H_TX_TGT and Rr/1000<=H_RX_TGT and Rtr/1000<=H_TX_RX)
            sdb=snr_db(Rt,Rr,d['mode'],rcs,clutter_db) if los and d['active'] else -999
            pd=1/(1+math.exp(-(sdb-THRESH_DB)/2)) if sdb>-100 else 0
            detected=rng.random()<pd
            if detected:
                tx_est=tx+rng.normal(0,donor_sigma,2)
                assoc_bad=rng.random()<assoc_error_prob and len(donors)>1
                if assoc_bad:
                    choices=[j for j in range(len(donors)) if j!=i]
                    j=int(rng.choice(choices)); tx_est=donors[j]['p0']+donors[j]['v']*t+rng.normal(0,donor_sigma,2)
                z=h(truth,tx,rx)+rng.normal(0,base_meas_sigma(d['mode']))
                outlier=rng.random()<outlier_prob
                if outlier: z+=rng.choice([-1,1])*rng.uniform(150,800)
                events.append({'t':t,'donor_id':i,'mode':d['mode'],'snr':sdb,'tx_true':tx,'tx_est':tx_est,'z':z,'assoc_bad':assoc_bad,'outlier':outlier})
            t+=SCAN_PERIOD
    world['events']=events
    return world

def replay(world,policy):
    rx=world['rx']; x=world['cue'].copy(); P=np.diag([300**2,300**2,1.5**2,1.5**2]); donor_sigma=world['donor_sigma']
    bysec=defaultdict(list)
    for e in world['events']: bysec[int(e['t'])].append(e)
    tcur=0.0; used=0; rejected=0; assoc_bad_used=0; outlier_used=0
    for sec in range(world['duration']):
        t0=float(sec); t1=t0+1
        if tcur<t0: x,P=predict(x,P,t0-tcur); tcur=t0
        cands=[]
        for e in bysec.get(sec,[]):
            xe,Pe=predict(x,P,e['t']-t0)
            sig=effective_sigma(xe,e['tx_est'],rx,e['mode'],donor_sigma)
            cands.append({**e,'sigma':sig,'trace':post_trace(xe,Pe,e['tx_est'],rx,sig),'xe':xe,'Pe':Pe})
        chosen=None
        if cands and policy!='NO_PASSIVE':
            if policy=='RANDOM':
                # deterministic per-world/policy selection to preserve reproducibility
                rr=np.random.default_rng(world['seed']+sec*1009+17); chosen=cands[int(rr.integers(len(cands)))]
            elif policy=='HIGHEST_SNR': chosen=max(cands,key=lambda c:c['snr'])
            elif policy=='SHORTEST_PULSE': chosen=min(cands,key=lambda c:c['sigma'])
            elif policy=='METROLOGY_CONDITIONED_EIG': chosen=min(cands,key=lambda c:c['trace'])
        if chosen is not None:
            x,P=chosen['xe'],chosen['Pe']; tcur=chosen['t']
            x,P,accepted,nis=update(x,P,chosen['z'],chosen['tx_est'],rx,chosen['sigma'])
            if accepted:
                used+=1; assoc_bad_used+=int(chosen['assoc_bad']); outlier_used+=int(chosen['outlier'])
            else: rejected+=1
        if tcur<t1: x,P=predict(x,P,t1-tcur); tcur=t1
    truth=truth_at(world,world['duration'])
    return {'policy':policy,'seed':world['seed'],'position_error_final_m':float(np.linalg.norm(x[:2]-truth[:2])),'velocity_error_final_mps':float(np.linalg.norm(x[2:]-truth[2:])),'position_sigma_final_m':float(math.sqrt(max(0,np.trace(P[:2,:2])))),'used_measurements':used,'rejected_measurements':rejected,'assoc_bad_accepted':assoc_bad_used,'outlier_accepted':outlier_used,'eligible_measurements':len(world['events'])}

def run_world_all(seed,**kwargs):
    w=generate_world(seed,**kwargs)
    return [replay(w,p) for p in POLICIES]

