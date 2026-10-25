# E-005 A2 slam stopped before its damage window (CI-P0-C-01), 2026-10-25

Status: OBSERVED PATTERN, CAUSE NOT IDENTIFIED. Bot-driven runs (existing driver unchanged, Starter build, `rpg.WakeClip` 1, `rpg.CloseTelegraph` 0.4, `rpg.Legend` 0, about 33 fps, window restored; see E-004 for the harness and its limits). A2 = `GA_GS_Boss_CloseRare` playing `GS_ChargedAttack_Montage` (3.4 s; tracker row: commit 1.68 s, damage window 1.93 to 2.11 s, recovery end 3.14 s).

## Data (tracker log lines `attack A2 instance N ended (montage stopped) at X s, phase was P`; world time of the nearest preceding player hit on the boss from `LogRPGHitIntake`)

| Run | Instance | Stop at montage time | Phase at stop | Last hit on the boss before the stop |
|---|---|---|---|---|
| A2 defaults (05:44 UTC) | 1 | 0.06 s | Windup | 0.49 s |
| A2 defaults | 2 | 0.97 s | Windup | 2.47 s |
| B warm (05:47) | 1 | 0.03 s | Windup | 0.15 s |
| B warm | 3 | 1.00 s | Windup | 2.03 s |
| B warm | 4 | 2.80 s | Recovery (normal end region) | 0.06 s |
| T1 trace (defaults) | 2 | 0.98 s | Windup | 1.98 s |
| T1 trace | 3 | 0.97 s | Windup | 1.59 s |
| T4 trace (08:36) | 1 | 0.06 s | Windup | 0.52 s |
| T4 trace | 2 | 1.99 s | Active (window open) | 1.64 s |
| T6 trace (08:40) | 1 | 0.06 s | Windup | 0.52 s |
| T9 trace + montage log | 1 | 0.06 s | Windup | not extracted |

Reading (counts of today's valid runs, one bot, not a frequency estimate): in 5 of the 6 fights in which an A2 occurred, the first A2 of the fight stopped 0.03 to 0.06 s after it started (A2 defaults, B warm, T4, T6, T9; instance numbers differ because the counter includes other moves); in the sixth (T1) the first A2 stopped at 0.98 s. Other A2 instances stopped at 0.97 to 1.00 s (4 times in total with that one), at 1.99 s (once, inside the open damage window) and once ran to its normal recovery end. Only 1 of 11 instances reached recovery; none was observed to complete its damage window with a hit on the player (`attacks_seen` of the runs: A2 "missed on its own"). The 10-24 runs (mutable saved log lines, not re-run) show the same family: windup stops at 0.68 and 1.35 s, stops at the commit moment 1.69 and 1.70 s, one full recovery at 3.0/3.14 s.

## What the traces show (probes/p0_montage_trace.py, T4; exports `natural_sample_T4_trace_defaults.txt`)

- Instance 1 (T4): the montage plays for two ticks (position 0.030), then `playing=False stopped=True current=None`; the boss ability system still lists `GA_GS_Boss_CloseRare_C` as activated AND as the animating ability on every one of the next 46 ticks (1.4 s, trace limit) with no montage playing. So the move is cut but the ability does not end for at least 1.4 s (it ended before the next A2 started 3.1 s later; exact end time not captured).
- Instance 2 (T4): the montage plays normally to 1.44 s (end of the 48-tick trace); the tracker later logged the stop at 1.99 s in the Active phase.
- The behavior-manager `CurrentState` object logged during all ticks is the base class `SM_Behavior_C`: the state TAG is not readable this way; the state-change hypothesis (BT service `S_UpdateBehavior`, 1.0 s) is therefore NOT confirmed. The 0.97 to 1.00 s group is phase-locked to the A2 start, not to world time, which also argues against a free-running 1 s service; the cause of that group is open.
- T9 (engine log `LogAnimMontage` at VeryVerbose, 74,151 lines in `natural_sample_T9_trace_animlog.txt`): at the instance-1 stop the log shows `Montage.Stop Before/After: AnimMontage: GS_ChargedAttack_Montage (DesiredWeight 1.00 -> 0.00, Weight 0.24)` while `GS_EquipWeapon_Montage` (the boss's enter-combat montage) is still blending out (weights 0.63, 0.51, 0.39). The log does not name the caller of the stop.
- No native code of this project can be the caller: the only `Montage_Stop` sites are the tracker's veto and branch check (each logs `vetoed`/`denied by the branch check`, none was logged), death, wake, encounter reset, phase transition, stance break and the retired director; no hit reaction montage played (the boss's `current` montage stays None); no encounter reset happened. Pack Blueprint exports searched (19 assets, `exports/BPX_*.t3d`): no direct `Montage_Stop` call node in them.

## Consequence and open items

- A2 as played is not the move the tracker table and the Freeze describe: most slams never reach their damage window, and a cut slam leaves its ability active for over a second, which blocks the next pack attack (`Can Activate Ability?` rejects while the ability is active/animating, E-002 Addendum 3) and can look like the boss standing idle. This bears on audit rows for attack reliability, finalisation and recovery, and on DD-1: behaviour-identical migration must either reproduce this cut or the owner must approve a corrected behavior first.
- Not known: who stops the montage; why the first A2 after the equip montage was cut in 5 of 6 fights; whether the ~1 s group has a different cause. Candidates not yet tested: the pack ability's own end handling (`PlayAbilityMontageAndWaitForEvent` completion/interrupt branch), the behavior-tree abort (`OnAbortCurrentBehaviorTask`), state exit of `Character.State.Attacking`, the EnterCombat ability end.
- Smallest next evidence without changing gameplay code: read the edge-level graphs of `GA_Attack`/`GA_MeleeBase` event graphs and `PlayAbilityMontageAndWaitForEvent` (E-006); if that does not name the caller, a minimal Development-only diagnostic (log a script callstack from `UAnimInstance::Montage_Stop` for the boss mesh) is proposed to the owner as a P0 extension; not implemented, not authorized.
