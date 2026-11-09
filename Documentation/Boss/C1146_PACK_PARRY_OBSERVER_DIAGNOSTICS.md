# C-1146 Pack parry observer diagnostics

Date: 2026-11-09  
Status: Diagnostic Source update ready for Lead BUILD-272 and parry-close rerun. Codex did not build or run Unreal.

## Trigger and question

Lead's BUILD-272 v3 compiled, with 490/491 native tests passing; the sole failure was the separate KI-177 `StanceBreakPendingState` fixture. In the DATA parry-close run (Tier 2 enabled, 90 seconds), Lead observed 26 presses, `ParriedCount=0`, and no `LogRPGPackParryContact` output. The original observer therefore provided no evidence whether it resolved the pack target, saw an active trace, or observed the player in `HitActors`.

The diagnostic pass leaves the approved candidate/reward decision unchanged. Lead's next run must answer whether the pack inserts the player into `HitActors` when `SM_ImpactDecision` considers a hit parried. If not, the hook location needs redesign from observed evidence.

## Added read-only diagnostics

- Target resolution reports resolved/unresolved plus target/collision component names once per state or object change.
- Trace activity reports rising/falling edges, current target name and HitActors count.
- Each newly observed player insertion reports current/previous native parry-window state, invulnerability/health query availability and values, grade, wall-seed and carried status.
- Early-outs have reason-coded Display messages, rate-limited to one per reason per game second. Candidate and final outcome messages remain.
- Reflected invulnerability/health reads occur only when an active trace contains a new player insertion; they are not performed every idle tick.

The KI-177 transient harness now starts from the authored `DA_Sevarog_SelectorProof_F5` profile so its posture mutation is evaluated against an F5 selector-lane profile. The five configured posture values remain within `ValidateProfile`'s F5 rules; the failure fix still needs Lead BUILD/native test confirmation.

## Validation

- `python -m unittest Scripts.Tools.test_pack_parry_contact_contract -v`: 8/8 passed.
- `python -m py_compile Scripts/Tools/test_pack_parry_contact_contract.py`: passed.
- Scoped `git diff --check` on the changed Source/test files: passed; Git printed only a line-ending normalization notice for the pre-existing KI-177 test file.
- No UHT/C++ build, native automation, Editor, PIE, or parry-close run by Codex.

## Lead follow-up

After rebuilding, inspect `[PARRY] observer_target`, `trace_edge`, `hitset_insert`, and `skip reason=`. If a parried swing causes a player insertion, the reason identifies which approved candidate predicate rejected it. If contacts occur but no player insertion is logged while the target is resolved and active, `SM_ImpactDecision` likely prevents insertion and a native overlap candidate hook must be designed. Keep runtime claims pending until those logs and the expected per-attack reward/Tier 2 recoil are observed.
