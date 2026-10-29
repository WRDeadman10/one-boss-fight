"""DD24 source-only capture. Does not run Unreal, a compiler or a test."""
from pathlib import Path
import json,hashlib,difflib,sys,re
here=Path(__file__).resolve().parent
root=here.parents[4]
sys.path.insert(0,str(here.parent/"EvidenceTools"))
from verify_bundle import parse_receipt,digest
files=[root/"Source/OneBossFight/Player"/n for n in ["RPGBossCloseClipSwapAdapters.h","RPGBossCloseClipSwapAdapters.cpp","RPGEncounterBinding.h","RPGEncounterBinding.cpp"]]
files.append(root/"Source/OneBossFight/Tests/RPGBossCloseClipSwapAdaptersTests.cpp")
review=here/"Review"
review.mkdir(exist_ok=True)
baseline={r["relative_path"]:r["expected_sha256"] for r in parse_receipt((here/"pre_source_manifest_sha256.txt").read_text(encoding="utf-8-sig"))}
for p in files:
    data=p.read_bytes().replace(b"\r\n",b"\n")
    p.write_bytes(data.replace(b"\n",b"\r\n"))
current={p.relative_to(root).as_posix():digest(p) for p in (root/"Source").rglob("*") if p.is_file()}
delta={"added":sorted(current.keys()-baseline.keys()),"removed":sorted(baseline.keys()-current.keys()),
       "changed":sorted(k for k in baseline.keys()&current.keys() if baseline[k]!=current[k])}
assert len(baseline)==206 and len(current)==209
assert {Path(k).name for k in delta["added"]}=={"RPGBossCloseClipSwapAdapters.h","RPGBossCloseClipSwapAdapters.cpp","RPGBossCloseClipSwapAdaptersTests.cpp"}
assert {Path(k).name for k in delta["changed"]}=={"RPGEncounterBinding.h","RPGEncounterBinding.cpp"} and not delta["removed"]
for p in (here/"Preimages").iterdir():
    key="Source/OneBossFight/Player/"+p.name
    assert digest(p)==baseline[key], "Preimage mismatch"
(here/"post_source_manifest_sha256.txt").write_text("".join(f"{v} *{k}\n" for k,v in sorted(current.items())),encoding="utf-8")
(here/"source_delta.json").write_text(json.dumps(delta,indent=2),encoding="utf-8")
diff=[];pins=[];details=[]
for p in files:
    relative=p.relative_to(root).as_posix()
    pre=here/"Preimages"/p.name
    old=pre.read_text(encoding="utf-8").splitlines(keepends=True) if pre.exists() else []
    text=p.read_text(encoding="utf-8")
    diff.extend(difflib.unified_diff(old,text.splitlines(keepends=True),fromfile=relative if pre.exists() else "/dev/null",tofile=relative))
    (review/p.name).write_bytes(p.read_bytes())
    pins.append(f"{digest(p)} *{relative}\n")
    data=p.read_bytes()
    assert b"\n" not in data.replace(b"\r\n",b"") and b"\r" not in data.replace(b"\r\n",b"")
    details.append({"path":relative,"sha256":digest(p),"bytes":len(data),"lines":len(text.splitlines())})
    if p.name.startswith("RPGBossCloseClipSwap"):
        assert not re.search(r'["\']/Game/',text), "Unexpected asset literal in new source"
(here/"five_file.diff").write_text("".join(diff),encoding="utf-8")
(here/"live_pins_sha256.txt").write_text("".join(pins),encoding="utf-8")
details={"scope":"Source-only integrity, NOT compilation or Unreal tests","baseline":206,"current":209,
         "old_files_unchanged":204,"delta":delta,"files":details,
         "test_names":re.findall(r'"(OneBossFight\.Binding\.CloseClipSwap\.[^"]+)"',files[-1].read_text(encoding="utf-8"))}
assert len(details["test_names"])==6 and len(set(details["test_names"]))==6
(here/"source_checks.json").write_text(json.dumps(details,indent=2),encoding="utf-8")
print(json.dumps(details,indent=2))
print("Source capture completed exit0. No build/UHT/engine/automation was executed.")
