# AG-17: Content and Animation Review of Codex WP8 and WP9 Drafts

**Document ID:** `AG17_STEP2_STEP3_CONTENT_REVIEW`  
**Author:** Antigravity (Visual & Technical Animation Investigator)  
**Parent Work Order:** `ANTIGRAVITY_WORK_ORDER_04.md` (`AG-17`)  
**Target Codebase Drafts:**  
- `Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Player/RPGEncounterBinding.h/.cpp` (WP-8)  
- `Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGTimelineCompiler.h/.cpp` (WP-9)  
- `Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGShadowCompare.h/.cpp` (WP-9)  
- `Docs/BossCombatReview/Execution/Codex/WP8_IMPLEMENTATION_REPORT.md`  
- `Docs/BossCombatReview/Execution/Codex/WP9_IMPLEMENTATION_REPORT.md`  
**Status:** DELIVERED (6 Concrete Verified Findings)  

---

## 1. Executive Summary

This independent technical art and animation audit investigates the runtime consequences of Codex's Step 2 (`RPGEncounterBinding`) and Step 3 (`RPGTimelineCompiler`, `RPGShadowCompare`) drafts.

While the drafts exhibit commendable discipline regarding memory ownership and read-only observation, they contain **severe animation architectural blindspots**. Specifically:
1. The compiler unconditionally rejects existing live pack montages whose state notifies extend beyond sequence length.
2. The playback adapter fails on multi-clip composite montages (such as the A2 overhead slam trio).
3. The cursor treats legitimate looping stances (such as the variable apex hold and dormant idle) as uninferrable `INCONCLUSIVE` failures.
4. The system overlooks critical animator-guaranteed geometric invariants that cannot be verified by C++ code alone.

Six concrete findings with exact file and line numbers are detailed below.

---

## 2. Granular Content & Animation Findings

### FINDING 1: Multi-Clip Composite Montage Truncation (`RPGShadowCompare.cpp:44-50` & `62-65`)
- **Source Lines:**
  ```cpp
  // RPGShadowCompare.cpp:44-48
  if (!Montage->SlotAnimTracks.IsEmpty() && !Montage->SlotAnimTracks[0].AnimTrack.AnimSegments.IsEmpty())
  {
      S.Slot = Montage->SlotAnimTracks[0].SlotName;
      if (const UAnimSequenceBase* Clip = Montage->SlotAnimTracks[0].AnimTrack.AnimSegments[0].GetAnimReference())
      {
          S.FirstSegmentAsset = Clip->GetPathName();
      }
  }
  ```
- **The Defect:** In `CaptureAfterTracker`, `FirstSegmentAsset` is hardcoded to `AnimSegments[0]`. In `FPlaybackAdapter::Observe` (lines 62-65), the incoming snapshot is matched against precompiled artifacts strictly via:
  ```cpp
  if (Artifact->Key.AssetPath != S.SourceAsset && Artifact->Key.AssetPath != S.FirstSegmentAsset) continue;
  ```
- **Animation Consequence:** Composite montages like `AM_Boss01_A2_OverheadSlam` contain three sequential segments: `AN_Boss01_A2_Raise` (Segment 0), `AN_Boss01_A2_ApexHold` (Segment 1), and `AN_Boss01_A2_Slam` (Segment 2). When the boss enters Section 2 (`ApexHold`) or Section 3 (`Slam`), `FirstSegmentAsset` remains permanently tied to Segment 0 (`AN_Boss01_A2_Raise`). The playback adapter will fail to match the artifact, dropping 100% of samples across the apex hold and downward slam (`++Dropped`).

---

### FINDING 2: Unconditional Compilation Abort on Live Pack Montages (`RPGTimelineCompiler.cpp:45`)
- **Source Line:**
  ```cpp
  // RPGTimelineCompiler.cpp:45
  if (... || W.Begin < 0. || W.End <= W.Begin || W.End > Length)
  {
      Result.Errors.Add(TEXT("invalid/duplicate window"));
  }
  ```
- **The Defect:** Codex enforces that every window's end time must satisfy $W.\text{End} \le \text{Length}$.
- **Animation Consequence:** In Unreal Engine, animators routinely place `ANS_DisableMovement_C` across the entire montage timeline, extending into the blend-out window. In the live export [`montage_notifies_2026-10-25.txt`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/Evidence/exports/montage_notifies_2026-10-25.txt):
  * `GS_ChargedAttack_Montage` (Line 29): `ANS_DisableMovement_C` is placed at `0.000 s` for `4.933 s`, while sequence length is `3.400 s` ($4.933 > 3.400$).
  * `GS_SprintAttackFollowUp_Montage` (Line 42): `ANS_DisableMovement_C` is placed at `0.000 s` for `3.400 s`, while sequence length is `1.867 s` ($3.400 > 1.867$).
- **Impact:** Codex's compiler will unconditionally **REJECT** the pack's primary attack montages as invalid! Clamping $W.\text{End} = \min(\text{Length}, W.\text{End})$ is strictly required.

---

