# C-1232a Ember notify parity driver hotfix

## Changes

Replaced the PIE driver's `set_editor_property` writes on the live boss `RPGAttackTracker` with a BlueprintCallable test switch, `SetUseMontageNotifyTimingsForTest`, and a BlueprintPure readback, `GetUseMontageNotifyTimingsForTest`. The setter changes runtime state in non-Shipping builds and ignores calls in Shipping. A native automation test verifies the switch defaults off, can be enabled, and restores off.

The parity driver now restores the initial mode through the same runtime API, heals the boss to full health before each move, and emits `WAIT_HEARTBEAT` messages while waiting for the boss/probe components. If they do not appear within 15 seconds, the driver records a failure, emits its one final `[EmberNotifyParity] RESULT FAIL` line, and exits PIE. All failure/exception paths emit the same single result line. The driver was not run.

## Verification

- `python -m py_compile Scripts/Editor/pie_ember_notify_timing_parity.py`: PASS.
- C-1155 Development `OneBossFightEditor` build: PASS.
- Strict read-only `EmberMontageTimingAudit`: exit 0; 6 montages, 4 expected missing annotations, 0 mismatch/duplicate/invalid, 2 untracked non-combat montages.
- Full `Automation RunTests OneBossFight`: PASS, 497/497, including `OneBossFight.Boss.AttackTracker.NotifyTimingTestSwitch`.
- Pinned manifest: `cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec`.
- Both C-1155 lock files released. No PIE/parity driver run, no asset authoring, no commit or push.

Raw logs and results: `Docs/BossCombatReview/Execution/Codex/C1232A_EMBER_NOTIFY_PARITY/`.
