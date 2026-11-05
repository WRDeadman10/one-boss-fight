# Queue Q16–Q20 — evidence runner and cleanup status

## Q016 — fresh Lead evidence run

The common `run_editor_script.ps1` path is hardened to require a new OutDir,
emit pre/post snapshots, raw log, result, and relative SHA-256 manifest. Q020's
offline guard and syntax checks pass below. A fresh Editor run is still
Claude-owned; Codex did not launch Unreal or create a run pack.

## Q017–Q018 — P35 referencer report and candidate reconciliation

Lead Editor execution remains pending. The read-only census script is
`Scripts/Editor/report_owner_cleanup_referencers.py`; it queries direct hard
and soft Asset Registry references for the seven exact packages listed in
`Documentation/Boss/P31_P35_PIPELINE_HARDENING.md`. There is no new
`[P35_REFERENCERS_JSON]` output, so Q018 cannot yet record per-asset counts or
reference identities. No candidate was deleted or saved.

## Q019 — retain candidates pending the owner decision

The owner decision row in `Documentation/Boss/OWNER_DECISIONS_PENDING.md`
keeps every candidate until referencer evidence is captured and explicitly
states that a zero count alone is not deletion authorization. It links the
seven-package inventory and run context in P31–P35. Counts cannot be linked
until Q017 is run; no cleanup choice is inferred.

## Q020 — existing-OutDir refusal

Executed:

```text
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/Tools/test_editor_runner_syntax.ps1
PASS PowerShell AST parse
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/Tools/test_run_editor_script_guard.ps1 -Runner Docs/BossCombatReview/Execution/Claude/run_editor_script.ps1
PASS existing evidence folder refused without mutation
```

The test passed the existing-folder refusal without launching the Editor or
writing inside the evidence directory. This proves the guard fixture only;
it does not establish a fresh run's hashes or logs.