### FINDING 3: Variable Apex Hold Looping Blinds Shadow Comparator (`RPGShadowCompare.cpp:71-73` vs `RPGTimelineCompiler.cpp:94`)
- **Source Lines:**
  ```cpp
  // RPGShadowCompare.cpp:72-73
  O.Traversal = O.Rate < 0.f ? ETraversal::Reverse : (Same && O.Current < O.Previous ? ETraversal::Unknown : ETraversal::Forward);
  
  // RPGTimelineCompiler.cpp:94
  if (!Forward || !Contiguous || ...)
  {
      R.Limitation = TEXT("reverse/loop/jump/gap/midclip... path not inferred"); return R;
  }
  ```
- **The Defect:** When a looping montage wraps around, $O.\text{Current} < O.\text{Previous}$ evaluates to true. Codex assigns `ETraversal::Unknown`, causing `FCursor::Advance` to abort crossing evaluation.
- **Animation Consequence:** The core mechanic of `ANM-003` (Variable Hold) and `AN_Boss01_DormantIdle` relies on looping sections. Because every loop cycle triggers `ETraversal::Unknown`, the shadow comparator completely drops observation during holding stances. Variable apex hold variants cannot be monitored or verified under this logic.

---

### FINDING 4: Secondary Track & Additive Blend Blindspot (`RPGShadowCompare.cpp:33-35`)
- **Source Lines:**
  ```cpp
  // RPGShadowCompare.cpp:33-35
  const UAnimMontage* Montage = Anim ? Anim->GetCurrentActiveMontage() : nullptr;
  ```
- **The Defect:** Querying `AnimInstance->GetCurrentActiveMontage()` returns only the single primary montage playing on the main slot.
- **Animation Consequence:**
  * When a montage blends out over 0.25s into another attack, the expiring montage is ignored.
  * In `AWR-008`, the boss plays an additive upper-body posture flare (`AN_Boss01_Adapt_Tell`) on an upper-body slot track while moving.
  * In Phase transitions (`AN_Boss01_PhaseRoar`), hit reactions can play on secondary layered slots.
  * All notifies firing on secondary slot tracks or blending-out clips are invisible to `CaptureAfterTracker`.

---

### FINDING 5: Blindness to Skeleton & Retargeting Invariants
- **Source File:** `Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Player/RPGEncounterBinding.cpp:30-45`
- **The Defect:** The binding manifest (`FRPGParticipantConfig`) verifies struct string presence, but performs zero validation of the underlying `USkeleton`.
- **Animation Consequence:** In Unreal Engine, binding an animation montage authored for `SK_CombatMannequin` to a mesh bound to another skeleton (or having mismatched bone names) causes silent failure: the montage plays, `Montage_GetPosition` advances, but the character mesh remains frozen in a reference T-pose or deforms catastrophically. The runtime compiler cannot detect whether bone tracks actually drive mesh vertices.

---

### FINDING 6: Invariants Animators Must Guarantee (Uncheckable by C++ Code)
Because the C++ compiler operates strictly on abstract timing floats, technical animators must guarantee the following physical invariants via authoring standards (`AG10_IMPORT_STANDARD.md`):
1. **Foot Grounding Clearance:** Both feet must remain within $[0.0, 2.0\text{ cm}]$ of floor Z during stance holds and turns (`AN_Boss01_A2_Raise`, `AN_Boss01_Turn_*`). C++ cannot detect floating or floor clipping.
2. **Hilt Separation Invariance:** Left and right hand IK markers on the two-handed greatsword hilt must maintain fixed separation ($18.0\text{--}22.0\text{ cm}$). C++ cannot detect broken hand placement on the weapon.
3. **Trace-to-Mesh Alignment:** Collision sweep notifies (`ANS_CollisionTrace_C`) must physically encompass the greatsword blade. If an animator moves the blade in DCC without updating the notify markers, the weapon visually passes through the player with zero hit detection.
4. **Root Motion Vector Parity:** Root bone translation speed in DCC must match the character movement component velocity to prevent visual foot sliding.

---

## 3. Evidence and Limits Table

| Finding / Topic | Source File / Anchor | Engine Reality | Impact / Required Fix |
| :--- | :--- | :--- | :--- |
| **1. Multi-Clip Truncation** | `RPGShadowCompare.cpp:44` | Hardcoded `AnimSegments[0]` | Fails on composite montages; segment index must track current position. |
| **2. Notify Clamping Abort** | `RPGTimelineCompiler.cpp:45` | `GS_ChargedAttack` has 4.93s notify | Rejects pack attacks; must clamp $End \le Length$ instead of rejecting. |
| **3. Looping Stance Blindspot**| `RPGShadowCompare.cpp:72` | Loop wrap sets `ETraversal::Unknown` | Aborts shadow comparison during apex holds and dormant idles. |
| **4. Secondary Slot Blindness**| `RPGShadowCompare.cpp:34` | Single active montage query | Drops additive tells (`AN_Boss01_Adapt_Tell`) and blend-out notifies. |
| **5. Skeleton Blindness** | `RPGEncounterBinding.cpp:35` | No skeleton compatibility check | Silent T-pose failure if skeleton reference diverges. |
| **6. Authoring Invariants** | `AG10_IMPORT_STANDARD.md` | Abstract floats cannot prove physics | Footing, hand grip, and mesh alignment require DCC validation. |
