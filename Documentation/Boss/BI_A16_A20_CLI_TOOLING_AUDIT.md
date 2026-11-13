# BI-A16..BI-A20: `KI-165..KI-167` CLI Tooling Diagnostics & Root `Scripts/*.py` Audit

**Authority:** [`QUEUE_BI_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BI_AG.md) Batch 4 (`BI-A16..BI-A20`)  
**Scope:** Read-only inspection of `KI-165..KI-167` CLIs & `119` root `Scripts/*.py` helpers (`0` CLI mutations to Codex tools, `0` commits).

---

## 1. `BI-A16..BI-A18`: `KI-165..KI-167` Source Findings (Confirmed Open)

- **`KI-165` (`Scripts/Tools/make_source_manifest.py:17–25`):** Does not fail closed when `<root>/Source` is absent — `source.rglob("*")` returns empty list and exits `0` writing an empty manifest (`atomic_write_text`). Recorded for bounded Codex/Lead tooling hardening (`--require-source` / `if not source.is_dir(): parser.error(...)`).
- **`KI-166` (`profile_dump.py:28`, `card_table.py:14`, `validate_baked_cards.py:15`, `plugin_dependencies.py:18,22`):** Call `json.loads(...)` directly with zero `try/except json.JSONDecodeError` handler naming the failing input path; root-shape `.get()` assumes `dict` (raises `AttributeError` if input JSON is a list/scalar).
- **`KI-167` (`proof_report.py`, `asset_provenance.py`, `evidence_summary.py`, `token_coverage.py`, `suite_log_report.py`, `summarize_framework_log.py`, `plot_framework_timeline.py`):** Emit `.resolve()` absolute filesystem paths or raw matched log lines into stdout/artifacts; local diagnostic use only until path-redaction flag is requested.

---

## 2. `BI-A19..BI-A20`: Root `Scripts/*.py` (`119` Files) Categorization & Contract Test

| Category Under Root `Scripts/` | Count | Examples / Status |
|---|---|---|
| Blender authoring helpers (`bpy` / `execute_blender`) | `84` | `author_brief13_anims.py` (`KI-170` syntax repaired in `BI-A03`; runtime `BLOCKED`), `author_all_clips_brief12.py`, etc. |
| Standalone CLI / utilities / checks | `35` | Active: `CheckDocs.py`, `CheckShippingBinary.py`, `CheckShippingFeatureSymbols.py`, `CheckStagedContent.py`, `ImportAssetClosure.py`, `MailboxViewer.py`, `SummarizeBenchmark.py`, `BalanceModel.py`, `CollectBalanceRuns.py`; Historical/boss01/misc: `stitch_*.py`, `fbx_*.py`, `bp_*.py`, `mcp_call.py` |
| **Total root `Scripts/*.py`** | **`119`** | `119 / 119` pass `ast.parse` cleanly (`BI-A04`) |

- **Contract Test:** [`Scripts/Tools/test_bi_a19_cli_tooling_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bi_a19_cli_tooling_contract.py) asserts non-empty existence & clean AST across all `12` `KI-165..KI-167` files and active root utility CLIs (`CheckDocs.py`, `CheckStagedContent.py`, `ImportAssetClosure.py`, `MailboxViewer.py`).
