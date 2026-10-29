"""Prepare source-only DD19 handoff. No engine, build, git or asset operations."""
from pathlib import Path
import hashlib,json,difflib,re,sys
here=Path(__file__).resolve().parent
root=here.parents[4]
sys.path.insert(0,str(here.parent/"EvidenceTools"))
from verify_bundle import verify_receipt,parse_receipt
claude=root/"Docs/BossCombatReview/Execution/Claude/DD19"
players=root/"Source/OneBossFight/Player"
tests=root/"Source/OneBossFight/Tests"
files=[players/"RPGBossBleedAdapters.h",players/"RPGBossBleedAdapters.cpp",
       players/"RPGEncounterBinding.h",players/"RPGEncounterBinding.cpp",
       tests/"RPGBossBleedAdaptersTests.cpp"]
review=here/"Review"
review.mkdir(exist_ok=True)
# Preserve original received snapshots; normalize only the three edited source files.
edited={"RPGBossBleedAdapters.h","RPGBossBleedAdapters.cpp","RPGBossBleedAdaptersTests.cpp"}
for p in files:
    if p.name in edited:
        data=p.read_bytes().replace(b"\r\n",b"\n")
        p.write_bytes(data.replace(b"\n",b"\r\n"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
integrity=verify_receipt(claude/"evidence_sha256.txt",claude,root)
assert integrity["all_verified"]
(here/"received_evidence_verification.json").write_text(json.dumps(integrity,indent=2),encoding="utf-8")
before=claude/"post_write_source_manifest_sha256.txt"
(here/"received_C251_source_manifest_sha256.txt").write_bytes(before.read_bytes())
current={p.relative_to(root).as_posix():sha(p) for p in (root/"Source").rglob("*") if p.is_file()}
(here/"source_full_manifest_sha256.txt").write_text("".join(f"{v} *{k}\n" for k,v in sorted(current.items())),encoding="utf-8")
old={r["relative_path"]:r["expected_sha256"] for r in parse_receipt(before.read_text(encoding="utf-8-sig"))}
foundation=root/"Docs/BossCombatReview/Execution/Claude/DD18/run_2026-10-28/final_source_manifest_sha256.txt"
base={r["relative_path"]:r["expected_sha256"] for r in parse_receipt(foundation.read_text(encoding="utf-8-sig"))}
delta={"added":sorted(current.keys()-base.keys()),"removed":sorted(base.keys()-current.keys()),
       "changed":sorted(k for k in base.keys()&current.keys() if base[k]!=current[k])}
assert {Path(k).name for k in delta["added"]}=={"RPGBossBleedAdapters.h","RPGBossBleedAdapters.cpp","RPGBossBleedAdaptersTests.cpp"}
assert {Path(k).name for k in delta["changed"]}=={"RPGEncounterBinding.h","RPGEncounterBinding.cpp"} and not delta["removed"]
(here/"source_delta_from_accepted_DD18.json").write_text(json.dumps(delta,indent=2),encoding="utf-8")
changed=sorted(k for k in old.keys()&current.keys() if old[k]!=current[k])
assert len(current)==194 and current.keys()==old.keys()
assert {Path(k).name for k in changed}==edited
diffs=[];follow=[];pins=[]
for p in files:
    rel=p.relative_to(root).as_posix()
    snapshot=here/"Received_C251"/p.name
    # Received bytes must agree with the frozen Claude manifest.
    assert hashlib.sha256(snapshot.read_bytes()).hexdigest()==old[rel]
    baseline=(claude/"Review"/(p.name+".preimage")) if p.name.startswith("RPGEncounterBinding") else None
    oldlines=baseline.read_text(encoding="utf-8").splitlines(keepends=True) if baseline else []
    lines=p.read_text(encoding="utf-8").splitlines(keepends=True)
    diffs.extend(difflib.unified_diff(oldlines,lines,fromfile=rel if baseline else "/dev/null",tofile=rel))
    follow.extend(difflib.unified_diff(snapshot.read_text(encoding="utf-8").splitlines(keepends=True),lines,fromfile="received_C251/"+p.name,tofile=rel))
    (review/p.name).write_bytes(p.read_bytes())
    pins.append(f"{sha(p)} *{rel}\n")
    assert b"\n" not in p.read_bytes().replace(b"\r\n",b"")
(here/"five_file.diff").write_text("".join(diffs),encoding="utf-8")
(here/"revision_from_C251.diff").write_text("".join(follow),encoding="utf-8")
(here/"live_pins_sha256.txt").write_text("".join(pins),encoding="utf-8")
(here/"source_delta_from_C251.json").write_text(json.dumps({"added":[],"removed":[],"changed":changed},indent=2),encoding="utf-8")
receipts=[]
for p in sorted(here.rglob("*")):
    if p.is_file() and p.name!="evidence_sha256.txt" and "__pycache__" not in p.parts:
        receipts.append(f"{sha(p)} *{p.relative_to(here).as_posix()}\n")
(here/"evidence_sha256.txt").write_text("".join(receipts),encoding="utf-8")
verified=verify_receipt(here/"evidence_sha256.txt",here,root)
assert verified["all_verified"]
print("Historical C251 receipts:",integrity["entries"],"verified")
print("Current Source files:",len(current),"changed from C251:",changed)
print("Own delivery receipts:",verified["entries"],"verified")
for p in files:print(p.name,sha(p))
print("Source-only preparation exit0; no compilation, Unreal test or runtime pass claimed.")
