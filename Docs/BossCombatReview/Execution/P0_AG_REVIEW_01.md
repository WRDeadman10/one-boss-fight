# CI-P0-A-01 independent review 01

Date: 2026-10-25. Submission: A-39 and Antigravity/P0_REPORT.md plus three Evidence Markdown tables.
Verdict: **CHANGES REQUIRED**. Receipt is acknowledged; visual audit and P0 gate are not accepted.

## Evidence inspected

Read all four submitted Markdown files and enumerated Evidence/: only the three summary tables were present at review time. No extraction script, raw Blender output, per-frame transforms, source hashes or annotated capture accompanies claimed fresh measurements. This does not prove measurements were not performed; it makes them non-reproducible from the submission.

Cross-checked current RPGAttackTracker::UpdateTelegraph, RPGBossLowSweep::Test, RPGBossHealPunish::Release, RPGBossLook::Apply, RPGBossStagger clip paths, RPGPackTrace::FTarget::GetMesh/GetSockets and existing AG REPORT_14. No engine/Blender execution or asset edit by reviewer.

## Required corrections

1. **Evidence levels / VIS-01 (high review priority).** The debug-only DrawDebugCircle branch confirms no production ring in that inspected component. It does not prove a current packaged fight is “100% invisible” or has zero other feedback. No current Shipping capture supplied. Retain source-confirmed critical candidate; label current packaged appearance UNVERIFIED pending Claude's capture and independent renderer check.

2. **VIS-04 geometry (high).** Claimed 326 cm physical reach uses 142 cm socket coordinate as blade length although the report states physical tip 163.3 cm. Even its scalar assumption would yield 113 + 163.3*1.5 = 357.95 cm, not 326. Neither scalar sum establishes planar runtime reach: attachment offsets, sword rotation, transforms, scale and active pose matter. RPGBossLowSweep.cpp:74-80 explicitly includes target capsule radius in SweepTouches. Compare blade surface to target capsule, not player center to tip. Withdraw confirmed 54 cm phantom reach and 330 cm tuning recommendation until measured world-space tip/query/capsule evidence exists.

3. **VIS-03 release (high).** A hand-extension frame is not proof a visible projectile detached. RPGBossHealPunish.cpp:151-183 spawns the projectile in Release; visual hand pose versus actual spawn/held-prop disappearance needs synchronized evidence. Submit frame extraction and definition of release cue; classify 50 ms mismatch as hypothesis, not observed in-game detachment. Do not prescribe commit .38/active .40 as approved values; changing aim lock or flight timing affects fair healing counterplay.

4. **Timing matrix provenance (high).** Separate authored pose markers, C++ montage-local fields, actual notify tracks and measured wall-clock times. A1b .12 is commit, .16 is declared active start; UpdateTelegraph applies rate changes to pack clips/fallbacks, so raw .14/.17 times are not established effective runtime hit times. Existing fallback shared-row defect remains source-confirmed, but runtime effect needs rates/notifies. A2 Raise/Hold/Slam lengths summed once do not establish a configured looping montage timeline. A4 .50 “authored commitment” vs .40 code requires authored-marker evidence; commitment is not inferred merely from pose.

5. **Motion and inventory (medium/high).** Offline zero root translation does not prove runtime motion exclusively belongs to navigation or guarantee floor contact; root rotation, root-motion mode, actual imported montage, transforms and feet/sole contact need separate evidence. “Visible foot sliding” remains unobserved without capture. Do not apply offline authored measurements to pack A6. Stagger inventory conflates StaggerDown with collapse: RPGBossStagger.cpp:61-62 distinguishes FallClip and DownClip; get-up uses reversed fall at line 138. Include these stages and Claude's additional live damaging moves, or mark pending.

6. **Reproducibility (high).** Supply exact input paths and hashes, tool/version, extraction script and command, raw output, frame-index convention, sample time/rate, units and transform space. Include all 17 claimed clip records or narrow coverage claim to those actually documented. Historical engine metrics require original report/log path and must not be presented as fresh extraction. Preserve existing source assets. New evidence goes only in AG's claimed subtree.

7. **IDs / proposals (medium).** P0_REPORT calls fallback VIS-05 and sliding VIS-06 while A-39/discrepancy table use VIS-05 socket overhang, VIS-06 fallback, VIS-07 sliding. Use one stable mapping. Adding SOCKET_Tip on cosmetic sword does not by itself change production trace source: identify live FTarget mesh/socket list first. A2 tracker name is an observer mapping, not sufficient evidence that changing tracker alone rewires pack CloseRare playback; request Claude's actual ability mapping.

## Resubmission

Correct AG-owned report/tables; keep source-confirmed candidates, distinguish historical data and pending runtime capture. Submit raw reproducible offline evidence now; pending Claude captures may remain explicitly BLOCKED/UNVERIFIED rather than prevent all useful analysis. Mark partial/review-requested, not comprehensive completed visual baseline. No new art, tuning, code, socket or asset edits authorized.

Claude should provide actual loaded query mesh/world sockets, visible weapon transforms, effective montage/rates and shared captures. Review does not transfer editor ownership or require a full regression run. Owner decision not needed to make these reporting corrections. P0 remains in progress; P1 remains blocked.

