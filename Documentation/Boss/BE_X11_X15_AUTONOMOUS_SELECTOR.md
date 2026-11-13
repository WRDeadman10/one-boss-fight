# Queue BE Batch 3 — autonomous selector test route

Date: 2026-11-10  
Status: source READY; Claude owns live route, HUD/retry, and saved-map acceptance.

## Delivered

- Added a development-only `StartSelectedCardForTest()` seam. It calls the production selector against the initialized executor model and current phase snapshot, accepts no caller-supplied card ID, records chosen move/phase/generation, and fails closed for no-candidate, selection failure, or start refusal. The existing forced-ID test entry remains separate.
- Added a bounded opt-in branch to `pie_sevarog_framework_live.py` (`SEVAROG_LIVE_AUTONOMOUS=1`). It starts at most one selector-chosen card, polls the boss outcome, caps runtime to 5–90 seconds, records terminal or timeout status, and unregisters its tick callback / ends PIE. It does not call the forced-ID entry or save assets. The existing default live driver path is unchanged.
- Preserved selector no-candidate/cooldown coverage and added a native health/HUD presentation test for current-generation terminal acceptance, duplicate/stale callbacks, victory predicate, and retry visibility delay/invalid clock behavior.
- Added an offline contract to pin the id-free selector call, bounded no-save driver behavior, and existing selector/terminal regressions.

## Validation

- `test_be_x11_x15_autonomous_selector_contract.py`: 3/3 passed.
- `py_compile` for the live driver and contract: passed.
- `test_check_shipping_guards.py`: 4/4 passed.
- C-1155 Development build: exit 0. DD27j-pinned full suite: 508/508 started and passed, 0 failed, complete. `OneBossFight.BossHealth.PresentationSnapshot` passed. No assets. Both locks released.
- Receipt: `Docs/BossCombatReview/Execution/Codex/BE_X11_X15_AUTONOMOUS_SELECTOR/Run_20261110_175316/`.

## Acceptance boundary

No PIE or map-selected framework route was run. The default route remains unchanged and framework selection remains opt-in/default-off. Native tests cover the HUD terminal callback acceptance and retry timing rule, but do not establish a full live player death → visible retry prompt → reload/new-generation sequence on the selected route. Claude's live route and saved-map acceptance remain required for that claim.

The driver is a bounded route witness, not an automated retry/reload verifier: it records the selected card and waits for an outcome or time cap, then ends PIE. It makes no save or packaged-behavior claim.
