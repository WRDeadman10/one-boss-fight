"""Read-only safety capture for the C253/C254 execution release."""
from pathlib import Path
import sys,json,subprocess
here=Path(__file__).resolve().parent
root=here.parents[4]
sys.path.insert(0,str(here.parent/"EvidenceTools"))
from verify_bundle import parse_receipt,verify_receipt,digest
run=here/"run_2026-10-29"
run.mkdir(exist_ok=True)
expected={x["relative_path"]:x["expected_sha256"] for x in parse_receipt((here/"post_source_manifest_sha256.txt").read_text(encoding="utf-8-sig"))}
actual={p.relative_to(root).as_posix():digest(p) for p in (root/"Source").rglob("*") if p.is_file()}
r={"source_exact":actual==expected,"source_count":len(actual),"pins":{}}
dd18=root/"Docs/BossCombatReview/Execution/Claude/DD18"
for name in ["pre_pins.txt","dependency_pins_after_c245_followup_sha256.txt","candidate_assets_sha256.txt","default_catalog_assets_sha256.txt"]:
    c=verify_receipt(dd18/name,root,root)
    for row in c["checks"]:
        key=Path(row["path"]).as_posix()
        if row["status"]=="mismatch" and key in {"Source/OneBossFight/Player/RPGEncounterBinding.h","Source/OneBossFight/Player/RPGEncounterBinding.cpp"} and row["actual_sha256"]==expected[key]:
            row["status"]="reviewed_DD20_Binding_replacement"
    c["all_verified"]=all(x["status"] in {"verified","reviewed_DD20_Binding_replacement"} for x in c["checks"])
    r["pins"][name]=c
binary=root/"Docs/BossCombatReview/Execution/Codex/DD19/run_2026-10-29/final_binary_sha256.txt"
r["pins"]["binaries"]=verify_receipt(binary,root,root)
r["pins"]["five_live"]=verify_receipt(here/"live_pins_sha256.txt",root,root)
r["head"]=subprocess.run(["git","rev-parse","HEAD"],cwd=root,capture_output=True,text=True,check=True).stdout.strip()
r["dirty"]=subprocess.run(["git","status","--porcelain","--","Source","Config","Content"],cwd=root,capture_output=True,text=True,check=True).stdout
(run/"pre_safety.json").write_text(json.dumps(r,indent=2),encoding="utf-8")
(run/"pre_source_manifest_sha256.txt").write_text("".join(f"{v} *{k}\n" for k,v in sorted(actual.items())),encoding="utf-8")
(run/"pre_binary_sha256.txt").write_bytes(binary.read_bytes())
assert r["source_exact"] and len(actual)==197 and r["head"]=="79d55906d155574a0c308b33d4442f4a7acbf8b9"
assert all(x["all_verified"] for x in r["pins"].values())
print("Fresh197-source/pins/assets/binary/HEAD safety passed; reviewed Binding replacements recorded explicitly.")
