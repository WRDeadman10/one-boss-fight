# D147 — crash and early-exit suite-log classifier audit

Date: 2026-11-03  
Scope: static comparison of the automation rebuild gate and offline suite-log utilities. No Editor, build, or test suite was run.

## Classifier behavior

| Path | Completion rule | Exit-zero/no-completion behavior |
|---|---|---|
| `Scripts/Rebuild.ps1:57-72` with `-Tests` | Requires UnrealEditor-Cmd exit 0, literal `TEST COMPLETE. EXIT CODE: 0`, at least one `Test Completed` row, and every completed row to be `Success`. | Fails if the process exits 0 but the terminal marker or completed rows are absent. A crash/truncation that produces no terminal success marker cannot pass. |
| `Scripts/Tools/suite_log_report.py` | Counts parseable completion rows; non-success results or duplicate identities return 1. Requires the terminal successful-suite marker by default. | C-764 hotfix: empty logs and truncated logs now return 2 with `PARTIAL`; `--allow-partial` enables intentional summaries but labels them non-certifying. |
| `Scripts/Tools/diff_suite_logs.py` | Requires at least one completion row per file, rejects duplicate identities, compares row identities/results, and checks the terminal successful-suite marker. | C-764 hotfix: if either log lacks the marker, it prints `PARTIAL` and exits 3. Exit 0 is reserved for identical complete logs; changed complete logs exit 1; invalid/no-row inputs exit 2. |
| `Scripts/RunDrivers.ps1:80-86,130-164` | Requires the editor-task process to exit 0 and a bounded per-driver RESULT/SUMMARY line with zero failures and at least its declared minimum count; timeouts become failure rows. | A missing final line times out/fails. The driver runner's row result is based on script-specific completion text, not a full editor process lifecycle marker. |

The fixture `test_suite_tools_accept_truncated_logs_with_completed_rows` in `Scripts/Tools/test_queue_c_tools.py` explicitly preserves truncated-log parsing for reporting/diff use. This is not a safe pass classifier. Conversely, `Rebuild.ps1` is the authoritative full-suite wrapper and gates on both exit code and terminal success evidence. The independent Queue C report tools are partial-log readers and their success codes mean “parsed rows have no failure/duplicate” or “the parsed rows match.”

## Finding and disposition

The full suite wrapper satisfies the completion requirement: exit 0 without the terminal marker and completed successful rows is reported failed/incomplete. C-764's bounded hotfix brings the two offline suite utilities in line: the summary tool fails closed unless `--allow-partial` is explicit, and the diff tool reports partial input with exit 3. A complete successful marker still does not independently certify every row passed in the summarizer; inspect its failure/duplicate counts as well. Tool fixtures were added and the full offline suite was run after the hotfix.
