"""Read-only review capture. No Unreal import or received command execution."""
from pathlib import Path
import hashlib, json, sys
root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(Path(__file__).parent / "EvidenceTools"))
from verify_bundle import verify_receipt
out = Path(__file__).parent / "Mail693Evidence"
out.mkdir(exist_ok=True)
execution = root / "Docs/BossCombatReview/Execution"
results = {}
for key, package, base in [
    ("DD17", execution/"Claude/DD17", execution/"Claude/DD17"),
    ("DD18", execution/"Claude/DD18", execution/"Claude/DD18"),
    ("AGToolkit", execution/"Antigravity/AuthoringToolkit", root),
    ("AGBuild", execution/"Antigravity/BuildAuthoringHelper", root),
]:
    results[key] = verify_receipt(package/"evidence_sha256.txt", base, root)
manifest = execution/"Claude/DD18/post_c245_followup_full_tree_manifest_sha256.txt"
results["current_source_manifest"] = verify_receipt(manifest, root, root)
files = [
    root/"Source/OneBossFight/Player/RPGBossPreparationRegistry.cpp",
    root/"Source/OneBossFight/Player/RPGBossWorldPreparation.cpp",
    root/"Source/OneBossFight/Player/RPGBossWorldInputCompiler.cpp",
    execution/"Antigravity/AuthoringToolkit/draft_boss_profiles.py",
    execution/"Antigravity/AuthoringToolkit/evidence_sha256.txt",
]
snapshots=[]
for p in files:
    data=p.read_bytes()
    target=out/(p.parent.name+"_"+p.name)
    if target.exists() and target.read_bytes()!=data:
        raise RuntimeError("Review snapshot already exists with different bytes")
    target.write_bytes(data)
    snapshots.append({"path":str(p.relative_to(root)), "sha256":hashlib.sha256(data).hexdigest()})
results["reviewed_snapshots"]=snapshots
text=json.dumps(results,indent=2)
(out/"verification.json").write_text(text,encoding="utf-8")
(out/"verification.sha256").write_text(hashlib.sha256(text.encode()).hexdigest()+" *verification.json\n",encoding="utf-8")
for key,value in results.items():
    if isinstance(value,dict):
        print(key,value["entries"],value["all_verified"],value["receipt_sha256"])
print("Review capture completed; integrity is not runtime acceptance.")
