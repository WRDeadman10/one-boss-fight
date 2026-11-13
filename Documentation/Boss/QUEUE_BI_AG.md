# Queue BI — Antigravity Residual 50 Offline Tasks (`BI-A01..BI-A50`)

**Queue Authority:** Acting Lead Assignment `[X-1897]` (`2026-11-11`, owner-authorized successor to [`QUEUE_BH_AG_CLOSEOUT.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BH_AG_CLOSEOUT.md))  
**Lane Owner:** Antigravity (`Python/PS1 Tooling Readiness / Asset Closure / Encoding & License Hygiene / Offline Contracts / Owner Commit Prep`)  
**Disjoint Scope Rule (`[X-1897]`):** Completely disjoint from Codex [`QUEUE_BI.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BI.md) (`BI-X01..X50`). Honors all working-tree diffs without overwriting in-flight edits; `0` Unreal/Editor/build/runtime/asset operations, `0` autonomous git commits, `0` pushes, `0` staged media, `broken_links=0`.

---

## Batch 1 (`BI-A01..BI-A05`): Python AST Readiness & `KI-170`/`KI-171`/`retarget_er_fit_candidate.py` Repair

| ID | Task | Acceptance |
|---|---|---|
| `BI-A01` | AST-parse all `887` `.py` files under `Scripts/` (`Scripts/`, `Editor/`, `Tools/`) and record exact syntax defects (`retarget_er_fit_candidate.py:23`, `author_brief13_anims.py:141` `KI-170`, `sevarog_pack_02_montages_abilities.py:215` `KI-171`) | Audit table |
| `BI-A02` | Bounded syntax fix in `Scripts/Editor/retarget_er_fit_candidate.py`: place `except ImportError: unreal = None` directly below `try: import unreal`, preserving all `33` lines of `C-1285` `ensure_root_chain_globally_scaled` & line `247` call bit-exact | Clean AST + intact `C-1285` diff |
| `BI-A03` | Bounded syntax fixes in `Scripts/author_brief13_anims.py` (`KI-170`: outer raw string delimiters `r'''...'''`) & `Scripts/Editor/sevarog_pack_02_montages_abilities.py:214` (`KI-171`: indent `compile_blueprint(hs)` inside block), carrying Editor/Blender verification `BLOCKED` | Clean AST + `BLOCKED` gates retained |
| `BI-A04` | Add offline unittest `Scripts/Tools/test_bi_a04_python_ast_contract.py` verifying `887+/887+` `.py` files across `Scripts/` parse cleanly (`0` errors) + re-run `test_c1285` & `test_be_a02` | Unittest PASS |
| `BI-A05` | Publish Batch 1 audit (`Documentation/Boss/BI_A01_A05_PYTHON_SYNTAX_AND_RETARGET_AUDIT.md`) & post `[A-###]` | Receipt + post |

## Batch 2 (`BI-A06..BI-A10`): `Scripts/Editor/` Safety Guards (`ENGINE_LOCK`, `DRY_RUN`, `KI-169` & Legacy Helpers)

| ID | Task | Acceptance |
|---|---|---|
| `BI-A06` | Audit all `496` `Scripts/Editor/*.py` files for unguarded top-level `import unreal` (`411` files vs offline-safe `85`) | Inventory report |
| `BI-A07` | Audit `Scripts/Editor/*.py` asset-saving scripts lacking `ENGINE_LOCK` (`87` files) or `--dry-run` / `DRY` mode (`104` files) | Safety matrix |
| `BI-A08` | Inspect all `13` `Scripts/Editor/sevarog_pack_*.py` scripts (`KI-169` `'Damage Gampelay Effect'` & reflected-property gates carried `BLOCKED` on Editor readback) | Doc + `BLOCKED` |
| `BI-A09` | Offline AST safety contract (`Scripts/Tools/test_bi_a09_editor_safety_contract.py`) checking active `C-1155..C-1285` authoring/PIE scripts keep `ENGINE_LOCK` / offline `ImportError` guards & `0` bare `except:` clauses | Unittest PASS |
| `BI-A10` | Publish Batch 2 safety audit & post `[A-###]` | Receipt + post |

## Batch 3 (`BI-A11..BI-A15`): `Scripts/` PowerShell Runner (`.ps1`) Syntax & Lock-Hygiene Audit

| ID | Task | Acceptance |
|---|---|---|
| `BI-A11` | Parse all `92` `.ps1` scripts under `Scripts/` using PowerShell AST `[System.Management.Automation.Language.Parser]::ParseFile` | Parse matrix |
| `BI-A12` | Audit `Scripts/Editor/run_*.ps1` active runners for explicit `ENGINE_LOCK` cleanup/release on failure and exit-code propagation | Audit table |
| `BI-A13` | Verify `Scripts/MailboxPost.ps1` and `Scripts/MailboxViewer.py` encoding/CLI invariants read-only | Audit notes |
| `BI-A14` | Add offline PowerShell parse contract (`Scripts/Tools/test_bi_a14_ps1_syntax_contract.py`) asserting `92/92` `.ps1` parse errors = `0` | Unittest PASS |
| `BI-A15` | Publish Batch 3 runner audit & post `[A-###]` | Receipt + post |

## Batch 4 (`BI-A16..BI-A20`): `KI-165..KI-167` CLI Tooling Diagnostics & Root `Scripts/*.py` Audit

| ID | Task | Acceptance |
|---|---|---|
| `BI-A16` | Inspect `Scripts/Tools/make_source_manifest.py` (`KI-165`) & active callers to confirm whether missing `<root>/Source` check can fail closed safely | Source audit |
| `BI-A17` | Inspect `profile_dump.py`, `card_table.py`, `validate_baked_cards.py`, & `plugin_dependencies.py` (`KI-166`) JSON error paths & callers | Source audit |
| `BI-A18` | Inspect `KI-167` local report scripts (`proof_report.py`, `asset_provenance.py`, `evidence_summary.py`, `token_coverage.py`, `suite_log_report.py`, `summarize_framework_log.py`, `plot_framework_timeline.py`) for path leak boundaries | Source audit |
| `BI-A19` | Inventory all `119` root `Scripts/*.py` helpers (`CheckDocs.py`, `CheckStagedContent.py`, `ImportAssetClosure.py`, `BalanceModel.py`, Blender scripts) distinguishing active tools vs legacy | Catalog + test |
| `BI-A20` | Publish Batch 4 CLI tooling audit (`test_bi_a19` contract) & post `[A-###]` | Receipt + post |

## Batch 5 (`BI-A21..BI-A25`): Markdown Encoding Normalization (`CL1_ORPHAN_DOCS_AUDIT.md`) & Doc Tree Hygiene

| ID | Task | Acceptance |
|---|---|---|
| `BI-A21` | Scan all `Documentation/**/*.md` files for non-UTF-8 byte encodings (`CL1_ORPHAN_DOCS_AUDIT.md` UTF-16LE `FF FE` BOM) & broken BOM/NULs | Encoding scan |
| `BI-A22` | Convert `Documentation/Boss/CL1_ORPHAN_DOCS_AUDIT.md` losslessly from UTF-16LE to clean UTF-8 (preserving exact text content) | Clean UTF-8 conversion |
| `BI-A23` | Audit `Documentation/Boss/` for any duplicate/conflicting queue numbering (`QUEUE_BA..QUEUE_BI_AG`) | Queue ledger |
| `BI-A24` | Add offline contract `Scripts/Tools/test_bi_a24_markdown_utf8_contract.py` asserting `100%` of `Documentation/**/*.md` decode strictly as UTF-8 with `0` NUL bytes | Unittest PASS |
| `BI-A25` | Publish Batch 5 encoding hygiene audit + `check_doc_links.py` & post `[A-###]` | Receipt + post |

## Batch 6 (`BI-A26..BI-A30`): Third-Party Content Packs vs `Documentation/ASSET_LICENSES.md` & `.gitignore`

| ID | Task | Acceptance |
|---|---|---|
| `BI-A26` | Inventory all third-party directories under `Content/` (`Paragon*`, `AdvancedARPGCombat`, `BeamPack`, `BloodPack`, `Deadly_Ruins`, `Essential_Foosteps_SK`, `Free_Spells`, `Mage`, `MS`, `MSPresets`, `RealisticSwordSoundEffects`, `StarterContent`, `Vefects`, etc.) with `.uasset` counts & byte sizes | Pack inventory |
| `BI-A27` | Cross-check every `Content/<Pack>/` directory against `.gitignore` and `git ls-files` proving `0` third-party `.uasset`s tracked or dirtied | Tracking matrix |
| `BI-A28` | Cross-check `Content/` third-party packs against `Documentation/ASSET_LICENSES.md` recording any undocumented packs | License gap table |
| `BI-A29` | Add offline unittest `Scripts/Tools/test_bi_a29_pack_ignore_contract.py` verifying `0` third-party pack files tracked/modified in git | Unittest PASS |
| `BI-A30` | Publish Batch 6 license & pack isolation audit & post `[A-###]` | Receipt + post |

## Batch 7 (`BI-A31..BI-A35`): Project Content (`Boss01/`, `Environment/`, `UI/`, `Input/`, `Levels/`, `Audio/`) Git-LFS & Asset Integrity

| ID | Task | Acceptance |
|---|---|---|
| `BI-A31` | Verify `.gitattributes` Git LFS tracking rules match tracked `.uasset`/`.umap`/binary types across `Content/OneBossFight/` | LFS alignment |
| `BI-A32` | Audit `Content/OneBossFight/Audio/` (`2` files, `55.9 MB`), `Boss01/` (`77` files), `Environment/` (`26` files), `UI/` (`7` files), `Input/` (`14` files), & `Levels/` (`2` `.umap`) for non-zero bytes and clean `git status` | Asset table |
| `BI-A33` | Verify every `.uasset`/`.umap` cited in `DefaultEngine.ini` (`L_SevarogArena`, `BP_AdvancedGameMode`, `BP_AdvancedGameInstance`) & active UI fonts resolves on disk | Resolution check |
| `BI-A34` | Add offline unittest `Scripts/Tools/test_bi_a34_project_content_lfs_contract.py` asserting non-zero project maps/UI/audio/data `.uasset`s and `.gitattributes` LFS patterns | Unittest PASS |
| `BI-A35` | Publish Batch 7 project content audit & post `[A-###]` | Receipt + post |

## Batch 8 (`BI-A36..BI-A40`): `Import/` Source Art Tree & `Unreal_Boss_Combat_Engineering_Kit/` Provenance Audit

| ID | Task | Acceptance |
|---|---|---|
| `BI-A36` | Inventory all `232+` files across `Import/{Boss01,Characters,Player,Environment,Audio,ThirdParty}` (counts, extensions, zero-byte check, sizes) | Import table |
| `BI-A37` | Cross-check `Import/` tracked vs untracked/ignored files and flag any binary files `> 5 MB` under `Import/` | Size/tracking report |
| `BI-A38` | Audit `Unreal_Boss_Combat_Engineering_Kit/` diagrams, concept art, and markdown links vs `check_doc_links.py` | Kit audit |
| `BI-A39` | Audit `Saved/BossCombatReview/` untracked JSON caches (`bb_a15_*`, etc.) for non-zero valid JSON without staging risk | Cache audit |
| `BI-A40` | Publish Batch 8 `Import/` & Kit provenance report (`test_bi_a39` contract) & post `[A-###]` | Receipt + post |

## Batch 9 (`BI-A41..BI-A45`): Cross-Queue Disjointness, Owner Manifest Refresh & Regression Check

| ID | Task | Acceptance |
|---|---|---|
| `BI-A41` | Audit strict task disjointness between `QUEUE_BI_AG.md` (`BI-A01..A50`) and Codex `QUEUE_BI.md` (`BI-X01..X50`) | Zero-overlap check |
| `BI-A42` | Update Owner `git add` Group A manifest (`BH_A41_A45_FINAL_CONSOLIDATED_MANIFEST.md` or addendum) separating newly repaired Group B scripts (`retarget_er_fit_candidate.py`) from Group A Antigravity docs/tests | Manifest update |
| `BI-A43` | Carry all runtime/Editor/Owner gates (`KI-168..173`, `retarget_er_fit_candidate.py` live run, `X26` PIE, Owner SFX/aura picks, Shipping) explicitly as `BLOCKED` | Blocker register |
| `BI-A44` | Hold next queue creation unless Lead/Owner explicitly authorize (`0` unapproved successor queue) | Hold confirmation |
| `BI-A45` | Publish Batch 9 consolidated readiness check & post `[A-###]` | Receipt + post |

## Batch 10 (`BI-A46..BI-A50`): Final `QUEUE_BI_AG` Verification & Closeout

| ID | Task | Acceptance |
|---|---|---|
| `BI-A46` | Reconcile all `BI-A01..BI-A45` deliverables, AST fixes, tests, & `BLOCKED` tags | Deliverable matrix |
| `BI-A47` | Author `Documentation/Boss/QUEUE_BI_AG_CLOSEOUT.md` | Closeout doc |
| `BI-A48` | Confirm `0` commits / `0` pushes / `0` Unreal Engine or asset mutations throughout `QUEUE_BI_AG` | Policy audit |
| `BI-A49` | Run full active offline suite (`test_bi_*` + `test_bh_*`..`test_bd_*` + `test_b*_contract` + `test_check_shipping_guards` + `check_doc_links.py`) | `0` fail, `broken_links=0` |
| `BI-A50` | Post Batch 10 closeout `[A-###]` receipt cleanly | Closeout + post |
