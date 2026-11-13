# BI-A36..BI-A40: `Import/` Source Art Tree & `Unreal_Boss_Combat_Engineering_Kit/` Audit

**Authority:** [`QUEUE_BI_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BI_AG.md) Batch 8 (`BI-A36..BI-A40`)  
**Contract Gate:** [`Scripts/Tools/test_bi_a39_import_and_kit_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bi_a39_import_and_kit_contract.py)  
**Scope:** Strictly read-only disk, tracking, & JSON validity audit (`0` commits, `0` pushes).

---

## 1. `BI-A36..BI-A37`: `Import/` Tree Census & `> 5 MB` Large Binary Register

- **Total files across `Import/`:** `264` files (`0` zero-byte files; `230` tracked in `git ls-files` under Git LFS).
- **Large source files (`> 5 MB`, `13` total):**
  - `Import/Audio/`: `MX_Boss01_Phase1.wav` (`32,926,982` B), `MX_Boss01_Phase2.wav` (`52,151,546` B), `MX_Boss01_Phase2.ogg` (`6,627,783` B)
  - `Import/Boss01/Animations/`: `playblast_A2_combo.gif` (`11,811,949` B), `playblast_A2_combo_front.gif` (`11,811,949` B), `playblast_A2_combo_side.gif` (`8,697,911` B)
  - `Import/Characters/`: `Greystone.fbx` (`5,783,280` B), `Greystone_Dragonlord.fbx` (`5,783,792` B), `Greystone_Tough.fbx` (`5,302,064` B), `Greystone_WhiteTiger.fbx` (`5,783,408` B), `Builds/SKM_Viking.fbx` (`5,502,668` B)
  - `Import/` root: `SKM_CombatMannequin.fbx` (`7,612,112` B), `SKM_Quinn.fbx` (`7,078,848` B)
  - All kept cleanly outside `git diff --cached` (`0` untracked additions staged).

---

## 2. `BI-A38..BI-A40`: `Unreal_Boss_Combat_Engineering_Kit/` & `Saved/BossCombatReview/` Caches

- **`Unreal_Boss_Combat_Engineering_Kit/`:** `60` files (`27` `.md` docs, `12` `.png` diagrams/concept art, plus templates/schemas); markdown links verified clean by `check_doc_links.py` (`broken_links=0`).
- **`Saved/BossCombatReview/`:** Holds `1` JSON cache (`bb_a15_greystone_materials_probe.json`), valid UTF-8 JSON (`gitignored` under `Saved/`, zero staging risk).
- **Contract Test (`BI-A39`):** [`test_bi_a39_import_and_kit_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bi_a39_import_and_kit_contract.py) asserts `0` zero-byte files under `Import/`, valid UTF-8 JSON under `Saved/BossCombatReview/` (when present), and valid UTF-8 markdown in `Unreal_Boss_Combat_Engineering_Kit/`.
