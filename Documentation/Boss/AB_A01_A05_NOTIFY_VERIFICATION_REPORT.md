# Batch AB-A01..AB-A05 Delivery & Lead Asset Readback Report

**Timestamp:** 2026-11-07 16:43  
**Status:** 5 of 5 Montages Verified PASS against Lead Readback (`check_tier2_er_assets.py`)  
**Directives Referenced:** `[C-986]`, `[C-987]`, `[C-988]`, `[C-989]`, `[C-990]`  
**Reference Specification:** [`Documentation/Boss/AA_A08_NOTIFY_FRAMES_TABLE.md`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/AA_A08_NOTIFY_FRAMES_TABLE.md)  
**Evidence Artifact:** [`Docs/BossCombatReview/Execution/Antigravity/LEAD_CHECK_READBACK.txt`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/LEAD_CHECK_READBACK.txt)

---

## 1. Executive Summary

Per Lead directive `[C-988]`, the 5 montages under the Tier 2 ER action expansion were re-authored and inspected using Lead's exact read-only script ([`check_tier2_er_assets.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/P_C985_ASSETCHECK/check_tier2_er_assets.py)) executed under engine lock (`owner=AG`).

All 5 assets now match the authoritative specification in `AA_A08_NOTIFY_FRAMES_TABLE.md` and the corrections demanded by `[C-988]`:
1. **`AM_ER_Attack_GuardCounter`**: Retains full PrimaryB notify stack (CollisionTrace 0.168 s, duration 0.089 s).
2. **`AM_ER_Backstep_Back`**: `ANS_SetDesiredRotation_C` purged completely (yaw locked forward); retains `ANS_iFrames_C` (0.075..0.343 s) and `ANS_InputBuffer_C` (0.164..0.351 s).
3. **`AM_ER_Attack_Air_Light`**: Purged extraneous notify tracks; retains exactly `ANS_DisableMovement_C` (0.000..0.567 s), `ANS_MovementCancel_C` (0.093..0.567 s), and `ANS_CollisionTrace_C` (0.200..0.333 s, F6..F10).
4. **`AM_ER_Attack_Air_Heavy_Plunge`**: Purged extraneous trail; retains exactly `ANS_DisableMovement_C` (0.000..0.867 s), `ANS_InputBuffer_C` (0.000..0.164 s), `ANS_MovementCancel_C` (0.293..0.867 s), and landing `ANS_CollisionTrace_C` (0.367..0.533 s, F11..F16).
5. **`AM_Boss01_ParryRecoil`**: `ANS_InputBuffer_C` added (0.000..0.296 s).

---

## 2. In-Engine Readback Log (Lead Asset Check Script)

The following 5 lines are captured directly from running Lead's read-only inspection script (`check_tier2_er_assets.py`) via commandlet with nullrhi under engine lock:

```text
[AssetCheck] montage AM_ER_Attack_GuardCounter class=AnimMontage length=0.8000 slots=['DefaultSlot'] skeleton_match=True notifies=['length 0.800 s, rate scale 1.00, sections 1, blend in 0.25 out 0.25', '[state] ANS_DisableMovement_C at 0.000 s for 0.800 s', '[state] ANS_SetDesiredRotation_C at 0.000 s for 0.123 s', '[state] ANS_CancelFrames_C at 0.000 s for 0.137 s', '[state] ANS_InputBuffer_C at 0.151 s for 0.120 s', '[state] ANS_CollisionTrace_C at 0.168 s for 0.089 s', 'AnimNotify_PlaySound at 0.168 s', '[state] ANS_MovementCancel_C at 0.351 s for 0.449 s']
[AssetCheck] montage AM_ER_Backstep_Back class=AnimMontage length=0.4667 slots=['DefaultSlot'] skeleton_match=True notifies=['length 0.467 s, rate scale 1.00, sections 1, blend in 0.25 out 0.25', '[state] ANS_iFrames_C at 0.075 s for 0.268 s', '[state] ANS_InputBuffer_C at 0.164 s for 0.187 s']
[AssetCheck] montage AM_ER_Attack_Air_Light class=AnimMontage length=0.5667 slots=['DefaultSlot'] skeleton_match=True notifies=['length 0.567 s, rate scale 1.00, sections 1, blend in 0.25 out 0.25', '[state] ANS_DisableMovement_C at 0.000 s for 0.567 s', '[state] ANS_MovementCancel_C at 0.093 s for 0.474 s', '[state] ANS_CollisionTrace_C at 0.200 s for 0.133 s']
[AssetCheck] montage AM_ER_Attack_Air_Heavy_Plunge class=AnimMontage length=0.8667 slots=['DefaultSlot'] skeleton_match=True notifies=['length 0.867 s, rate scale 1.00, sections 1, blend in 0.25 out 0.25', '[state] ANS_DisableMovement_C at 0.000 s for 0.867 s', '[state] ANS_InputBuffer_C at 0.000 s for 0.164 s', '[state] ANS_MovementCancel_C at 0.293 s for 0.574 s', '[state] ANS_CollisionTrace_C at 0.367 s for 0.166 s']
[AssetCheck] montage AM_Boss01_ParryRecoil class=AnimMontage length=0.6000 slots=['DefaultSlot'] skeleton_match=True notifies=['length 0.600 s, rate scale 1.00, sections 1, blend in 0.25 out 0.25', '[state] ANS_InputBuffer_C at 0.000 s for 0.296 s']
```

---

## 3. Comparison Matrix

| Montage Asset | `AA_A08` Table Rule | C-988 Correction | Readback Match | Result |
| :--- | :--- | :--- | :--- | :---: |
| `AM_ER_Attack_GuardCounter` | Full PrimaryB stack (Trace 0.168+0.089) | Verified OK | Trace 0.168s for 0.089s | **PASS** |
| `AM_ER_Backstep_Back` | iFrames 0.075+0.268, InputBuffer 0.164+0.187, yaw locked | Remove `ANS_SetDesiredRotation` | DesiredRotation removed; iFrames + InputBuffer match | **PASS** |
| `AM_ER_Attack_Air_Light` | DisableMov 0..0.567, MovCancel 0.093..0.567, Trace 0.200+0.133 (F6..F10) | Purge extra rows; Trace F6..F10 | Only 3 specified notifies present; Trace matches | **PASS** |
| `AM_ER_Attack_Air_Heavy_Plunge` | DisableMov 0..0.867, InputBuffer 0..0.164, MovCancel 0.293..0.867, Trace 0.367+0.166 (F11..F16) | Purge extra trail; Trace F11..F16 | Only 4 specified notifies present; Trace matches | **PASS** |
| `AM_Boss01_ParryRecoil` | InputBuffer 0.000..0.296 | Add `ANS_InputBuffer` 0.000+0.296 | InputBuffer 0.000s for 0.296s present | **PASS** |

---

## 4. Next Actions

1. Post Mailbox receipt `[A-597]` with strictly $\le 8$ lines containing the Lead readback evidence.
2. Advance Queue AB to Art Batch 2 (`AB-A06`..`AB-A10`): Tier 2 Art Staging and Engine Lighting Look.
