# C-1280 X26 — Sevarog phase eligibility and transient validation

**Status:** Codex implementation and transient validation READY for Lead review. No Sevarog assets were saved; the C1278 live acceptance table remains a separate Lead run.

## Implemented

- Added optional `FRPGBossMoveCardSpec::AdditionalPhaseIds` in `RPGBossMoveCard.h:115`. Empty preserves prior single-phase eligibility; validation rejects `None`, the primary phase, duplicate entries, and more than four entries (`RPGBossMoveCard.cpp:28-65`).
- Model selection accepts a card in its primary or additional phase (`RPGBossMoveModel.cpp`); profile phase validation and starvation pools count each card in every eligible phase (`RPGBossFrameworkProfile.cpp:230-250`).
- Added a conservative per-card damage budget for direct damage, enabled area damage, and channel tick damage (`RPGBossMoveCard.cpp:30-49`). Profile damage acceptance and the repeated-attack survival budget use that total (`RPGBossFrameworkProfile.cpp:197-200,224`).
- Pure ChannelDrain-only cards bypass the strike-recovery walk-in gate only when authored counterplay exists: a cone narrower than 180 degrees or fixed facing. The profile log prints `recoveryGate=ExemptConeEscape` or `ExemptFixedFacing`; a full-cone tracking channel remains gated (`RPGBossPunishRules.h:13-18`, `RPGBossFrameworkProfile.cpp:277-284`).
- Sevarog authoring data keeps S1–S5 and S7 eligible in Phase 1 and Phase 2; S6 and S8 are Phase 2. S8 uses the C-1280 cadence: five 8-damage ticks at 0.467, 0.667, 0.867, 1.067, and 1.267 seconds with 0.50 heal fraction.
- Applied the BE-X22 Shipping guard to `CVarBossProofSkipInitialWalk` in `RPGFrameworkBossCharacter.cpp:151-160`. The repository scan also found `CVarBossProofTraceGeometry` declared for Development but read in Shipping; its read is now development-guarded in `RPGFrameworkMoveExecutor.cpp:359-369`.

## Verification

- `python Scripts/Tools/test_check_shipping_guards.py`: **4/4 passed**, zero Shipping-visible uses remain.
- `python Scripts/Editor/test_author_sevarog_draft_cards_contract.py`: **13/13 passed**.
- `python -m py_compile Scripts/Editor/author_sevarog_draft_cards.py`: passed.
- C-1155 task runner `Scripts/Editor/run_c1280_x26_locked_validation.ps1`: **BUILD_EXIT=0**, **EDITOR_EXIT=0**, transient dry-run PASS, **NO_SAVES=True**, pinned suite **507/507**, `FAILED=0`, `COMPLETE=True`, phase validator/model/pool tests all passed, and **LOCKS_RELEASED=2**. The S8 validator log records `recoveryGate=ExemptConeEscape` for its approved 45-degree, fixed-facing channel. Pinned DD27j manifest: `cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec`.
- The native suite includes `OneBossFight.Framework.MoveCard.DamageBudget`, `OneBossFight.Framework.MoveCard.Rejections`, `OneBossFight.Framework.MoveModel.Eligibility`, and `OneBossFight.Framework.Runtime.SelectorProfile`.
- Receipt directory: `Docs/BossCombatReview/Execution/Codex/C1280_X26_PHASE_ELIGIBILITY/Run_20261110_165108/` (build, dry-run, suite, status, and lock-release receipts).

## Remaining acceptance

Claude owns live checks against `C1278_X26_LIVE_CHECK_ACCEPTANCE_TABLE.md`, including phase refusal/unlock, S6 single-hit behavior, S7 area/snare resolution, and S8 five-tick cadence/cone escape. This report does not claim those PIE checks passed.
