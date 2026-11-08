# AJ-C11–C15 — C-1003 saved asset evidence audit

Date: 2026-11-07. Independent static review of Antigravity's A-607 saved-asset evidence. Codex did not operate Unreal or modify any assets.

## AJ-C11 — Strong AttackData on the two strong overrides

The raw T3D exports are present under `Saved/C1003_t3d/`. In `AM_ER_Attack_Air_Heavy_Plunge.t3d:13–16`, `AttackData=StrongMeleeAttackData` is inside the `ANS_CollisionTrace_C_1` subobject. In `AM_ER_Attack_GuardCounter.t3d:26–29`, the same property is inside its `ANS_CollisionTrace_C_1` subobject. This matches C-1003's two strong-kind asset instructions.

## AJ-C12 — AirLight remains unset

`AM_ER_Attack_Air_Light.t3d` contains an `ANS_CollisionTrace_C_1` subobject and an active `Notifies(1)` trace at 0.150 s for 0.186 s; the file has no `AttackData` line. This matches C-1003's AirLight requirement and leaves data selection to the ability.

## AJ-C13 — Lead asset-check readback

`C1003_LEAD_CHECK.txt` reports GuardCounter 0.8000 s, Backstep 0.4667 s, AirLight 0.6000 s, AirHeavy 0.8667 s, and ParryRecoil 0.6000 s. Those values agree with the C-1003 saved-asset check request. The report is a montage/config readback; it is not the pending hit-damage PIE rerun.

## AJ-C14 — status refresh

AA-A08, GATE-07, KI-193, TEST_PLAN, PROJECT_STATE and TASKS now mark A-607's saved-property edit/readback complete: Strong on AirHeavy and GuardCounter; unset on AirLight. The remaining acceptance is runtime behavior, especially the expected AirHeavy HP delta.

## AJ-C15 — Lead runtime close condition

Lead reruns the existing `P_C992_AIRHITS` on both routes, with the pack jump+R2 control on each. Keep the raw logs and confirm the hit records still report JumpHeavy/posture 38/StrongMeleeAttackData. The expected control and AirHeavy damage are -22.4 HP; AirLight should remain -16 HP. Report measured values; the T3D proof alone does not close KI-193.
