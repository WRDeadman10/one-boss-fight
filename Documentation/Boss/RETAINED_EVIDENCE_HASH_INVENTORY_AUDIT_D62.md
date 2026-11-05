# Retained evidence hash inventory audit (Queue D D62)

## Read-only reconciliation

Ran `python Scripts/Tools/check_evidence_sha256.py .`: 38 `B_*/evidence_sha256.txt` manifests, 481 parsed entries, zero malformed entries, missing files, or hash mismatches. The checker reads listed files and hashes; it does not rewrite manifests. A separate inventory found no `evidence_manifest.json` files under `Docs/`, so no JSON evidence manifests were available in this checkout to verify.

This is an integrity check of paths named by the legacy text hash lists. It reports missing or byte-changed listed files as issues; none were found. It does not compare manifests against all files in each evidence folder, so newly added/unlisted files are not reported. It also does not establish completeness of evidence, command/run identity, or gameplay proof.

## Scope and reproducibility

`check_evidence_sha256.py` scans only immediate `B_*` child folders of `Docs/BossCombatReview/Execution/Claude/` for the exact filename `evidence_sha256.txt`. Other folder naming patterns, nested manifests, and evidence outside that root are outside its automatic inventory. The tool's summary field counts manifest text lines, but all 481 nonblank/noncomment lines matched its entry format in this run. No hash list was refreshed or modified; no build, tests, or Unreal run occurred.
