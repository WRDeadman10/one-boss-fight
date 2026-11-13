# BQ-06..10: Queue BQ batch 2, authoring, executor and audit follow-ups

C (implementer), 2026-11-13. Queue: `QUEUE_BQ.md`.

**Not done:** no compile, engine, editor, tool run, asset change or commit. The C++ change is comments only.

| Task | Result | Files | Evidence |
|---|---|---|---|
| **BQ-06** KI-139 soft-class conversion | **reconciled, no edit.** The cited defect is already fixed in Antigravity's toolkit `Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/authoring_core.py`: `FireballAbility` left `FNAME_PROPERTIES` (:412-415) for `SOFT_CLASS_PROPERTIES` (:418-420), which is checked first (:591-595 via `to_class_ref`). The KNOWN_ISSUES KI-139 citation is stale. The remaining generated-class asset-API load proof is ENG. AG-owned files were not touched | none | source reading |
| **BQ-07** Sevarog executor dry-run skeleton | **deferred to batch 17 (O1-gated), no code.** `sevarog_executor_contract.py` (BK-102: a pure state machine for a future executor) and `plan_sevarog_definition_repair.py` (BK-92/93: a proposal-only planner) already exist with tests (`test_sevarog_executor_contract*.py`, `test_plan_sevarog_definition_repair.py`). A real executor needs the editor `unreal` module and the X-1991 values; a dry-run wrapper would mostly repeat those tests, so it was not built as standalone tooling | none | source reading |
| **BQ-08** finish the BK-116..120 audit | **already complete.** `BK_116_120_RECEIPT_VALIDATOR_ADVERSARIAL_AUDIT.md` exists, the lead hotfix closed six validator gaps (PROJECT_STATE.md:3; TASKS.md:3242-3247), and BK-121..130 build on it. `PROJECT_STATE.md:830` ("still underway") is stale | none | doc reading |
| **BQ-09** KI-136 citations | **done.** `Source/OneBossFight/Player/RPGBossDeath.cpp:126` and `RPGBossDeath.h:31,99` (the death lifecycle: the pack destroys the dead boss) now cite KI-136. `RPGBossDeath.h:137` (the PIE `set_editor_property` hazard) keeps KI-083. The BM-36..40 static pin `Scripts/Tools/test_framework_boss_static_pins.py::Ki136DeathCitations` is updated to assert the new state | `RPGBossDeath.cpp`, `RPGBossDeath.h`, `test_framework_boss_static_pins.py` | `python -m unittest test_framework_boss_static_pins`: OK (static, in-process) |
| **BQ-10** | this report | | |

## Suggested doc refreshes (lead's call; no KI status changes)

- **KI-139:** **done per X-2332.** The KNOWN_ISSUES row now distinguishes the fixed FireballAbility conversion from the still ENG-gated ImmunityEffect/class-load proof. The status is unchanged (open).
- **`PROJECT_STATE.md` BK-111..115 follow-up:** refreshed to record that the BK-116..120 audit is complete and link its accepted report.

## Gates

- **BQ-09** comment changes need no build to be meaningful, but they will compile with the next C-1155 build.
- **BQ-07** waits on O1 (X-1991) plus the editor.

**Batch 2 delivered little new code:** three of its five tasks were already satisfied by earlier work. **Next, batch 3:** BQ-11 (montage notify-track helper), BQ-13 (KI-085 latched input) and BQ-14 (KI-059 dodge characterization).
