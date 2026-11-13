# BI-A11..BI-A15: `Scripts/` PowerShell Runner (`.ps1`) Syntax & Lock-Hygiene Audit

**Authority:** [`QUEUE_BI_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BI_AG.md) Batch 3 (`BI-A11..BI-A15`)  
**Contract Gate:** [`Scripts/Tools/test_bi_a14_ps1_syntax_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bi_a14_ps1_syntax_contract.py)  
**Scope:** Offline PowerShell AST parse & lock/exit hygiene audit (`0` Unreal/Editor launches, `0` commits).

---

## 1. `BI-A11..BI-A12`: `.ps1` AST Parse & `Scripts/Editor/run_*.ps1` Lock Hygiene

- **PowerShell AST (`[System.Management.Automation.Language.Parser]::ParseFile`):** **`92 / 92`** `.ps1` scripts across `Scripts/` parse cleanly (`parse_errors = 0`).
- **Active Runner Lock Safety (`Scripts/Editor/run_*.ps1`, `57` files):** **`57 / 57` (`100%`)** wrap lock acquisition/cleanup in `try { ... } finally { ... }`.
- **Exit-Code Propagation:** `47 / 57` emit explicit exit codes (`$LASTEXITCODE` / `exit`), whereas `10` older pre-queue runners (`run_apply_notifies.ps1`, `run_c1256a_live_self_test.ps1`, `run_c1257a_author.ps1`, `run_c1257a_dry_run.ps1`, `run_c1258a_live_self_test.ps1`, `run_c1262a_live_diagnostic.ps1`, `run_c1265b_clip_trace.ps1`, `run_c1274_s6_locked_dryrun.ps1`, `run_inspect_props.ps1`, `run_verify_notifies.ps1`) rely on trailing PowerShell command status without an explicit final `exit`. Recorded for future runner updates without disturbing C-1155 runners in flight.

---

## 2. `BI-A13..BI-A15`: Mailbox Tooling Check, Contract Test & Receipt

- **`Scripts/MailboxPost.ps1`:** Uses named OS mutex `Global\OneBossFightMailbox` (`15 s` wait, `finally` release/dispose), strict `UTF8Encoding($false)` append-only writes (`[System.IO.FileShare]::ReadWrite`), and duplicate `### [` heading rejection.
- **`Scripts/MailboxViewer.py`:** Non-destructive read/web dashboard (`DEFAULT_PORT = 8080`); `parse_timestamp()` never fabricates timestamps from file `mtime`.
- **Contract Test (`BI-A14`):** [`test_bi_a14_ps1_syntax_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bi_a14_ps1_syntax_contract.py) AST-parses all `92` `.ps1` files via PowerShell and enforces `try`/`finally` cleanup on all `run_be_*.ps1` / `run_bf_*.ps1` runners plus mutex/UTF-8 invariants on `MailboxPost.ps1`.
