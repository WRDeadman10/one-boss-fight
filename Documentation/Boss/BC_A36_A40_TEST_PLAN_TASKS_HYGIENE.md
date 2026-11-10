# BC-A36..A40: `TEST_PLAN.md`, `TASKS.md` & Offline `Scripts/Tools` Hygiene Audit

**Queue Lane:** `QUEUE_BC_AG` Tasks `BC-A36`..`BC-A40` (Antigravity)  
**Authority:** `[C-1282]` #4  
**Scope:** Read-only audit of `Documentation/TEST_PLAN.md` & `Documentation/TASKS.md` (Codex retains `[X-1855]` claim on `TASKS.md` so no unrequested `TASKS.md` edits made), full `Scripts/Tools` offline discovery (`653` tests), and `check_doc_links.py`.

---

## 1. Document Structure Audit (`BC-A36..A38`)

| File | Total Lines | Markdown Headers | Duplicate Headers | Open Checkboxes (`- [ ]`) | Notes |
|---|---:|---:|---:|---:|---|
| `Documentation/TEST_PLAN.md` | `2,572` | `222` | `0` | `269` | Zero duplicate headers and `broken_links=0`; lines `155–156` (`X31–X35` pending wrapper/child BP packages) are now superseded by `[C-1282]` (`f97994a7`) once Lead/Codex syncs Queue BB checkboxes. |
| `Documentation/TASKS.md` | `3,073` | `43` | `0` | `0` | Zero duplicate headers, zero open checkboxes, `broken_links=0` (left untouched under active Codex `[X-1855]`). |

---

## 2. Offline Verification Smoke (`BC-A39..A40`)

- **`check_doc_links.py`:** `broken_links=0`.
- **Active Queue BB / BC Offline Contract Suite (`27/27` PASS):**
  - `test_probe_greystone_materials_contract.py`: `3/3 PASS` (`BC-A03` / `BB-A15` base-material & texture-parameter walk tested offline).
  - `test_c1276_sevarog_s6_s8_contract.py`: `4/4 PASS` (`[C-1280]` Decision 1 & 2 validated).
  - `test_c1278_x26_acceptance_contract.py`: `2/2 PASS` (verbatim `[FrameworkProof]` log predicates + `BC-A10` `Death_front`).
  - `test_b*_contract.py`: `18/18 PASS` (`BC-A01`, `BC-A09`, `BC-A14`, `BC-A25`, `BC-A26`, plus all Queue `BB` contracts).
- **Broader Historical `Scripts/Tools/test_*.py` Discovery (`653` tests, `13.26 s`):**
  - `637` PASS, `1` skipped, **`12` FAIL / `3` ERROR** — all outside current Queue `BB`/`BC` contracts, primarily:
    - Historical schema/refactor drift (`test_compare_manifest_to_legacy_defaults`, `test_import_er_clips`, `test_optional_presentation_wiring_contract`, `test_optional_tier2_hooks`, `test_tier1_visual_wiring_contract`, `test_validate_encounter_manifest` expecting `phase_two_aura_effect`).
    - **Flagged For Codex/Lead:** `test_check_shipping_guards.py` flagged `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:48` (`CVarBossProofSkipInitialWalk`, `use_line=151`) during the current in-flight tree check — Lead/Codex should verify Shipping `#if !UE_BUILD_SHIPPING` guard before Shipping packaging.
