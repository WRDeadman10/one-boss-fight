"""C315 measured final capture. File/process checks only; no engine launch."""
from pathlib import Path
from collections import Counter
import hashlib,json,re,subprocess,sys
H=Path(__file__).resolve().parent;ROOT=H.parents[4];R=H/'run_2026-10-29'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
expected={s.split(' *',1)[1]:s.split(' *',1)[0] for s in (H/'post_source_manifest_sha256.txt').read_text().splitlines() if ' *' in s}
current={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'Source').rglob('*') if p.is_file()}
(R/'final_source_manifest_sha256.txt').write_text(''.join(f'{v} *{k}\n' for k,v in sorted(current.items())))
binary={rel:sha(ROOT/rel) for rel in ('Binaries/Win64/UnrealEditor-OneBossFight.dll','Binaries/Win64/OneBossFight.exe')}
(R/'final_binary_sha256.txt').write_text(''.join(f'{v} *{k}\n' for k,v in binary.items()))
old_binary={s.split(' *',1)[1]:s.split(' *',1)[0] for s in (R/'pre_binary_sha256.txt').read_text().splitlines() if ' *' in s}
pre=json.loads((R/'pre_promotion_safety.json').read_text())
pin_checks=[]
changed={'Source/OneBossFight/Player/RPGBossHydrationPreparation.h','Source/OneBossFight/Player/RPGBossHydrationPreparation.cpp'}
for row in pre['pins']:
    key=row['path'];want=expected[key] if key in changed else row['actual_sha256'];now=sha(ROOT/key)
    pin_checks.append({'path':key,'expected_post_sha256':want,'final_sha256':now,'equal':want==now,'C315_promoted_replacement':key in changed})
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
dirty=subprocess.check_output(['git','status','--short','--','Source','Config','Content'],cwd=ROOT,text=True)
proc=subprocess.check_output(['powershell','-NoProfile','-Command',"Get-Process | Where-Object { $_.ProcessName -match '^(UnrealEditor.*|UnrealBuildTool|UBT|cl|link)$' } | Select-Object ProcessName,Id | ConvertTo-Json -Compress"],text=True).strip()
(R/'post_process_check.txt').write_text(proc+'\n')
tags=('activation','preparation','registry','world_preparation','production_preparation','full_dd28')
gates={tag:json.loads((R/f'{tag}_gate.json').read_text()) for tag in tags}
def warnings(p):
    rows=[re.sub(r'^\[[^]]*\]\[\s*\d+\]','',s) for s in p.read_text(errors='replace').splitlines() if ': Warning:' in s]
    return Counter(re.sub(r'(?i)(sponsor(?:process)?(?:id|pid)?[ =:]+)\d+',r'\1<PID>',re.sub(r'(?i)(epoch=)[a-f0-9]{32}\b',r'\1<EPOCH>',s)) for s in rows)
a=warnings(R/'automation_full_dd28.log');b=warnings(H.parent/'DD26/run_2026-10-29/automation_full_dd26.log')
delta={'added':dict(a-b),'removed':dict(b-a),'current_count':sum(a.values()),'prior_count':sum(b.values())}
focused=[p for tag in tags[:-1] for p in gates[tag]['paths']]
result={'source_exact':current==expected,'source_count':len(current),'binary':binary,'exe_unchanged':binary['Binaries/Win64/OneBossFight.exe']==old_binary['Binaries/Win64/OneBossFight.exe'],'head':head,'head_unchanged':head==pre['head'],'dirty':dirty,'post_processes':json.loads(proc) if proc else [],'pin_checks':pin_checks,'focused_unique':len(set(focused)),'focused_disjoint':len(focused)==len(set(focused))==22,'gates':{k:{'pass':v['pass'],'unique':v['unique'],'paths':v['paths']} for k,v in gates.items()},'warning_delta_vs_DD26':delta,'build':json.loads((R/'build_gate.json').read_text())}
(R/'final_verification.json').write_text(json.dumps(result,indent=2)+'\n')
assert result['source_exact'] and len(current)==213 and result['exe_unchanged'] and result['head_unchanged'] and not proc
assert all(c['equal'] for c in pin_checks) and result['focused_disjoint'] and all(v['pass'] for v in gates.values())
assert not delta['added'] and not delta['removed'] and delta['current_count']==63,'Warning multiset drift; report before any more operations'
# Future engine-Python operations must take these pins, not DD26's historical binary.
baseline={'release':'C-315 item6','source_manifest':str((R/'final_source_manifest_sha256.txt').relative_to(ROOT)).replace('\\','/'),'source_manifest_sha256':sha(R/'final_source_manifest_sha256.txt'),'source_count':213,'binary_manifest':str((R/'final_binary_sha256.txt').relative_to(ROOT)).replace('\\','/'),'binary_manifest_sha256':sha(R/'final_binary_sha256.txt'),'binary':binary,'head':head,'scope':'Measured DD28 baseline for a future separately released DD27-family run; not a new execution permission or gameplay acceptance'}
(H.parent/'CURRENT_ENGINE_BASELINE.json').write_text(json.dumps(baseline,indent=2)+'\n')
print(json.dumps({'all_gates_passed':True,'focused_unique':22,'full_unique':gates['full_dd28']['unique'],'binary':binary,'source_count':213,'warnings':delta,'uht_lines':result['build']['uht_lines']}))
