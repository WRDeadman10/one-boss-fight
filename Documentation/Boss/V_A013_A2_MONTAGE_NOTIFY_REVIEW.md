# V-A013: A2 Montage Notify and Timing Review

**Author:** Antigravity (Offline Quality, Audit & Asset Lane)
**Date:** 2026-11-05
**Scope:** Verification of composite montage `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A2` against the production tracker row (`FRPGAttackTrackerConfig::A2`) in `Source/OneBossFight/Player/RPGAttackTracker.cpp`.
**Sources:** Source/OneBossFight/Player/RPGAttackTracker.cpp:30-108, Content/OneBossFight/Boss01/Animations/AM_Boss01_A2.uasset

---

## 1. Executive Summary

- **Status:** **PASS** (all key combat timing deltas \(\le\) 7 ms).
- Composite montage `AM_Boss01_A2` is assembled from 3 authored clips:
  - `AN_Boss01_A2_Raise` (0.600 s)
  - `AN_Boss01_A2_ApexHold` (1.167 s)
  - `AN_Boss01_A2_Slam` (1.367 s)
- Total Composite Duration: **3.134 s** (vs tracker `RecoveryEndTime` 3.140 s; \(\Delta = -6\text{ ms}\)).
- Floor contact & damage active window start: **1.937 s** (vs tracker `ActiveStartTime` 1.930 s; \(\Delta = +7\text{ ms}\)).
- Heading commitment lock: **1.687 s** (vs tracker `CommitTime` 1.680 s; \(\Delta = +7\text{ ms}\)).
- All timing discrepancies remain under half a single frame at 60 Hz (\(< 8.33\text{ ms}\)).

---

## 2. Timing Alignment Matrix

| Timing Parameter | Tracker Row (`GS_ChargedAttack_Montage`) | Composite Montage (`AM_Boss01_A2`) | Delta (\(\Delta\)) | Frame Delta (@60 FPS) | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Windup Phase 1 (Raise)** | 0.000 s – 0.600 s | 0.000 s – 0.600 s | 0.000 s | 0.00 frames | EXACT |
| **Windup Phase 2 (Hold)** | 0.600 s – 1.680 s | 0.600 s – 1.687 s | +0.007 s | +0.42 frames | PASS (\(< 1\text{ frame}\)) |
| **Commit Point (`CommitTime`)** | **1.680 s** | **1.687 s** (end of hold - 80 ms) | **+0.007 s** | **+0.42 frames** | **PASS** |
| **Active Start (`ActiveStartTime`)**| **1.930 s** | **1.937 s** (slam impact frame) | **+0.007 s** | **+0.42 frames** | **PASS** |
| **Active End (`ActiveEndTime`)** | **2.110 s** | **2.107 s** (trace window close) | **-0.003 s** | **-0.18 frames** | **PASS** |
| **Recovery Phase End** | **3.140 s** | **3.134 s** (montage blend out) | **-0.006 s** | **-0.36 frames** | **PASS** |
| **Clip Total Length** | 3.400 s (truncated by blend out) | 3.134 s | -0.266 s | N/A (blend at 3.14) | PASS |

---

## 3. Anim Notify Verification

1. **`Notify_AttackCommit`:**
   - Authored at **1.687 s** (within `AN_Boss01_A2_ApexHold` at 1.087 s relative).
   - Fires heading rotation freeze via `URPGAttackTracker::HandleCommit`.
2. **`Notify_ActiveStart` / Weapon Trace Open:**
   - Authored at **1.937 s** (within `AN_Boss01_A2_Slam` at 0.170 s relative).
   - Exactly matches visual sword impact on ground.
3. **`Notify_ActiveEnd` / Weapon Trace Close:**
   - Authored at **2.107 s** (within `AN_Boss01_A2_Slam` at 0.340 s relative).
   - Coincides with the shockwave launch trigger on `URPGBossShockwave`.
4. **`Notify_RecoveryBlend`:**
   - Authored at **2.884 s** (0.250 s blend-out duration brings animation to idle at 3.134 s).

---

## 4. D5 Parity and Deployment Recommendation

- `AM_Boss01_A2` is saved on disk at `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A2`.
- Per **[C-906]**, **[C-908]**, and **Queue V V-C031**, `AM_Boss01_A2` remains **UNWIRED** in production C++ components until Codex delivers the optional tracker clip wiring plan (`V-C031`) and Lead Claude performs live before/after telegraph pair comparison.
- When wired, fallback to `GS_ChargedAttack_Montage` must remain the default when `bUseLegacyStartup=true` or when the authored override is empty.
