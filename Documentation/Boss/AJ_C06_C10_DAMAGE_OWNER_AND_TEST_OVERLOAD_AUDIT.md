# AJ-C06–C10 — C-1003 damage owner and test overload audit

Date: 2026-11-07. Static review of C-1003 plus retained Lead BUILD-249/PIE evidence. Codex did not run tests, edit assets, or operate Unreal.

## AJ-C06 — native test overload review

The first BUILD-249 attempt failed at `TestEqual(FName, NAME_None)` (C2665). Lead changed the unknown-data assertion to `TestTrue(...IsNone())`; the final test source does that at `RPGAutomationTests.cpp:439`. The other new `TestEqual` calls at `:436–438` pass `FName` on both sides; the classification and identity checks compare `int32`. The retained v2 build log says `RPGAutomationTests.cpp` compiled and linked; suite status is 484/484. This review is source inspection corroborated by Lead's log, not an independent build.

## AJ-C07 — damage owner boundary

`RPGHitIntake::FinalizePending` reads the pack hit-data/target AttackData, records the selected table row, and separately applies project posture/bleed and scaler behavior (`RPGHitIntake.cpp:546–646`). The C++ canonical AttackData normalization changes the hit record/table semantics; it does not mutate the `ANS_CollisionTrace_C` notify data consumed by the pack's own damage path. C-1003's two-route result confirms the distinction: classification is now JumpHeavy/posture 38/StrongMeleeAttackData, but the observed HP delta is still -16 versus pack jump+R2 -22.4.

## AJ-C08 — notify property scope

C-1003 supersedes the earlier blanket unset rule for two strong overrides: assign `StrongMeleeAttackData` to the CollisionTrace notify in `AM_ER_Attack_Air_Heavy_Plunge` and `AM_ER_Attack_GuardCounter`; leave AirLight unset. `AA_A08_NOTIFY_FRAMES_TABLE.md` now records this instruction and distinguishes it from A-599's prior export. This is an assigned asset edit, not evidence it has been made; Antigravity owns the edit under ENGINE_LOCK and Lead owns saved-property readback.

## AJ-C09 — status reconciliation

PROJECT_STATE, TEST_PLAN, KI-193 and GATE-07 now mark BUILD-249 classification/native suite as complete, preserve the actual -16 HP result, and keep the expected -22.4 delta pending a fresh probe after the notify edit. The old blanket-unset status and “Lead compile pending” statements are superseded; owner review and package proof remain separate gates.

## AJ-C10 — handoff / acceptance

Antigravity's required asset change: AirHeavy and GuardCounter notify AttackData=`StrongMeleeAttackData`; AirLight remains unset. Lead then reads back all three saved CollisionTrace properties and reruns both routes plus pack controls. Acceptance requires AirHeavy to log JumpHeavy/posture 38/StrongMeleeAttackData and produce the expected -22.4 HP delta; AirLight remains JumpLight/Default and -16 HP. Record actual results and raw logs; do not claim pass before that evidence arrives.
