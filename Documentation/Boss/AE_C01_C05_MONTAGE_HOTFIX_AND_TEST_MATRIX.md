# AE-C01–C05 — Montage hotfix and runtime closeout matrix

Date: 2026-11-07. Static documentation/source/mailbox analysis only. Codex did not edit Source or assets, run tests, launch Unreal, build, cook, package, or run PIE.

## AE-C01 — GuardCounter FootStep disposition

C-992 accepts A-597's Lead readback as a 5/5 table match. C-993 explicitly calls the missing proposed GuardCounter FootStep row cosmetic and says no change is needed. Keep the row as a documented proposal; do not modify the asset or treat its absence as a blocker. This resolves the earlier concern recorded in the AD-C46–C50 report.

## AE-C02 — notify-to-code/test map

| Montage rows | Project-side code and current test coverage | Boundary |
|---|---|---|
| GuardCounter CollisionTrace | Pack trace is documented as the damage source in `RPGTraceGuard.h:11`; hit attribution reads `HitData.AttackData` one frame later in `RPGHitIntake.cpp:529-555`. C-992 requires the notify instance's AttackData unset so ability-provided data is used. | Pack Blueprint notify execution is external; no native test asserts its asset instance properties or live damage. |
| Backstep iFrames / InputBuffer | `RPGIFrameMonitor.h:13,38` observes the pack `ANS_iFrames_C` window; `RPGIFrameMonitor.cpp:39` finds its montage interval. `RPGDodgeTiming.cpp:262` locates the pack input-buffer component. | Monitor/field observation does not prove the saved montage, actual invulnerability, or buffer response; Lead PIE owns those checks. |
| AirLight / AirHeavy CollisionTrace | Same pack trace and `RPGHitIntake.cpp:529-555` data attribution path. `RPGAttackKind.h` and `RPGAutomationTests.cpp:410-419` cover attack-data name classification, including airborne Light/Strong data. | These unit assertions do not exercise montage notify serialization, ability-supplied data, or collision damage. C-992's live 0-damage PIE is authoritative for the defect. |
| AirLight / AirHeavy MovementCancel, DisableMovement, InputBuffer | No project C++ handler for these pack notify classes was found in the searched player/source tree. | Pack behavior remains external; runtime state/input effects require Lead PIE. |
| ParryRecoil InputBuffer | `RPGSevarogDirector.cpp:244-252` plays the optional boss recoil montage; caller is `RPGPlayerParry.cpp:161`. | No project test verifies the montage notify's input-buffer effect. It is not a hit/damage or i-frame proof. |

`RPGMontageUtilsTests.cpp:16-65` covers montage segment range editing, length recomputation and dirtiness; it does not inspect notify types, properties or timing. No native assertion currently verifies `AttackData=unset` on the three attack montage CollisionTrace instances.

## AE-C03 — Lead PIE matrix after A-597 re-authoring

Lead runs each row on an identified current build, on both legacy and selected-data routes, with held boss and player 160 cm from target as in P_C992_AIRHITS. Preserve raw log, build ID, route, montage position, before/after boss HP, `HitIntake` line and asset/t3d identity. Use same actor/weapon/health reset for each paired case.

| Case | Input and asset | Required evidence to pass |
|---|---|---|
| GuardCounter damage | Successful guarded contact, then counter input; `AM_ER_Attack_GuardCounter` | CollisionTrace opens; target HP decreases; hit log reports ability-provided AttackData; exported CollisionTrace has no AttackData override. |
| Backstep invulnerability/buffer | Dodge input; `AM_ER_Backstep_Back` | i-frame window matches notify interval; an otherwise valid incoming hit during that window is ignored; buffered follow-up is observed; yaw remains locked. |
| AirLight hit | Jump + R1; `AM_ER_Attack_Air_Light` | Airborne hit reduces boss HP and hit log has valid ability-provided data; trace interval 0.200–0.333 s, montage blend-in 0.100 s, MovementCancel begins at/after 0.333 s. |
| AirHeavy hit | Jump + R2; `AM_ER_Attack_Air_Heavy_Plunge` | Airborne hit reduces boss HP and hit log has valid ability-provided data; trace interval 0.367–0.533 s, MovementCancel begins at/after 0.533 s. |
| ParryRecoil buffer | Successful parry; `AM_Boss01_ParryRecoil` | Boss recoil montage starts; input-buffer response is observed/logged independently of the player's counter input; no damage claim is inferred from this notify. |

For each case record PASS/FAIL/INCONCLUSIVE separately. Compare to same-route pack control; do not require the exact 16/22 control damage value from a different run. A successful saved-asset check alone is not runtime acceptance. C-992 requires Lead to rerun the air-hit test after Antigravity's 3-asset re-authoring.

## AE-C04 — owner decision status

Mailbox through C-993 contains no owner visual approval, optional-field assignment, or Phase 2 unpark decision. C-968/C-972/C-977 report clip delivery/acceptance for owner review; C-985 accepts Tier 2 previews for owner review; C-992 accepts the saved-asset readback but reports a live damage fail; C-993 clarifies FootStep as cosmetic. Delivery, Lead readback, owner approval, assignment, runtime and package status remain separate.

## AE-C05 — release evidence closeout and next receipt

Open gates: three asset re-authorings per C-992 (GuardCounter, AirLight, AirHeavy); Lead post-authoring readback/t3d proof that CollisionTrace `AttackData` is absent; Lead re-run of air hit test; other notify-dependent PIE; owner clip/preview review and any assignment; current build/cook/stage/package and gameplay capture. Phase 2 remains parked by C-954. A-597's 426 OK / 1 skipped / broken_links=0 remains mailbox-reported only because no raw suite summary was attached.

Queue AE-C01–C05 is complete. Next five-task lane is `Documentation/Boss/QUEUE_AF.md` (AF-C01–C05); validate the queue IDs before work begins. No release gate was closed due to missing evidence.
