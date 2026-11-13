# BI-A01..BI-A05: Python AST Readiness & `KI-170` / `KI-171` / `retarget_er_fit_candidate.py` Audit

**Authority:** [`QUEUE_BI_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BI_AG.md) Batch 1 (`BI-A01..BI-A05`, per acting Lead `[X-1897]`)  
**Contract Gate:** [`Scripts/Tools/test_bi_a04_python_ast_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bi_a04_python_ast_contract.py)  
**Policy (`[X-1897]`):** `0` Unreal/Editor/Blender/runtime/asset operations, `0` git commits, `0` remote pushes, working-tree `C-1285` diffs preserved intact.

---

## 1. `BI-A01..BI-A03`: AST Defect Inventory & Bounded Syntax Repairs (`888 / 888` Pass)

Full `ast.parse` scan across `Scripts/**/*.py` (`887` existing files + `1` new contract test = `888` `.py` files) identified **exactly `3` parse failures**, all now syntactically repaired cleanly offline:

| Script | Defect Found (`Before`) | Bounded Syntax Repair (`After`) | Remaining Runtime Gate (`BLOCKED`) |
|---|---|---|---|
| [`Scripts/Editor/retarget_er_fit_candidate.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Editor/retarget_er_fit_candidate.py) | Line `23` `SyntaxError: expected 'except' or 'finally' block`: `C-1285` inserted `def ensure_root_chain_globally_scaled(...)` inside open `try: import unreal` block above line `56` `except ImportError:`. | Moved `except ImportError: unreal = None` directly below `import unreal` (lines `19–22`), leaving all `33` lines of `ensure_root_chain_globally_scaled` & line `247` call byte-exact; offline import yields `unreal=None`, `has_fn=True`. | Live `--write` / paired `RM4` capture remains **`BLOCKED`** on Lead Engine slot (`[C-1286+]`). |
| [`Scripts/author_brief13_anims.py`](file:///C:/UnrealProject/OneBossFight/Scripts/author_brief13_anims.py) (`KI-170`) | Line `141` `SyntaxError: invalid decimal literal`: outer `code = r"""..."""` (lines `7`, `503`) was prematurely closed by inner `"""` docstrings (lines `55`, `57`, `141`, `173`, `203`, `205`, `218`, `220`), exposing raw text `(tip Z 0‑3 cm)` to Python's tokenizer. | Switched outer delimiters (`7`, `503`) from `r"""` / `"""` to `r'''` / `'''` (`0` inner `'''` collisions), preserving the entire Blender payload unmodified. | Blender execution & UE FBX import verification remain **`BLOCKED`** (`KI-170`). |
| [`Scripts/Editor/sevarog_pack_02_montages_abilities.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Editor/sevarog_pack_02_montages_abilities.py) (`KI-171`) | Line `215` `IndentationError: unexpected indent`: line `214` `unreal.BlueprintEditorLibrary.compile_blueprint(hs)` sat at column `0` between `hs.modify()` and `save_loaded_asset(hs, False)` (both indented `4` spaces). | Restored `4`-space indentation on line `214` (`unreal.BlueprintEditorLibrary.compile_blueprint(hs)`). | Reflected Blueprint property / Editor verification remain **`BLOCKED`** (`KI-171`). |

*(Advisory finding recorded during AST scan: `Scripts/Editor/pie_pack_demo.py:1` emits Python `DeprecationWarning: invalid escape sequence '\]'` inside docstring; parses cleanly via `ast.parse`.)*

---

## 2. `BI-A04..BI-A05`: Verification & Batch 1 Owner-Ready Manifest

- `Scripts/Tools/test_bi_a04_python_ast_contract.py`: **`2/2 PASS`** (`888/888` `Scripts/**/*.py` AST parse OK; `retarget_er_fit_candidate.py` retains `ensure_root_chain_globally_scaled`, `except ImportError:`, `GLOBALLY_SCALED`, `set_retarget_chain_settings`).
- `test_c1285_retarget_root_chain_contract.py` (`3/3 PASS`), `test_be_a02_rootfix_dryrun_contract.py` (`1/1 PASS`), `test_validate_queue_batches.py` (`4/4 PASS`).
- `check_doc_links.py`: `broken_links=0`.
- **Owner-Ready Note:** `Scripts/Editor/retarget_er_fit_candidate.py` & `Scripts/Editor/sevarog_pack_02_montages_abilities.py` sit under `Scripts/Editor/` (Group B alongside `retarget_pack_to_greystone.py` until Lead verifies live runs); `QUEUE_BI_AG.md`, `BI_A01_A05_PYTHON_SYNTAX_AND_RETARGET_AUDIT.md`, and `test_bi_a04_python_ast_contract.py` sit cleanly in Antigravity Group A.
