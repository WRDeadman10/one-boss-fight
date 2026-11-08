# AK-C11–C15 — Lead PIE runner hardening

| Task | Offline result |
|---|---|
| C11 | Pester-free dry-run now refuses invalid routes, malformed `-Env`, a manually supplied H019 route value, and timeout below 10 s. It asserts both route commands, extra environment, `-nosound`, `-abslog`, stop marker, lines paths, and no lock/output creation. |
| C12 | Source audit: live runner creates `ENGINE_LOCK` atomically, kills only the process it launched on marker/timeout/exception, writes `status.txt`, and exits with failure if any route lacks the marker. A process that exits just before polling gets one final marker check. Live timeout/early-exit behavior still needs Lead smoke. |
| C13 | Source audit: each route snapshots process env values, applies extras and selected H019, then restores them in `finally`. Dry-run with a pre-existing `ER_GC_ASSIGN=original` preserves it. Live env restoration remains unrun under Lead engine lock. |
| C14 | Absolute and relative script/output paths work in dry-run. Live `ExecCmds=py` uses the script's Windows 8.3 ShortPath; if the filesystem does not provide an unspaced path, it fails explicitly instead of issuing a malformed Python command. Quoted `-abslog` supports spaces in the output folder. |
| C15 | `Scripts/Tests/TestRunLeadPieDryRun.ps1` passes after the changes. PowerShell parser check passes. The command and Lead-only runtime gate are documented in `AK_SPRINT_LEAD_PIE_RUNNER.md`. |

No editor, PIE, build or package operation was run by Codex. The Lead's full-fight capture holds `ENGINE_LOCK`; live runner smoke waits for that lock to clear.
