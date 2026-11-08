# AJ-C21–C25 — ER guard-counter live-hit probe

Date: 2026-11-07  
Source task: Claude C-1004  
Status: Driver and handoff complete locally; Lead PIE not run by Codex.

## Source contract

`URPGDodgeTiming::NotifySuccessfulGuardContact()` is called by accepted guarded boss contact and stores world time. `OnEldenRingHeavyTap()` checks `RPGGuardCounterRules::IsCounterPress` against `GuardCounterWindowSeconds` (the reflected default is 0.60 s). A successful counter attempt logs `guard counter accepted`; if no GuardCounter montage is assigned, the source keeps the pack strong-attack fallback. `URPGHitIntake::GetRecordLines()` exposes the completed player hit records, whose text includes `kind` and `attack data`.

The probe does not infer a guard from a player montage, unchanged HP, or a boss attack animation. It tails the active project's Unreal log for the exact successful-guard source diagnostic, then sends one R2 press in the same Editor tick that Python observes the written line. That is not an exact contact-to-press measurement; the source's subsequent `guard counter accepted` log is the authoritative proof that its own configured window accepted the press.

## Driver

`Scripts/Editor/pie_er_guard_counter.py`:

- Starts `L_SevarogArena` PIE on the selected route. Set `H019_ENCOUNTER_DEFINITION` before editor startup for the data route; leave it unset for legacy.
- Places the player 220 cm in front of the active `BP_ExampleGreatSwordBoss_C` Ember Warden, leaves the encounter unheld so its AI can attack, and toggles combat with the mapped `R` key.
- Logs whether the boss has an `RPGFrameworkMoveExecutor` component. The only source call sites found for the successful-guard notification are in that executor; component presence is a useful runtime discriminator, but not proof that a guarded hit occurs.
- Holds real `Gamepad_LeftShoulder` (L1) until it reads the successful guarded-contact source log line, then releases L1 and taps `Gamepad_RightTrigger` (R2) immediately.
- Logs boss/player montages, player HP, boss HP before/after, hit count, and the last eight `RPGHitIntake.GetRecordLines()` entries (including attack kind/data). It releases held inputs, unholds the encounter, and ends PIE on completion, timeout, or exception.
- Does not set any component property, assign a montage, save an asset, or claim success when the source guard diagnostic was not observed.

## Lead run and acceptance

Run once per route with the same current saved content and retain the raw PIE log for each. For each run, verify in one evidence set:

1. `[ERGuardCounter] GUARD_CONTACT_CONFIRMED` contains the source's successful guarded-contact line.
2. `[ERGuardCounter] COUNTER_ACCEPT_CONFIRMED` captures the source's counter acceptance log. The script logs that R2 was sent in the same Editor tick as the guard line was observed and reports the configured window; exact physical contact-to-press timing is not claimed.
3. A subsequent player montage identifies the counter clip if one is assigned; absent an assignment, the source's documented pack fallback is expected.
4. The hit-intake record line for the boss hit reports `kind Strong` and `attack data StrongMeleeAttackData`, and the before/after boss HP delta is reported.

A timeout without the source diagnostic is **no verified guarded contact**, not a counter-rule failure. A confirmed guard with no counter-hit record or damage is a failed live-hit result to triage from the paired raw logs. Existing C-1004 air-route results do not count as this guard-counter check.

Owner review of the four clips and Lead assignment of approved montage fields in saved assets remain separate gates. This probe intentionally does not assign the guard-counter montage while owner approval is pending.

## Validation boundary

Static source/API review only. Codex did not run Unreal, PIE, a build, or tests. Python driver syntax/API behavior, the log-file selection in the Lead's Editor session, guarded-contact delivery, and both-route runtime output all remain unverified until Lead execution.
