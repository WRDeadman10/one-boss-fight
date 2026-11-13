# BI-A06..BI-A10: `Scripts/Editor/` Safety Guards (`ImportError`, `ENGINE_LOCK`, `--dry-run`, `KI-169`)

**Authority:** [`QUEUE_BI_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BI_AG.md) Batch 2 (`BI-A06..BI-A10`)  
**Contract Gate:** [`Scripts/Tools/test_bi_a09_editor_safety_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bi_a09_editor_safety_contract.py)  
**Scope:** Strictly read-only AST & static safety inspection (`0` Editor calls, `0` commits).

---

## 1. `BI-A06..BI-A07`: Aggregate `Scripts/Editor/` (`496` Files) Guard Distribution

| Static Check Across `Scripts/Editor/**/*.py` | Count | Notes / Disposition |
|---|---|---|
| Total Python scripts | `496` | `100%` pass `ast.parse` (post Batch 1) |
| Unguarded top-level `import unreal` | `412` | Historical Unreal-only scripts; fail fast outside Editor (`ModuleNotFoundError`) |
| Offline-importable or guarded (`except ImportError:` / helper) | `84` | Includes `author_sevarog_draft_cards.py` and repaired `retarget_er_fit_candidate.py` |
| Call `save_loaded_asset` or `save_asset` | `115` | Asset-mutating scripts |
| Mutating scripts referencing `ENGINE_LOCK` / `lock` in `.py` | `28 / 115` | Remaining `87` rely on outer `.ps1` lock runners (`run_*.ps1`) or legacy manual execution |
| Mutating scripts with explicit `dry` / `--write` guard | `11 / 115` | Remaining `104` write directly when executed in Editor (`author_sevarog_draft_cards.py` & `fix_greystone_fit_root_motion.py` are cleanly fail-closed opt-in `--write`) |
| Bare `except:` clauses across all `496` scripts | `0` | Clean — zero broad bare-except swallowing |

---

## 2. `BI-A08..BI-A10`: `sevarog_pack_*.py` (`13` Scripts) & Active Authoring Gate Check

- **All `13` `Scripts/Editor/sevarog_pack_*.py` scripts (`01_proxy`..`10_combo_telegraph`):** `0/13` have `--dry-run` or in-script `ENGINE_LOCK` checks. **`sevarog_pack_07_bolt_impact.py:33` (`KI-169`)** still passes literal `'Damage Gampelay Effect'` and MUST remain unedited & **`BLOCKED`** until reflected Editor property readback verifies exact spelling on the target Blueprint.
- **Active `C-1247..C-1285` Core Scripts:** `author_sevarog_draft_cards.py` enforces `--dry-run` / `SEVAROG_DRY_RUN` & refusal without overwriting existing packages, while `fix_greystone_fit_root_motion.py` enforces explicit opt-in `--write` (`dry-run` default); `author_sevarog_draft_cards.py` & `retarget_er_fit_candidate.py` both support offline `ImportError` AST/unit-test inspection.
- **Contract Test (`BI-A09`):** [`test_bi_a09_editor_safety_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bi_a09_editor_safety_contract.py) enforces `0` bare `except:` across all `Scripts/Editor/**/*.py`, fail-closed `--write` guards on active authoring scripts, and non-regression of `KI-169` / `ImportError` boundaries.
