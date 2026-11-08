# AJ-C36–C40 — owner and runtime acceptance boundary

Date: 2026-11-07  
Source: C-1004, ER hand-test sheet, GATE-07, AA-A08, and current guard-counter source.  
Status: Read-only reconciliation; no Editor/runtime work.

## Acceptance layers

1. **Owner-visible guard test:** `ER_HAND_TEST_SHEET.md` requires positive player health/stamina, a front-facing incoming strike, L1 held through a visibly blocked contact, and before/after health, stamina, and player animation. Its guard-counter row explicitly requires owner clip review, field assignment, and Lead build before expecting the assigned counter montage.
2. **Counter source test:** `pie_er_guard_counter.py` verifies the ER input context, records whether the arena boss exposes `RPGFrameworkMoveExecutor`, waits for the source's successful-guard diagnostic, taps R2 in the same editor tick that it observes that line, and then requires the source's counter-accepted diagnostic. This is useful live instrumentation; absence of the hook remains inconclusive until the active boss route is established.
3. **Hit result:** after a source-accepted counter, the probe records the player hit-intake rows, their `kind`/`attack data`, count, montage, and boss HP before/after. A saved montage property readback alone does not establish this hit result.
4. **Clip and assignment gates:** C-1004 says the owner must approve the four clips before Lead assigns their fields in saved assets. A-607's StrongMeleeAttackData on the GuardCounter notify is saved-property proof only. The probe does not assign the field and cannot close the owner or saved-asset gates.

## Consequence for result labels

- No component/contact diagnostic: **no verified guarded contact**; do not classify as a guard-counter failure.
- Guard diagnostic but no counter-accepted source line: **counter input/rule not accepted or not observed**; retain the raw log and route identity for Lead triage.
- Counter accepted but no Strong record/HP delta: **live-hit result not demonstrated**; use record, montage, and trace logs to locate the next boundary.
- Matching record/data/HP result on both routes: closes only the live counter-hit check for the tested build/content. Owner visual approval and saved montage assignment remain separately tracked until actually completed.

## Evidence sources and limits

`ER_HAND_TEST_SHEET.md` v2 records the manual setup and prior probe classification. `GATE07_ANIMATION_REVIEW.md` and `AA_A08_NOTIFY_FRAMES_TABLE.md` track authored/readback montage data and their own scope. C-1004 confirms the prior two-route air-hit result and separately leaves guard-counter live hit and owner review open. No current source here supplies a Lead guard-counter PIE result. Codex ran no tests, Editor, PIE, build, or asset operation.
