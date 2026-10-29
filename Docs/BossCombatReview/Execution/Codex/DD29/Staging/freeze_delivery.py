from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parent;ROOT=R.parents[5]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
names=('RPGBossActivation.h','RPGBossActivation.cpp','RPGBossActivationWorldTests.cpp')
for name in names:
    p=R/name;p.write_bytes(p.read_text(encoding='utf-8').replace('\n','\r\n').encode('utf-8'))
manifest=json.loads((R/'staged_manifest.json').read_text())
manifest['files']=[{'path':n,'size':(R/n).stat().st_size,'sha256':sha(R/n)} for n in names]
manifest['hard_error_policy']='Explicit thread/cleanup and mid-call stable-input drift tokens; lead review pending, no runtime drift test'
(R/'staged_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
mutations=[]
for n in names[1:]:
    for i,line in enumerate((R/n).read_text(encoding='utf-8').splitlines(),1):
        if re.search(r'\.(Add(?:Unique)?|Emplace|Append|Insert|Reset|Sort)\(',line):mutations.append({'file':n,'line':i,'text':line.strip()})
(R/'array_mutations.json').write_text(json.dumps(mutations,indent=2)+'\n',encoding='utf-8')
base=ROOT/'Docs/BossCombatReview/Execution/Codex/DD28/run_2026-10-29/final_source_manifest_sha256.txt'
want={s.split(' *',1)[1]:s.split(' *',1)[0] for s in base.read_text().splitlines() if ' *' in s}
now={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'Source').rglob('*') if p.is_file()}
assert now==want and len(now)==213,'Live Source drift'
assert len(manifest['new_test_names'])==5 and not manifest['tests_run']
print(json.dumps({'live_source_unchanged':213,'staged_files':manifest['files'],'new_UNRUN_tests':5}))
