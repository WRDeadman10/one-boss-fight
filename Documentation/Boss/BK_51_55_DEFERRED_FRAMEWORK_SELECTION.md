# BK-51..55 — deferred framework selection

Claude assigned BK-3 in C-1295 after BK-46 READY. This source batch authors the framework encounter definition on explicit request, provides a test-only deferred activation path for a begun PIE world, and makes the BF-X05 receipt verify that deferred order. It does not change the configured startup route or the default-off framework selector.

## Changes

- `Scripts/Editor/author_framework_encounter_definition.py`: validates the existing Sevarog typed boss definition, Hero V3 typed player definition, framework profile and `Phase_1`; computes a deterministic SHA-256 over sorted canonical selection fields (excluding random EncounterInstance); dry-runs by default and saves a new asset only with `--write`; refuses overwrite and reads back the authored references/flags/hash.
- `RPGFrameworkBossCharacter::InitializeSelectedEncounterForTest`: narrowly accepts an already-begun actor/player in a standalone game world when the exact transient binding owns both participants. The regular production initializer still rejects begun actors. Shipping returns false and the reflected test method is absent under `WITH_EDITORONLY_DATA`.
- `URPGPlayerMovesSubsystem::ActivateDeferredSelectionForTest`: Shipping false; in non-Shipping requires a begun standalone world, explicit definition, selector opt-in and exact framework census. It can release a current transient activation lease for the test replacement, activate through the rebind preparation path, initialize the selected boss, and attach player diagnostics/HUD/music.
- `URPGEncounterSelectionSubsystem::GetForWorld`: editor-only reflected accessor needed by the Python live driver.
- `pie_sevarog_framework_live.py`: after pack-style readiness and PIE-only pack-boss isolation, spawns the transient actor, clears any stored selection, sets the encounter path and framework opt-in CVars, and calls the deferred activation hook. It fails closed if the asset or bridge is absent.
- `verify_bf_x05_selected_route.py` and its synthetic tests: FW-01 now requires pack-isolated-before-spawn, framework-spawn-before-selection, flag 1, matching definition path, and `Activated` result.

## Verification and limits

- `test_bk51_bk55_framework_deferred_selection_contract.py`: 4/4.
- `test_bk3_bf_x05_verifier.py`: 13/13.
- Antigravity A-830 found the Shipping-reflection contract allowlist omitted the new editor-only actor initializer. Updated `test_bf_x11_x15_shipping_reflection_contract.py`; its three tests now pass, including guard and definition-parity checks. Combined focused batch/verifier/reflection contracts: 20/20.
- `py_compile` passed for the changed author/driver/verifier/test Python files; `check_doc_links.py` reports `broken_links=0`.
- Unreal C++ compilation, saved asset readback, and live route evidence are not yet verified in this batch. The engine remains held by the C-1295 instruction until Claude releases it again. The authoring script has not been run with `--write`; no content asset was saved.
- The verifier remains a receipt predicate checker, not a raw-log authenticity checker. Runtime acceptance remains Lead-owned.

No commit or push.

## A-831 follow-up hotfixes (2026-11-11)

- UHT rejected the reflected `const ARPGEncounterBinding&` argument. `InitializeSelectedEncounterForTest` now takes `const ARPGEncounterBinding*` and validates it before use.
- The live driver now gates deferred asset loading/activation behind `SEVAROG_LIVE_DEFERRED_SELECTION=1`; default X26 profile arms retain the existing standalone path when the encounter asset has not been authored.
- The X26 log verifier now accepts the expected `before_initialize` + `before_request` setup pair when S6 is the first card, while rejecting duplicate `before_request` rows.
- Focused checks after the hotfixes: deferred-selection contract 5/5, Shipping reflection 3/3, X26 live-log verifier 15/15, and BK2 driver contract 9/9. No build, Editor, PIE, asset save, or receipt/log edits were performed. C-1297 bars engine use pending Claude's BUILD-299 analysis.
- S8's five accepted 8-damage ticks report `bossHealed=0`; this remains a Lead investigation item. See A-831 and X-1953 in the mailbox.

## Lead read-only gate audit (2026-11-11; X-1981)

The deferred live route is not ready to claim as a production selected-route acceptance. `InitializeSelectedEncounterForTest` currently passes `bAllowDevTest=true` to `InitializeProofInternal`, which sets `bTestInitialized=true`; native actor Tick then returns before autonomous production selection (`RPGFrameworkBossCharacter.cpp:89-116,162,708-710`). The driver uses `start_selected_card_for_test()` in its autonomous branch and Phase_2 probes (`pie_sevarog_framework_live.py:309-310,322-324`) and `start_combo_for_test()`/`start_card_for_test()` in the regular path (`:809,813`). A-841 independently confirms this violates C-1298 for the deferred arm. X-1983 assigns Claude BK-56..60: deferred-only production-Tick path, contract coverage, authored definition/readback, bounded no-save PIE, and status handoff. The BK-3 live acceptance remains open until that batch is addressed and run; the standalone X26 results above are unaffected.

## A-832 S8 healing diagnosis

Antigravity traced the zero healing to the standalone card health hook, not to `ReadNativeHealth`: the first S6 card consumes `bTestHealthOverridePending` while preserving 125/250; starting S8 then resets the boss to full health, so `CappedHeal` correctly returns 0. For a healing witness, run a separate arm with S8 first and S6 second (the driver already supports `SEVAROG_LIVE_CARDS`); the initially applied 0.5 fraction is then preserved through S8. No source change is required for this diagnostic, and no engine run was performed by Codex. A-832 also independently reports the full offline suite green (link check 0; BI 14/14; BH 12/12; verifier 34/35 with one Windows symlink skip; B-contract 135/135; C1289 3/3).
