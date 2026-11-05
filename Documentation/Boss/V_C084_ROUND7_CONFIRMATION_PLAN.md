# V-C084 — Round 7 performance confirmation plan

## Gate before scheduling

Wait for Round 6's complete results zip, a validated intake report, the Lead's review, and the owner's explicit selection of settings and visual-quality acceptance. Keep the current project defaults until those exist. Do not run Round 7 from the unapproved candidate table.

## Controlled confirmation

1. Use the same selected encounter, packaged configuration, map, 1920×1080 window, build identity and run method for baseline and candidate. Preserve BUILD_INFO, executable hash, active selection/manifest identity, CVars, `game.log`, `summary.json`, `frames.csv` and GPU telemetry.
2. Prefer the physical RTX 2060 Super if available. Otherwise use the owner-approved RTX 3060 proxy, record GPU/driver and physical console session, and label the result proxy evidence. Reject RDP/virtual adapters and runs without `fight_started=true`.
3. Verify CVar help and actual values before capture. Keep VSync off, uncapped, `r.DynamicRes.OperationMode=0`; check the active upscaler, NGX mode witness, primary screen-fraction upper bound and AA method on every run.
4. Warm up for 5 s, then capture three 60 s runs per profile. Interleave a TSR anchor at the start, after each four treatments and at the end as defined by the Round 6 plan. Restart between profiles if a setting persists or identity differs. Preserve failures; never replace a failed run silently.
5. Report median average FPS, p99 frame time, GPU average/p99, anchor drift, active mode and image-quality review. The absolute gate is average ≥60 FPS and p99 ≤16.67 ms; retain the separate regression comparison. If anchors drift >5%, invalidate treatment deltas and repeat after diagnosing the source.
6. An owner-approved setting is a candidate only after the measurement and visual-quality gate pass. Apply it in a separately reviewed change, then run V-C085's five matched legacy/data parity pairs.

Round 6 run procedure and conditional tuning flags are in `Documentation/BENCHKIT_README.md` and `Scripts/round6_experiments.json`. This is a plan only; no run or setting change is claimed.
