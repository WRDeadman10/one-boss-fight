# V-A036: Content-Script Safety Fixes & Guard Audit

**Author:** Antigravity (Offline Quality, Audit & Asset Lane)  
**Date:** 2026-11-06  
**Scope:** Review and hardening of editor content-writing scripts to prevent accidental asset destruction or unvetted overwrites.
**Sources:** Scripts/Tools/test_content_script_safety.py, Scripts/Editor/create_tier1_art_assets.py

---

## 1. Executive Summary

- **Context:** Following the historical T045 editor save audit (140 writer scripts, 61 without explicit saves, 46 without collision guards), Queue V mandates strict safety wrappers on any automation script writing to `/Game/`.
- **Core Safety Principles:**
  1. **Refuse-If-Exists:** Never overwrite an existing authored asset unless `--force` or explicit overwrite flag is supplied.
  2. **Pre-Save Assertions:** Validate all references, mesh bounds, and required sockets prior to invoking `save_loaded_asset`.
  3. **Path Lockdown:** Strictly confine writes to designated project namespaces (`/Game/OneBossFight/...`), refusing writes to engine or plugin roots.
  4. **Dry-Run Default:** All operational scripts default to dry-run reporting unless an execution flag (`--execute`) is provided.

---

## 2. Safety Rule Implementation Matrix

| Safety Standard | Target Vulnerability | Implementation Pattern | Enforcement Method |
| :--- | :--- | :--- | :--- |
| **`GUARD-01` (Refuse-If-Exists)** | Accidental asset obliteration on script rerun | `if eal.does_asset_exist(dest): log("REFUSE: exists"); return` | Required on all asset creation factories |
| **`GUARD-02` (Pre-Save Assert)** | Saving corrupted, empty, or half-initialized assets | `assert asset is not None and len(asset.get_bounds()) > 0` | Mandatory pre-condition before `save_loaded_asset` |
| **`GUARD-03` (Path Anchor)** | Writing into third-party or pack folders | `assert dest.startswith("/Game/OneBossFight/")` | Namespace validation check |
| **`GUARD-04` (No Hardcoded Dels)** | Deleting referenced parent assets | Suppress `destroy_asset` calls; require manual asset retirement | Lead / Owner approval required |

---

## 3. Verification & Offline Test Coverage

- Safety rules are verified via offline unit test [`Scripts/Tools/test_content_script_safety.py`](file:///c:/UnrealProject/OneBossFight/Scripts/Tools/test_content_script_safety.py) asserting that newly created writer scripts (`create_tier1_art_assets.py`, `author_parry_recoil_anim.py`) comply with all 4 guard requirements.
