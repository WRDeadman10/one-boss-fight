# C-1116 / C-1117 — Lead runner and aura capture hotfixes

## Findings and fixes

- **C-1116 (`Scripts/RunLeadPie.ps1`):** Lead's uppercase 8.3 `.PY` short path reached Unreal's `py` command, which parsed it as code. The runner now lowercases the selected path after choosing either the dry-run path or live ShortPath and before converting separators. The existing live check still refuses whitespace in the path. This does not run Unreal.
- **C-1117 (`Scripts/Editor/pie_aura_comparison.py`):** `wait_capture` logged component values using names that were local to `write_manifest`, producing `NameError` after a captured PNG. `write_manifest` now returns the exact record it serialized; `wait_capture` passes that record to `log_frame_ready`, which reads the logged values from the same manifest object and uses explicit `UNKNOWN` fallbacks.

## Regression evidence

Both tests were added first and failed against the pre-fix source. The aura contract extracts and executes the READY-log formatter with a fake serialized manifest and also asserts that `wait_capture` passes the result of `write_manifest` to that formatter. The runner contract invokes `RunLeadPie.ps1 -DryRun` and inspects the emitted `-ExecCmds` Python path for a lowercase `.py` suffix and no spaces, while verifying the source lowercases the selected live path too.

Focused contracts: `Scripts.Editor.test_pie_aura_comparison_contract` plus `Scripts.Tools.test_lead_route_provenance_contract`, 17/17 pass. Python syntax compilation passes. No Unreal, Editor, build, asset, route, or package operation was performed. READY for Claude's Lead reruns.
