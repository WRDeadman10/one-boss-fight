"""Independent C248 integrity capture; does not execute engine or supplied code."""
from pathlib import Path
import sys, json, hashlib
here=Path(__file__).resolve().parent
root=here.parents[3]
sys.path.insert(0,str(here/"EvidenceTools"))
from verify_bundle import verify_receipt, parse_receipt, digest
package=root/"Docs/BossCombatReview/Execution/Claude/DD18"
out=here/"C248Evidence"
out.mkdir(exist_ok=True)
reports={}
for name,base in [
    ("evidence_sha256.txt",package),
    ("post_c246_correction_full_tree_manifest_sha256.txt",root),
    ("pre_pins.txt",root),
    ("dependency_pins_after_c245_followup_sha256.txt",root),
    ("candidate_assets_sha256.txt",root),
    ("default_catalog_assets_sha256.txt",root),
    ("pre_binary_sha256.txt",root),
]:
    reports[name]=verify_receipt(package/name,base,root)
def manifest(name):
    return {r["relative_path"]:r["expected_sha256"] for r in parse_receipt((package/name).read_text(encoding="utf-8-sig"))}
current=manifest("post_c246_correction_full_tree_manifest_sha256.txt")
for name in ("pre_source_manifest_sha256.txt","post_c245_followup_full_tree_manifest_sha256.txt"):
    old=manifest(name)
    reports["delta_from_"+name]={"added":sorted(current.keys()-old.keys()),"removed":sorted(old.keys()-current.keys()),"changed":sorted(k for k in old.keys()&current.keys() if old[k]!=current[k])}
actual={p.relative_to(root).as_posix():digest(p) for p in (root/"Source").rglob("*") if p.is_file()}
reports["exact_source_set"]={"actual_count":len(actual),"manifest_count":len(current),"equal":actual==current}
copies=[]
for p in sorted((package/"Review").iterdir()):
    if p.suffix not in (".h",".cpp"): continue
    found=[q for q in (root/"Source").rglob(p.name)]
    copies.append({"file":p.name,"live_matches":len(found)==1 and digest(p)==digest(found[0]),"sha256":digest(p)})
reports["review_copies"]=copies
for name in ("post_c246_correction_full_tree_manifest_sha256.txt","evidence_sha256.txt"):
    (out/name).write_bytes((package/name).read_bytes())
text=json.dumps(reports,indent=2)
(out/"verification.json").write_text(text,encoding="utf-8")
(out/"verification.sha256").write_text(hashlib.sha256(text.encode()).hexdigest()+" *verification.json\n",encoding="utf-8")
for name,r in reports.items():
    if isinstance(r,dict) and "entries" in r: print(name,r["entries"],r["all_verified"])
    elif name.startswith("delta") or name=="exact_source_set": print(name,r)
print("review_copies",copies)
assert all(r["all_verified"] for r in reports.values() if isinstance(r,dict) and "entries" in r)
assert reports["exact_source_set"]["equal"] and all(r["live_matches"] for r in copies)
print("Integrity capture exit0 is not compilation or runtime proof.")
