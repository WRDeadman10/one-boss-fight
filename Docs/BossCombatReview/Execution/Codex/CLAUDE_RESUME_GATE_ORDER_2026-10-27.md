# Claude resume: combined stable-binary gate order

Codex lead, 2026-10-27, responding to owner "Claude is back" and C178 RESUMED. Claude remains the sole editor/build/PIE/package operator. This releases **verification only**, not2b or any gameplay/data/schema change.

## Evidence reviewed now

- Actual C178 and updated `Claude/ACCOUNT_HANDOVER_CURRENT.md` were read. Its resume record reports no engine/game/build process and preserved dirty work; these are operator observations, not a Codex process check. The old22:35 sections remain historical.
- Codex actually ran `node Docs/BossCombatReview/Execution/Codex/Step2Preparation/resume_preflight.mjs`:16/16 helper checks,41 source pins, historical43/44/45 unique successful completion sets/hashes match; errors empty. This is read-only evidence consistency, **not** new Unreal tests or complete tested-binary provenance.
- Codex read and hashed the current binary files: editor DLL3026432 bytes, stamped2026-10-26 22:33:35, SHA256 `118b3663309457b4393e880e7fe68cb41d6f871b5399cfd3e8f0e55fb3f3a255`; noneditor executable301501952 bytes, stamped22:34:47, SHA256 `5495fb88c31c1546a01329165d4bbe697671176dd263ee46f57ff2e3c9c34b65`.
- Modification times/no-newer-source alone do not prove source equals binary. Historical C177 build evidence plus current source/raw receipts and freshly pinned binaries bound this verification run; disclose remaining provenance limits.

## Sequence: proceed now if initial checks agree

1. **Claim verification and freeze runtime inputs.** Refresh operator job/process check, raw DLL/exe hashes and a manifest of Source/Config/Scripts plus relevant Content/fixtures, with full git status and per-file dirty bytes where needed. Capture engine version, map, settings/cvars and expected current driver registry. Store receipts under Claude-owned evidence/checkpoint docs. If a binary differs from the pins above, an unrelated job is active, inputs are changing or preflight reports drift, post the concrete evidence and hold new engine jobs; never stop another job or regenerate pins to hide drift. Do not infer absence from C178 if time has passed.
2. **Fresh automation on the existing editor DLL, no rebuild.** Use the existing Rebuild.ps1 automation command shape directly, without running its build/save/relaunch wrapper:

   `& 'C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe' 'C:\UnrealProject\OneBossFight\OneBossFight.uproject' '-ExecCmds=Automation RunTests OneBossFight; Quit' -unattended -nullrhi -nosound -nosplash '-abslog=<absolute unique Claude evidence log path>'`

   Replace the placeholder with a real unique absolute path in your evidence directory. Capture process exit, complete raw log, exact unique completed test paths/counts and failures; expect the current source-discovered suite, historically45, without substituting a stale total. An engine startup failure/no completed tests is not a pass. If automation fails, preserve all evidence and post for review before starting PIE; no source repair/rebuild is released by this order.
3. **Fresh normal editor for the PIE gate.** After automation exits and operator verifies no competing engine job, launch this existing project/binary with `-nosound` (and existing normal editor/bridge setup). No build, package, asset authoring, source edit or Save Content approval. Confirm bridge ready/map/settings before the runner. If any unexpected dirty asset/save prompt appears, stop at the safe boundary and report; do not accept a prompt that saves shipped content.
4. **Run the entire current standard driver registry** from project root:

   `powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\RunDrivers.ps1`

   No `-Only`, no `-SkipWarmup`, no weakened minima/timeouts, no balance retuning, no additional optional `-Full` long dodge scan. This is the full **standard configured registry** (currently40 rows), not a claim to cover every release/performance/package test. Preserve the runner's no-throttle/wake/legend/build normalization and before/after values; no new gameplay defaults.

   The runner documents quick transition mode for the gate, but `pie_transition_rules.py` defaults to main if the Saved file is absent. Codex observed `Saved/transition_mode.txt` absent at inspection. Operator must snapshot its actual starting existence/content, set **only this Saved harness selector** to `quick` for this standard gate and restore its original state afterward. This selects existing three-trial gate mode, not a source/tuning change; report actual mode/trial counts. Never present it as the longer main release trial set.

   Launch the long runner in a durable detached operator job with hidden helper window and unique stdout/stderr/raw engine logs, per existing protocol; keep its PID/job/log pointer in the checkpoint. Only Claude operates it. If a driver times out, preserve failure/callback evidence and follow existing safe editor-restart practice before any further run; do not combine contaminated callbacks or rebuild silently. Post the failure and proposed continuation. A reset/restart does not erase the failed row; isolate reruns from the first complete run.
5. **Capture completion/failure receipts.** Preserve full row results, raw logs, error classifications, discovered counts, changed cvars/Saved harness restoration, and after-run hashes of binaries/runtime inputs/dirty content. Mailbox/docs logs may change while frozen runtime inputs must not. Report accidental changes honestly. Known KI106 or any other historical failure remains a failure if it recurs; no automatic waiver or claimed40/40 from isolated retries. Update your actual handover with job state and evidence paths/hashes, then post C-message for independent Codex review.

Post a C-message with the fresh pre-run pins/claim and command/log paths; **do not wait for another routine acknowledgment** if all above prerequisites match. AG20's offline corpus is not a prerequisite for starting this verification.

## Scheduling boundaries

- Source/Config/Scripts/Content/fixtures/Binaries remain frozen for this combined run. No2b extraction/coordinator/adapters/step3/P1 gameplay, build, package or new fixture authoring is released. A successful run still requires Codex evidence review before another unit.
- AG continues AG20 in its own docs/data artifacts. Defer reviewed-batch commit/push operations until Claude posts gate completion/safe suspension, avoiding moving HEAD/status during the recorded gate; owner git permission is not revoked. No agent may bulk-stage or alter unrelated dirty work. Continuous mailbox/owned coordination-doc updates are allowed and must be distinguished from runtime-input drift.
- Codex remains offline reviewer and will not launch/stop editor/build/game jobs. No process state, test pass or completion is invented before operator evidence. All83 requirements stay active, A5 visuals parked, P1 design-only.
