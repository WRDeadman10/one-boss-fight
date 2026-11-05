# Framework proof workflow

This workflow describes the existing F4 proof runner and validator. Run proof in the windowed UE 5.5.4 editor; the C1 guide documents that level-actor authoring is not supported by the NullRHI editor path.

## Run a proof

From the repository root, use the checked-in PowerShell wrapper (example run recorded under `Docs/BossCombatReview/Execution/Claude/F4`):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File Docs\BossCombatReview\Execution\Claude\F4\run_pie.ps1 -Map /Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofF4 -OutDir Docs\BossCombatReview\Execution\Claude\F4\final_f4_run1 -Task "F4-review"
```

The wrapper owns the editor lock, captures command/result and raw editor logs in the run directory, and must be used instead of opening a second editor. Inspect the generated `command.json`, `result.json`, and `editor_raw.log`; preserve the raw log with the run evidence.

## Validate structured logs

The canonical syntax and semantic validator is:

```powershell
python Docs\BossCombatReview\Execution\Antigravity\Reviews\validate_framework_proof_logs.py Docs\BossCombatReview\Execution\Claude\F4\final_f4_run1\editor_raw.log
```

It checks every `[FrameworkProof]` line against a registered token schema and applies cross-line invariants. Unknown tokens, malformed fields, missing expected events, or failed semantic checks fail the proof review. See [LOG_TOKENS.md](LOG_TOKENS.md) for the current schema inventory.

When writing expected sheets, classify checks as measured, inferred, or manual and preserve unproven branches explicitly; see [EXPECTED_SHEET_AUTHOR_GUIDE_S152.md](EXPECTED_SHEET_AUTHOR_GUIDE_S152.md) for a strong measured example and a limited negative setup.

## Preserve evidence

Each proof run belongs in a task-specific directory under `Docs/BossCombatReview/Execution/Claude/`. Record exact command/map/task, preserve raw output, and keep the final result alongside it. `evidence_sha256.txt` manifests list relative paths and SHA-256 values for the evidence files; generate/update them only as part of the owning task and verify them offline:

Before refreshing hashes or preparing a handover, follow [EVIDENCE_HASH_REFRESH_CHECKLIST_S187.md](EVIDENCE_HASH_REFRESH_CHECKLIST_S187.md). It distinguishes unchanged source, same-source/new-build, and unchanged evidence.

```powershell
python Scripts\Tools\check_evidence_sha256.py .
```

The helper verifies manifests under `Docs/BossCombatReview/Execution/Claude/B_*`; it does not establish that evidence is sufficient or that a run proves the intended gameplay claim. Review the run conditions and log semantics too. A PIE result is scoped to its map, build, configuration, and tested scenario.

For examples of a positive pass, paired negative control, retained failure, and hash manifest, see [EVIDENCE_RETENTION_GUIDE_S155.md](EVIDENCE_RETENTION_GUIDE_S155.md).
