# C-1239a: Hitch-aware Ember timing parity gate

Updated `Scripts/Editor/pie_ember_notify_timing_parity.py` so each measured timing trial logs every PIE callback delta. A callback delta strictly greater than 0.1 seconds marks that attempt `HITCH`; the driver retries the same mode/move up to three times after the initial attempt. Each retry has a separate row and attempt number, so phases from a hitched run cannot leak into the clean result.

Only a frame-clean, started, ended attempt enters the selected `clean_rows` comparison. Incomplete or refused moves fail their clean-trial check; four hitched attempts record an exhausted trial and fail the gate. The final `RESULT` reports the clean-trial count, actual retries and retry attempt mapping, exhausted trials, and checks. `RECEIPT` preserves all attempt rows alongside the selected clean rows.

## Verification

- Focused offline driver contracts: 13/13 PASS, including exact-threshold behavior, hitched-attempt retry selection, three-retry exhaustion, and clean-only result counts.
- Python syntax: PASS.
- Documentation links: 0 broken.
- PIE and Unreal were not run by Codex; the Lead owns the runtime rerun.

No gameplay C++ or assets changed. Report the parity gate as source-updated and offline-verified until the Lead runs the driver.
