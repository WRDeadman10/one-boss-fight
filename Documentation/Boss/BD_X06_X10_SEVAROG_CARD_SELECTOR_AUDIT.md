# Queue BD Batch 2: X06–X10 Sevarog cards, traces, and selector

## X06 — authored card rows versus plan

The candidate table in `C1247_SEVAROG_FIRST_FIVE_CARD_PLAN.md` lists S1–S5 proof-card analogs and the standalone fast candidate separately. On-disk project assets exist for five `/Game/OneBossFight/Data/Sevarog/DA_Move_Sevarog_*_C1247` candidates; the accepted draft authoring and profile receipt is indexed at `Docs/BossCombatReview/Execution/Claude/P_C1254_SEVAROGAUTHOR/`. The plan's values and timing rows are candidate data; the status/handoff identifies owner-approved authoring separately from live timing/contact acceptance. S1/S2 live contact is not established by the authored fields.

## X07 — S1/S2 trace boundary

`C1262A_SEVAROG_TRACE_AND_COMBO_DIAGNOSIS.md` records the S1/S2 miss at 140 cm and the later 120 cm S5 hit. The later full-clip cross-check in `BC_A06_A09_SEVAROG_X03_TRACE_CROSSCHECK.md` identifies a Swing1 sample jump from 0.21140 s to 0.45873 s, leaving no Python samples in the 0.267–0.400 s active interval. Swing2's reported closest pass is 37.022 cm capsule-surface distance versus a 15 cm trace radius. The report explicitly flags Swing1 as needing fixed-step recapture before locking a range. These are diagnostic reports, not a new witness or tuning decision; do not reopen their raw logs.

## X08 — combo edges and execution

Existing sources convert profile combo node/edge data into the combo graph (`RPGBossFrameworkProfile.cpp:28–38`). The candidate plan records the S1 Hit→S2 and S4 Whiff→S5 edges; the C-1262 diagnosis reports the tested S4 Whiff→S5 continuation. A profile-level edge and an observed test-driver continuation are different evidence. Do not infer ordinary autonomous selector use from a forced-card test bridge.

## X09 — profile and selector rules

The selector validates candidate cooldown, checks model eligibility, and rejects a card still on cooldown (`RPGBossMoveSelector.cpp:18–56`). The move model rejects phase mismatch (`RPGBossMoveModel.cpp:16–32`). Profile resolution checks phase pool membership and starvation capacity against `AttackCount` (`RPGBossFrameworkProfile.cpp:218–226`), verifies combo nodes resolve to profile moves (`:228–233`), and validates defensive cooldown and damage budget (`:236–241`). This is source-level rule mapping; it does not establish that a production encounter selects this profile.

## X10 — active gates snapshot

- Authored candidate assets/profile: Lead C-1254 status is indexed under `P_C1254_SEVAROGAUTHOR`; do not edit pack-source sequences or `/Game/ParagonSevarog/`.
- S1/S2 contact/range: unresolved; Swing1 trace has a sample gap, and the reports request a properly stepped recapture before tuning.
- S4→S5: C-1262 diagnostic route is documented; distinguish test-driver evidence from autonomous selector acceptance.
- Framework production encounter/HUD/death binding: remains open per `BD_X01_X05_FRAMEWORK_INTEGRATION_MAP.md` and `BB_X26_X30_FRAMEWORK_BINDING_AUDIT.md`.
- Latest captured frame cross-check/report paths can be rechecked from mailbox; raw captures remain immutable.

## Scope

Read-only source and report reconciliation. No raw log/capture contents, content assets, tests, engine, build, PIE, lock, commit, or push operation was performed. Any value decision or runtime retune remains with Lead/owner.
