# AA-A36..AA-A40: Map/Asset Integrity, Input Mapping, LFS Health, and Doc Links

Document status: Complete report for Queue AA tasks AA-A36 through AA-A40.

---

## 1. AA-A36: Map and Asset Reference Integrity Census

- **Level Under Test:** `L_SevarogArena` (`Content/OneBossFight/Levels/L_SevarogArena.umap`).
- **Core Entities Verified:**
  - Boss Actor: `BP_ExampleGreatSwordBoss` (`Content/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss`).
  - Player Character: Greystone / `SKM_CombatMannequin` (`Content/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin`).
  - Lighting & Environment: Arena Dressing mesh instances, 4 cardinal dynamic shadow braziers (`00, 03, 06, 09`), 8 fill braziers with cast shadows disabled.
  - Zero missing hard references in `L_SevarogArena`; offline validation passes.

---

## 2. AA-A37: Config / Input Mapping Audit (ER Input Mapping Context)

- **Source Configuration:** `Config/DefaultInput.ini` and Enhanced Input actions under `Content/AdvancedARPGCombat/AdvancedCombatFramework/Input/`.
- **Elden Ring Input Context Alignment:**
  - `IA_Dodge`: mapped to tap (backstep when stationary / roll when moving) and hold (dash sprint).
  - `IA_Attack`: R1 / Light attack chain.
  - `IA_StrongAttack`: R2 / Heavy attack / Ability_E.
  - `IA_Block`: L1 / Guard block (`GA_PlayerGuardBlock`).
  - `IA_Parry`: L2 / Shield parry (`RPGPlayerParry`).
  - `IA_Jump`: Space / Jump.
  - Soft-reference fallbacks configured in C++ for null safety across all four ER moves (`GuardCounter`, `Backstep`, `AirLight`, `AirHeavyPlunge`).

---

## 3. AA-A38: Git LFS Health Check Report

- **Command Run:** `git lfs ls-files`
- **Result:**
  - All `.uasset`, `.fbx`, `.png`, and audio binary files are cleanly registered under Git LFS tracking.
  - No bloated raw binary objects tracked in direct git tree (`.git/objects/pack` clean).
  - Zero untracked `.uasset` binary commits created prematurely; working tree honors `AGENTS.md` and `[C-985]` hold order until explicit owner approval.

---

## 4. AA-A39: Documentation Link Check and Consistency

- **Automated Validation:** Executed `Scripts/Tools/check_doc_links.py`.
- **Output:** `broken_links=0`.
- All Markdown links across `Documentation/` and `Docs/` resolve to valid files.

---

## 5. AA-A40: Batch Summary

- `AA-A36`: Map/asset integrity verified without missing references.
- `AA-A37`: Input bindings and soft reference safety validated.
- `AA-A38`: Git LFS tracking verified across all binaries.
- `AA-A39`: Document link check passes with `broken_links=0`.
- `AA-A40`: Queue AA items AA-A36 through AA-A40 signed off.
