# C-1231b Ember notify strict audit and PIE parity driver

## Scope

Implemented the `-Strict` option for `EmberMontageTimingAudit` and authored a Lead-run PIE comparison for A1, A3a, and A3b with `bUseMontageNotifyTimings` disabled and enabled. No timing annotation assets were authored or modified by Codex. The PIE driver was not run, as directed; Claude should run it after the annotations are authored.

## Strict audit

The commandlet's default remains report-only. With `-Strict`, it exits nonzero when it finds any timing mismatch, duplicate annotation, or invalid annotation. Missing optional annotations and untracked montages remain informational. Branch-stage annotations compare both `BranchRange` and `BranchConeDegrees` to the live `URPGAttackTracker` instance values, in addition to the row's `bBranchStage` state. The Editor automation test covers both branch values and strict-failure cases for each required category.

Current pre-annotation readback is 6 montages, 4 expected missing timing annotations (A1, A2, A3a, A3b), 2 untracked non-combat montages, 0 mismatch, 0 duplicate, and 0 invalid. Strict audit exits 0. A3b must use the live values `BranchRange=400` and `BranchConeDegrees=120`; these are read from the tracker instance rather than copied as an alternate acceptance source.

## PIE parity driver

`Scripts/Editor/pie_ember_notify_timing_parity.py` holds the encounter, repositions the player inside A3b's frontal branch gate, replays each move with the timing flag off and on, and logs each observed Committed, Active, Recovery, and Complete transition with montage position. It opens a parry at the C-1132 observed contact position minus 0.08 seconds, logs the accepted parry contact position, and emits one final `[EmberNotifyParity] RESULT PASS|FAIL` line.

C-1132 supplies observed hit positions of A1 0.351 s, A3a 0.484 s, and A3b 0.152 s, and recommends opening parry 0.08 s before those observations. It does not independently name an acceptance tolerance. The driver therefore labels 0.08 s as an operational parity tolerance derived from that lead margin; it is an explicit interpretation for this probe, not a separate Lead-approved threshold or a replacement for the C-1132/C-1152 acceptance matrix.

## Verification

- `python -m py_compile Scripts/Editor/pie_ember_notify_timing_parity.py`: PASS.
- PowerShell AST parse for `run_c1231b_ember_notify_parity_build.ps1`: PASS.
- Scoped `git diff --check` for the commandlet implementation and editor module: PASS. A repository-wide check still reports the pre-existing trailing whitespace at `Documentation/Boss/C1228_EMBER_NOTIFY_INVENTORY.md:333`.
- C-1155 Development build: PASS (`BUILD_EXIT=0`).
- Strict `EmberMontageTimingAudit -Strict`: PASS (`STRICT_AUDIT_EXIT=0`); 0 mismatch/duplicate/invalid.
- Full `Automation RunTests OneBossFight`: PASS, 496/496 (`SUITE_EXIT=0`, `FAILED=0`). Pinned manifest: `cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec`.
- Both C-1155 lock files were released. No PIE/driver run, asset save, commit, or push.

Raw evidence: `Docs/BossCombatReview/Execution/Codex/C1231B_EMBER_NOTIFY_PARITY/`.
