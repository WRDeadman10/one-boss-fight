# Rebuild incomplete-suite refusal audit (D77)

Date: 2026-11-03. Source-reviewed `Scripts/Rebuild.ps1` and added a terminal automation completion-marker requirement for its `-Tests` path.

The wrapper now requires all of: `UnrealEditor-Cmd.exe` exit 0, a `TEST COMPLETE. EXIT CODE: 0` terminal marker in the raw log, at least one `Test Completed` row, and every completed row to report `Result={Success}`. Missing raw log yields no marker/completions and fails. Zero completed rows, truncated output without a terminal marker, failed rows, and nonzero child process status all exit 1. This mirrors the marker present in retained successful Unreal automation logs (e.g. the cited 2026-10-31 full suite).

`Rebuild.ps1` PowerShell parser validation passed. No UnrealEditor-Cmd or build was run, and no synthetic log was routed through the full wrapper; marker behavior is source-verified only. The required marker is an Unreal log-format assumption that should be checked again on the next Lead-owned run.
