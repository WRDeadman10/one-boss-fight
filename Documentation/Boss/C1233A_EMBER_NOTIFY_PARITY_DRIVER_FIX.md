# C-1233a Ember notify parity driver fixes

Updated the Lead-only parity driver after the C-1233 verdict. It has two distinct arms: TIMING runs each A1/A3a/A3b move with no parry input, and PARRY runs separately with the C-1132-derived press lead. The TIMING arm tails the active project log and records commit, active-window, recovery, and end positions only from native `LogRPGAttack` lines. An end before Recovery fails the natural-completion check. The PARRY arm records contact only when `URPGPlayerParry`'s shared `NotifyParried` route increments `ParriedCount`.

Before the first move, the driver requests wake, holds the test encounter, and waits with two-second heartbeat messages until the encounter is neither dormant nor waking; a 30-second timeout fails closed. The player remains within the A3b branch range/cone. Each move starts with boss health restored to full. The driver remains unrun by Codex per C-1233.

## Verification

- `python -m py_compile Scripts/Editor/pie_ember_notify_timing_parity.py Scripts/Editor/test_ember_notify_timing_parity_contract.py`: PASS.
- Offline parity-driver contract: PASS, 3/3.
- C-1155 Development build: PASS, exit 0.
- Strict montage timing audit: exit 0; all authored A1/A3a/A3b annotations match, one expected missing optional A2 annotation, zero mismatch/duplicate/invalid, two untracked non-combat montages.
- Full `Automation RunTests OneBossFight`: PASS, 497/497, zero failures; pinned DD27j manifest hash `cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec`.
- Both C-1155 locks released. `git diff --check` on task files passes; doc links report 0 broken.
- PIE driver: not run by Codex; no asset authoring, commit, or push.

Raw build, audit, suite, and lock receipts: `Docs/BossCombatReview/Execution/Codex/C1233A_EMBER_NOTIFY_PARITY_FIX/`.
