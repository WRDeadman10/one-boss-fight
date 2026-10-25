#!/usr/bin/env python3
"""Pure Python boss decision sandbox (not Unreal API, no external packages).

Run: python code/combat_decision_reference.py --distance 220 --yaw 30 --phase 2 --seed 42
     python code/combat_decision_reference.py --distance 150 --yaw 165 --phase 1

All numbers hypothetical and explicitly not Elden Ring data.
"""
import argparse,csv,math,random
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def load_attacks():
    with open(ROOT/'data'/'attack_catalogue.csv',newline='',encoding='utf8') as f:
        return list(csv.DictReader(f))

def eligible(a,distance,yaw,phase,cooldowns=None):
    reasons=[]
    if phase<int(a['AvailableFromPhase']): reasons.append('Phase')
    if not float(a['MinRangeCm'])<=distance<=float(a['MaxRangeCm']): reasons.append('Range')
    # AbsYaw works symmetrically for left and right rear angles.
    ay=abs(yaw)
    if not float(a['MinAbsYawDeg']) <= ay <= float(a['MaxAbsYawDeg']):
        reasons.append('Angle')
    if cooldowns and a['AttackID'] in cooldowns: reasons.append('Cooldown')
    return reasons

def score(a,distance,yaw,recovery,repeat):
    ideal=float(a['PreferredRangeCm'])
    reach=max(100,float(a['MaxRangeCm'])-float(a['MinRangeCm']))
    rf=max(0,1-abs(distance-ideal)/reach)
    # side/rear naturally works by the explicit gate; this fit rewards near direction center.
    mn,mx=abs(float(a['MinYawDeg'])),abs(float(a['MaxYawDeg']))
    if a['AttackID']=='A05': preferred=145
    elif a['AttackID'] in ('A09','A10'): preferred=90
    else: preferred=0
    af=max(0,1-abs(abs(yaw)-preferred)/180)
    opportun=min(1,max(0,recovery))
    varied=0 if a['AttackID'] in repeat else 1
    return round(float(a['BaseWeight'])*(.28*rf+.20*af+.20*opportun+.12*.7+.10*.75+.10*varied)-(0.15 if a['AttackID'] in repeat else 0),4)

def decide(distance,yaw,phase,recovery,seed,repeat=()):
    trace=[]
    for a in load_attacks():
        errors=eligible(a,distance,yaw,phase)
        trace.append({'id':a['AttackID'],'name':a['Name'],'eligible':not errors,
                      'reason':','.join(errors) or 'ok','score':score(a,distance,yaw,recovery,repeat) if not errors else None})
    valid=[r for r in trace if r['eligible']]
    if not valid: return None,trace
    best=max(r['score'] for r in valid)
    near=[r for r in valid if r['score']>=best-.12]
    # Deterministic seeded temperature-weighted choice over near-best candidates only.
    rng=random.Random(seed)
    temp=.18
    weights=[math.exp((r['score']-best)/temp) for r in near]
    pick=rng.choices(near,weights=weights,k=1)[0]
    return pick,trace

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--distance',type=float,default=220,help='Centimeters')
    p.add_argument('--yaw',type=float,default=20,help='Signed angle [-180,+180] degrees')
    p.add_argument('--phase',type=int,default=1,choices=[1,2])
    p.add_argument('--recovery',type=float,default=0,help='Player remaining recovery in seconds')
    p.add_argument('--seed',type=int,default=42)
    p.add_argument('--repeat',nargs='*',default=[])
    args=p.parse_args()
    pick,trace=decide(args.distance,args.yaw,args.phase,args.recovery,args.seed,args.repeat)
    print(f'Context: distance={args.distance}cm yaw={args.yaw}° phase={args.phase} playerRecovery={args.recovery}s seed={args.seed}')
    for r in sorted(trace,key=lambda x:(x['eligible'], x['score'] if x['score'] is not None else -100),reverse=True):
        print(f"{r['id']:>3} {r['name']:<24} {'eligible' if r['eligible'] else r['reason']:<20} {str(r['score']):>7}")
    print('SELECTED:',pick['id']+' '+pick['name'] if pick else 'Reposition / purposeful wait')
if __name__=='__main__':main()
