# Offline replacement-account preflight — 2026-10-26

Run from project root: `node Docs/BossCombatReview/Execution/Codex/Step2Preparation/resume_preflight.mjs`.

Read-only: no engine/build/process or git commands; no asset/source writes. Checks38 source-observation pins plus3 applied scaffold raw pins (41 total), exact hashes AND completed/success counts for C17043/43, C17244/44 and2a45/45 logs; prints current handover file digest. Rejects missing/drifted/bad/duplicate/escaping input and automation missing/failed/extra entries.11 embedded helper tests passed in the recorded run. All41 pins matched, all3 evidence hashes/counts matched, no consistency errors. Checkpoint digest87b061946c8dfe5392ebfc17585762f15296182bbbc1c3405b2e11adaaf6fc85 at this read.

This is evidence consistency ONLY. Exit0 does NOT authorize runtime resumption, prove this binary generated those logs, establish active process/editor/cvar state, validate Shipping or replace full gate. Operator must independently inspect current processes/settings/jobs and latest scope before RESUMED. Expected source drift after an authorized packet is reviewed/versioned; do not rewrite pins simply to make a check green. Keep failed historical attempts.

The current editor DLL hash observed read-only was118b3663309457b4393e880e7fe68cb41d6f871b5399cfd3e8f0e55fb3f3a255; noneditor executable5495fb88c31c1546a01329165d4bbe697671176dd263ee46f57ff2e3c9c34b65. These are current-byte observations, NOT a signed build provenance link to earlier automation. A future gate must pin its actual binary/source/config/asset inputs at launch.

## 2026-10-27 identity-count correction

The original11-check helper rejected an extra completion but did not reject two identical successful paths replacing a missing test at the same expected count. Its old count-only predicate would accept that fixture. Existing exact raw-log hashes separately prevented silent replacement of the three pinned evidence files; this was a helper validation weakness, not a newly failed Unreal run.

`countAutomation` now requires a positive safe-integer expected count, a nonblank `Path={...}` on each completion and unique full paths. Equal short names in distinct suites remain valid. Summary reports unique/missing/duplicate path counts. Five added offline checks cover same-count substitution, distinct suites with equal names, missing/blank identity and zero expected count. Current16/16 helper checks pass; actual pinned logs remain43/43 unique,44/44 unique and45/45 unique, hashes unchanged. All41 source pins match and checkpoint still hashes87b06194...fc85. No source/evidence pins were regenerated. This does not prove expected test-set membership beyond the pinned historical bytes, runtime readiness or binary provenance.
