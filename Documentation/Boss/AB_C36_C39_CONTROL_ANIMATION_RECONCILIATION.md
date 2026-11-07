# Queue AB AB-C36–C39: controls, animation evidence, lifecycle and terms

Mailbox evidence checked through C-977, A-588. This is a static reconciliation; no UE build, Editor, PIE, asset assignment, or owner video review was performed.

**Subsequent mailbox update:** C-978 confirmed the air-restore probe passed on both routes. A-589/C-979 report Backstep and GuardCounter montage trims; A-590 reports both air montage trims match accepted lengths. Owner review remains distinct from delivery acceptance. The importer status-gate hotfix requested in C-979 is recorded in X-1383.

## AB-C36 — canonical control map and discrepancy resolution

| Control | Canonical mapping / runtime route | Evidence and current limit |
|---|---|---|
| Dodge | `Gamepad_FaceButton_Right` (Xbox B); tap routes through pack dodge; optional empty-default `BackstepMontage` handles a standing tap only when assigned | `ER_INPUT_DUMP/run1/editor_raw.log:1285`; `RPGDodgeTiming.cpp::OnDodgePressed`; live optional animation/owner approval pending |
| Sprint | Same face button hold; pack sprint action | input dump `:1286`; do not label it a long roll |
| Jump | `Gamepad_FaceButton_Bottom` (Xbox A) | input dump `:1294` |
| Guard | L1 = `Gamepad_LeftShoulder` (Xbox LB), pack `IA_Block` | input dump `:1290`; mapping alone does not prove a successful block (AA-C06) |
| Parry | L2 = `Gamepad_LeftTrigger` (Xbox LT), pack `IA_Parry` | input dump `:1307`; distinct action from guard |
| Light | R1 = `Gamepad_RightShoulder` (Xbox RB) -> `IA_ER_Light` press -> light; falling may use optional `AirLightMontage` | `ER_INPUT_DUMP/update2/editor_raw.log:1309`; C-975 runtime-only route test; grounded-after-air restore still needs `pie_er_air_restore.py` |
| Strong / charged | R2 = `Gamepad_RightTrigger` (Xbox RT); `IA_ER_HeavyTap` tap -> strong, hold -> charged | mapping readback `update2/editor_raw.log:1310-1311`; C-945 PIE; falling strong may use optional `AirHeavyMontage` |

Source names the optional air fields and empty-default behavior in `RPGDodgeTiming.h`; `TickEldenRingInput` temporarily overrides the applicable pack arrays only when the optional montage is used. C-975 initially omitted the post-air check; C-978 reports Lead PIE then confirmed grounded R1=Attack_PrimaryA and R2=Ability_E after both air cases, on both routes. The maintained ER spec and owner hand-test sheet now use this mapping and exact pending gates.

## AB-C37 — accepted delivery vs owner decision

“Accepted for owner review” means Claude accepted the delivery/import gate; it does not mean the owner approved the animation feel. No owner review result appears through C-977.

| Clip | Mailbox-backed state | Remaining gate |
|---|---|---|
| ER-A1 Backstep R7 | C-977 accepted for owner review; A-588 confirms imported sequence and `AM_ER_Backstep_Back` | Owner video review and field assignment; C-977 says strip shows backward stride, planted feet, arms close, sword pointing straight up with tip out of frame. Do not repeat A-587's contrary “forward/down” description. C-978 further notes montage is 0.8667 s and needs trimming to the 15f/0.467 s clip range. |
| ER-A2 Air Light R4 | C-972 accepted for owner review; A-585 import and montage are reported | Owner video review and optional field assignment |
| ER-A3 Air Heavy Plunge R4 | C-972 accepted for owner review; A-585 import and montage are reported | Owner video review and optional field assignment |
| ER-A4 GuardCounter | C-968 accepted for import only; A-584 records source length 1.6667 s and accepted slice F10..F34 (0.8000 s); A-588 says montage exists | Owner video review, Antigravity trims under lock using BUILD-248 helper to 0.3333..1.1333 s and reads back 0.800 s, then field assignment after owner approval |

All four saved optional runtime fields remain empty. C-977 explicitly directs the owner review for all four clips.

## AB-C38 — player death/reset during an active attack montage

| Event/owner | Source behavior established here | Test coverage / conclusion |
|---|---|---|
| `URPGDodgeTiming` teardown | `EndPlay` restores any temporary attack-array override and clears the successful-guard timestamp (`Source/OneBossFight/Player/RPGDodgeTiming.cpp:40-46`). It does not explicitly stop an active attack montage. | `RPGAutomationTests.cpp:1192-1195` checks optional montage defaults; `RPGGuardCounterRulesTests.cpp:11-40` checks a pure timer rule. Neither covers player death/reset while a montage is active. |
| Encounter reset | `RPGDodgeTiming.cpp:40-46,65-70,419-427` has teardown and tick routes but no encounter-reset subscription/handler; attack montage lifecycle remains owned by pack ability/animation systems. | No Source test proves montage cancellation or array restoration on a live player reset. |
| Player death | No health/death observer or explicit player-death montage cancel was found in `URPGDodgeTiming.cpp:40-70,419-526`. A pawn destroyed as part of death would take EndPlay, but that does not establish behavior for a surviving/dead pawn. | No test establishes whether pack death interrupts, preserves, or restarts an in-flight player attack montage. Treat as unverified; do not infer from boss death components. |

The present evidence supports a coverage gap, not a confirmed runtime bug. Lead-owned PIE should record pawn survival/destruction, active montage before/after, temporary-array values, reset/death route, and EndPlay log/callback for each scenario before promising cancellation behavior.

## AB-C39 — owner-facing terminology

| Term | Use it for | Avoid conflating with |
|---|---|---|
| Guard / block | Hold L1; “successful guarded contact” only after the resolver reports an actually guarded contact | Parry or merely holding L1 without contact |
| Parry | Timed L2 action (`IA_Parry`) | Block/guard |
| Guard counter | One R2 tap after successful guarded contact, within the configured runtime window; 0.60 s is a proposal, not owner-approved tuning | Any R2 after holding guard or a parry |
| Light | R1 press (`IA_ER_Light`) | R2 strong |
| Strong | R2 tap (`IA_ER_HeavyTap`) | Charged R2 hold |
| Charged | R2 hold; mapping asset uses a hold trigger | Strong R2 tap |
| Backstep | Optional standing no-direction dodge montage when assigned; empty field preserves pack route | Moving dodge roll or sprint hold |

