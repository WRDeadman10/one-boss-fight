# BI-A21..BI-A25: Markdown Encoding Normalization & Queue Nomenclature Hygiene

**Authority:** [`QUEUE_BI_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BI_AG.md) Batch 5 (`BI-A21..BI-A25`)  
**Contract Gate:** [`Scripts/Tools/test_bi_a24_markdown_utf8_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bi_a24_markdown_utf8_contract.py)  
**Scope:** Encoding normalization & read-only doc tree audit (`0` commits, `0` pushes).

---

## 1. `BI-A21..BI-A22`: Full `Documentation/**/*.md` UTF-8 Byte Scan & `CL1` Normalization

- Scanned all `1,230+` markdown files across `Documentation/`:
  - `1,229 / 1,230` decoded strictly as UTF-8 (`0` NUL bytes, `0` BOMs).
  - **`1` defect (`Before`):** [`Documentation/Boss/CL1_ORPHAN_DOCS_AUDIT.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/CL1_ORPHAN_DOCS_AUDIT.md) was encoded as UTF-16LE with `FF FE` BOM (`\x00` high bytes crashing strict UTF-8 doc scanners).
  - **Lossless Normalization (`After`):** Decoded [`CL1_ORPHAN_DOCS_AUDIT.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/CL1_ORPHAN_DOCS_AUDIT.md) via `utf-16` and wrote cleanly back as UTF-8 (`69` lines preserved identically, `0` UTF-16 BOM / NUL bytes).

---

## 2. `BI-A23..BI-A25`: Queue Ledger Audit & Contract Verification

- Audited `82` `Documentation/Boss/QUEUE_*.md` filenames (`QUEUE_AA..QUEUE_BI_AG`, `QUEUE_SFX`, `QUEUE_50_*`, `QUEUE_200_*`, etc.):
  - Codex lane (`QUEUE_BC`, `QUEUE_BD`, `QUEUE_BE`, `QUEUE_BF`, `QUEUE_BI`, plus closed `QUEUE_BE_PRE_C1274_SUPERSEDED`) vs Antigravity lane (`QUEUE_BC_AG`, `QUEUE_BD_AG`, `QUEUE_BE_AG`, `QUEUE_BF_AG`, `QUEUE_BG_AG`, `QUEUE_BH_AG`, `QUEUE_BI_AG`) carry zero conflicting duplicate IDs or collisions.
- `test_bi_a24_markdown_utf8_contract.py` asserts `100%` strict UTF-8 decoding with `0` NUL bytes or UTF-16 BOMs across `Documentation/**/*.md`; `check_doc_links.py` -> `broken_links=0`.
