# BD-A36..A40 & Batch 8 (`BD-A36..BD-A40`): Repo Hygiene, Drift Triage & Shipping Guards

**Authority:** [`QUEUE_BD_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BD_AG.md), `[X-1872]` (`0` commits made, `0` pushes, `0` editor calls)

---

## 1. Read-Only Document Hygiene Audit (`BD-A36..BD-A37`)

*(Kept `TEST_PLAN.md`, `TASKS.md`, and `PROJECT_STATE.md` unmodified during active Codex `BE` Batches 7–8.)*
- `Documentation/TEST_PLAN.md`: `2,635` lines, `230` headers, `0` duplicate Markdown headers, `278` checkboxes, `broken_links=0` (`L155–156` `X31–X35` historical checkboxes remain flagged for next Lead/Codex sync).
- `Documentation/TASKS.md`: `3,082` lines, `43` headers, `0` duplicate Markdown headers, `0` open checkboxes (`- [ ]`), `broken_links=0`.
- `Documentation/PROJECT_STATE.md`: `657` lines, `30` headers, `0` duplicate Markdown headers, `0` open checkboxes, `broken_links=0`.

---

## 2. Legacy `Scripts/Tools/test_*.py` Drift Triage (`BD-A38`)

From the `653`-test full discovery (`12` FAIL / `3` ERROR):
- **Retired Schema / Refactored Symbol Drift (Safe / Historical — `12` FAIL / `3` ERROR):**
  - `test_compare_manifest_to_legacy_defaults.py` (`2` ERROR: legacy `RPGAttackTracker.cpp:41` line citation shifted).
  - `test_import_er_clips.py` (`1` ERROR: `GATE-07` registry check expects `AN_ER_Backstep_Back` before Mixamo V2 rename).
  - `test_optional_presentation_wiring_contract.py` (`1` FAIL), `test_optional_tier2_hooks.py` (`4` FAIL), `test_tier1_visual_wiring_contract.py` (`1` FAIL): assert superseded pre-`RPGPresentationRules` Tier-2 helper names (`IsTier2PreviewEnabled`).
  - `test_validate_encounter_manifest.py` (`4` FAIL) & `test_encounter_tuning_example.py` (`1` FAIL): assert `phase_two_aura_effect` before `RPGLook`/profile migration.
- **Shipping Guard Regression Fixed (`BD-A39`):**
  - `test_check_shipping_guards.py` earlier caught `CVarBossProofSkipInitialWalk` (`RPGFrameworkBossCharacter.cpp:48`, flagged by Antigravity `[A-749]`, fixed by Codex `[X-1859]`/`[X-1864]`) and now passes **`4/4`** cleanly across all `Source/` files.

---

## 3. Verification & Owner-Ready Batch 8 Manifest (`BD-A40`)

- `test_check_shipping_guards.py`: **`4/4 PASS`**
- All active Queue `BB` / `BC` / `BD` contracts + `test_validate_queue_batches`: **`100% PASS`** (`test_c1285_retarget_root_chain_contract.py` `3/3 PASS`)
- `check_doc_links.py`: `broken_links=0`
- **Owner-ready Batch 8 file list (`0` commits made):** `Documentation/Boss/BD_A36_A40_HYGIENE_AND_DRIFT_TRIAGE.md`
