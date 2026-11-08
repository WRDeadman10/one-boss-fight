# C-1044 project A4 guard-contact hotfix

**Later C-1045 validation:** Lead accepted this Source change, BUILD-259 passed 485/485, and both-route PIE proved real A4 `Blocked`, counter arm, R2 acceptance and GuardCounter montage play with no player HP loss. Boss HP remained 2000 at a 250 cm starting distance; the C-1045 140 cm probe is the remaining damaging-hit gate. The unbuilt language below records the original X-1473 handoff state.

**Route provenance correction (C-1099):** the nominal legacy and data arms in `P_C1043_A4COUNTER` were both DATA-default because the legacy arm did not set `RPG_LEGACY_STARTUP=1`. C-1047's accepted real-block/counter/HP observations therefore apply to the tested DATA-default PIE case only; they do not establish legacy parity. Package proof remains open.

## Evidence and decision

Lead C-1044's clean two-route A4 probe observed `Status.Blocking=1`, active `GA_PlayerGuardBlock`, and one real low-sweep contact, but no `GA_Sword_BlockReaction` and no counter arm. `URPGBossLowSweep` sends its contact to `URPGDamageResolver`, which writes health directly and never invokes the pack's weapon-trace block reaction. The archived M2 damage spec treats A4 as blockable by default and lists a future `Blocked` outcome; no current decision declares A4 unblockable. The new path therefore opts in **A4 only**. A5/A6 and other resolver clients keep their existing policy until separately decided and tested.

## Change

`FRPGDamagePayload::bCanBeBlocked` defaults false; A4 sets it true. After existing dead/stale/duplicate/dodge/parry precedence, a real player target with `Status.Blocking` produces `Blocked`. It spends the hit, leaves health unchanged, and calls that player's `URPGDodgeTiming::NotifySuccessfulGuardContact` once. The sweep ends after the block. A duplicate, dodge i-frame, parry, or non-player target cannot arm through this path. This is a zero-chip A4 block; the archived stamina/reduction model is unimplemented and remains a separate design gate. The probe still must show real arm, R2 acceptance, counter montage, and boss HP decrease on both routes.

## Validation and Lead handoff

Expanded native `OneBossFight.Combat.DamageResolver.Decide` assertions cover guarded, unguarded, unblocked, dodge, parry, duplicate, and stable `Blocked` name. Source diff check passed. **Source is unbuilt; no PIE verdict is claimed.** Lead closes the editor, builds, runs native suite, then reruns:

```powershell
& ./Scripts/RunLeadPie.ps1 -Script Scripts/Editor/pie_er_a4_guard_counter.py -Routes @('legacy','data') -OutputDir Docs/BossCombatReview/Execution/Claude/P_C1044_A4_GUARD
```

Expected log sequence: A4 `Blocked (Status.Blocking)` and `successful guarded contact armed guard counter window`, then `guard counter accepted after successful block`, observed `AM_ER_Attack_GuardCounter`, and boss HP decrease. KI-198 stays open until that sequence passes on both routes.
