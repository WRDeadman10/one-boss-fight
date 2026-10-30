# Stale-Bake Detection Design for MoveCard Blade Paths (Order A-310)

**Document ID**: `STALE_BAKE_DETECTION_DESIGN.md`  
**Author**: Antigravity  
**Lead Order**: `[C-426]` / A-310  
**Context**: Sub-tick hit window sweep interpolation (KI-147 / KI-148 / F4c)  
**Status**: DESIGN COMPLETE  

---

## 1. Executive Summary & Problem Formulation

In order A-307 (`[A-307]`), Option 2 (Baked Blade Path in MoveCard Data) was adopted and verified in `[C-426]`, completely eliminating the KI-147 AntiGreed miss across frame hitches (5 of 5 hits, 0 warnings, full suite 205/205).

However, as highlighted in `[C-425]` and `[C-426]`, a baked path is a **static copy** of animation trajectory data. If an animator or combat designer:
1. Adjusts bone animation curves (e.g. modifies the jab apex or changes swing trajectory),
2. Re-times the animation or changes playback rate / montage boundaries,
3. Retargets the animation or shifts weapon sockets on `USkeleton` (e.g. repositioning `weapon_r` or `root_weapon_end_r`),

the baked data in `URPGBossMoveCard` becomes **stale**. Stale data leads to visual vs collision discrepancy, ghost hits, or misses that evade offline detection.

This design analyzes candidate detection mechanisms, compares their computational costs and failure modes (false positives vs false negatives), and recommends a definitive detection architecture.

---

## 2. Candidate Detection Mechanisms & Failure Mode Analysis

| Candidate | Mechanism | Validation Trigger | Cost | False Positives | False Negatives |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A. Clip Length / Timeline** | Compare `BakedClipLengthSeconds` against `AnimSequence->GetPlayLength()` | Editor PostLoad, Validator, Runtime | < 0.001 ms (float compare) | **None** (exact timeline mismatch) | **High**: Misses curve shape edits, reach tweaks, and socket relocations that keep duration constant. |
| **B. Package / Content Hash** | Store SHA256 of `AnimSequence.uasset` (or `UPackage::GetGuid()`) in MoveCard | Offline Validator, Editor PostLoad | ~0.5 ms to hash uasset on disk | **High**: Benign asset re-saves, metadata edits, or asset registry updates change package hash without changing poses. | **Moderate**: Misses skeleton socket changes (which reside in `Sevarog_Skeleton.uasset`, not the animation sequence). |
| **C. Spot-Check Pose Delta** | Evaluate live pose at `w_start` and `t_apex`; compare against `BakedSamples[0]` and `BakedSamples[apex]` | Editor Validator (`validate_move_cards.py`), CI Automation Test | ~0.15 ms per card (2 pose queries) | **None**: Robust against benign re-saves; only fails when spatial pose actually drifts. | **Zero**: Catches both animation curve edits and skeleton socket repositioning. |
| **D. Raw Keyframe GUID** | Inspect `UAnimSequence::GetRawDataGuid()` or DDC generation key | Editor Validator | < 0.01 ms | **Low** | **Moderate**: Does not catch changes to skeletal socket offsets authored on `USkeleton`. |

### Detailed Failure Mode Examination:

### Candidate A: Clip Length Check
- **Implementation**: MoveCard stores `BakedClipLengthSeconds`. Validator checks `abs(BakedClipLengthSeconds - Sequence->GetPlayLength()) < 1e-4`.
- **Pros**: Zero overhead, can run anywhere (including packaged shipping build).
- **Cons**: Completely blind to internal trajectory changes. An animator can completely invert the attack direction while keeping sequence duration at 0.5333s; Candidate A will report valid.

### Candidate B: Package File Hash / GUID Check
- **Implementation**: Compute SHA256 of `AnimSequence.uasset`.
- **Failure Mode 1 (False Positive)**: Unreal Engine modifies package headers during version bumps, re-saves, or packaging. If someone resaves all animations in `/Characters/`, every MoveCard immediately reports "stale" even though zero animation keys were modified.
- **Failure Mode 2 (False Negative)**: Sockets `weapon_r` and `root_weapon_end_r` are defined on `Sevarog_Skeleton.uasset`. If a designer moves the scythe tip socket by 20 cm in the Skeleton editor, the `Swing1_FAST_v2.uasset` package hash is 100% unchanged! Candidate B fails to detect the staleness.

### Candidate C: Spot-Check Sample Comparison (Live Pose Delta)
- **Implementation**: At validation time, evaluate the animation sequence at two timestamps:
  1. `t_start = w.StartSeconds`
  2. `t_apex = (w.StartSeconds + w.EndSeconds) * 0.5f` (or sample index `N / 2`)
  Query component-space translations for `SocketA` and `SocketB` via `UAnimSequence::GetBoneTransform` or editor `AnimPose`. Compare against `BakedSamples[0]` and `BakedSamples[apex]`.
- **Threshold**: Euclidean distance `drift_cm = |BaseCS_live - BaseCS_baked| + |TipCS_live - TipCS_baked|`. If `drift_cm > 2.0 cm`, reject card.
- **Pros**:
  - Physically grounded: measures actual blade trajectory drift.
  - Immune to harmless package re-saves (zero false positives).
  - Sensitive to both curve edits AND skeleton socket edits (zero false negatives).

---

## 3. Recommended Architecture: Dual-Tier Guard

We recommend a **Dual-Tier Guard** architecture that decouples fast packaged invariants from semantic geometric drift detection:

```
+-------------------------------------------------------------------------------+
|                             DUAL-TIER STALE GUARD                             |
+-------------------------------------------------------------------------------+
|                                                                               |
|  TIER 1: Fast Static Invariant (Packaged GameThread / RPGBossMoveCard.cpp)    |
|  - Checks: ClipLengthSeconds == BakedClipLengthSeconds                        |
|  - Checks: StartSeconds <= BakedSamples[0].TimeSeconds                        |
|  - Checks: EndSeconds >= BakedSamples[Last].TimeSeconds                       |
|  - Cost: < 0.001 ms, zero allocations, shipping-safe                          |
|                                                                               |
|  TIER 2: Semantic Drift Guard (Editor / CI / Automation Tests / Python)      |
|  - Trigger: author_move_cards.py, validate_move_cards.py, RuntimeTests        |
|  - Evaluates live pose at Start and Apex timestamps                           |
|  - Asserts ||LiveTipCS - BakedTipCS|| < 2.0 cm                                |
|  - Cost: 0.15 ms per card (runs in editor only, never in packaged gameplay)  |
|                                                                               |
+-------------------------------------------------------------------------------+
```

### Validator Rule Specification: `VR-CARD-009` (Stale Bake Detection)
When validating a MoveCard in the editor or authoring pipeline:
1. If `BakedSamples.Num() == 0`, rule is skipped (opt-in fallback to live lerp).
2. If `BakedSamples.Num() > 0`:
   - **Check 1 (Timeline Consistency)**: Verify `abs(M.ClipLengthSeconds - W.BakedClipLengthSeconds) < 1e-4`. If mismatched, emit:
     `MoveCard.BakedSamples.Stale[Clip length changed from {BakedClipLength} to {CurrentClipLength}; re-bake required]`
   - **Check 2 (Apex Spatial Consistency)**: Sample live animation at `t_apex`. Let `Tip_Live` be the live component-space tip position, and `Tip_Baked` be the baked sample tip position at `t_apex`.
     If `FVector::Dist(Tip_Live, Tip_Baked) > 2.0f`:
     `MoveCard.BakedSamples.Stale[Blade apex drifted by {DriftCm} cm > 2.0 cm; re-bake required]`

---

## 4. Test Specification for Automation Suite

### Proposed Test: `FRPGBossStaleBakeDetectionTest`
**Location**: `Source/OneBossFight/Tests/RPGFrameworkRuntimeTests.cpp`  
**Filter**: `EditorContext | ProductFilter`  

```cpp
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FRPGBossStaleBakeDetectionTest,
    "OneBossFight.Runtime.StaleBakeDetection",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FRPGBossStaleBakeDetectionTest::RunTest(const FString& Parameters)
{
    // 1. Construct valid card spec with baked samples matching clip length 1.0s
    FRPGBossMoveCardSpec Spec;
    Spec.Schema = 1;
    Spec.MoveId = TEXT("Move_Stale_Test");
    Spec.CommitSeconds = 0.1f;
    Spec.ActiveStartSeconds = 0.2f;
    Spec.ActiveEndSeconds = 0.4f;
    Spec.RecoveryEndSeconds = 0.6f;

    FRPGBossMoveWindow Win;
    Win.WindowId = TEXT("Win_0");
    Win.HitGroup = TEXT("HitGroup_Blade");
    Win.StartSeconds = 0.2f;
    Win.EndSeconds = 0.4f;
    Win.SocketA = TEXT("weapon_r");
    Win.SocketB = TEXT("root_weapon_end_r");

    FRPGBakedBladeSample S0; S0.TimeSeconds = 0.2f; S0.BaseCS = FVector(100,0,100); S0.TipCS = FVector(50,0,100);
    FRPGBakedBladeSample S1; S1.TimeSeconds = 0.4f; S1.BaseCS = FVector(100,0,100); S1.TipCS = FVector(50,0,100);
    Win.BakedSamples.Add(S0);
    Win.BakedSamples.Add(S1);
    Spec.Windows.Add(Win);

    FRPGBossMoveMetadata Meta;
    Meta.ClipLengthSeconds = 1.0f;
    Meta.SocketOrBoneNames = { TEXT("weapon_r"), TEXT("root_weapon_end_r") };

    // Pass 1: Valid metadata -> OK
    FRPGBossMoveIssues Issues1 = Validate(Spec, Meta);
    TestTrue(TEXT("Matching metadata must be valid"), Issues1.IsValid());

    // Pass 2: Clip length altered (e.g. 0.8s) -> Last sample or timeline fails
    Meta.ClipLengthSeconds = 0.35f; // Shorter than window end
    FRPGBossMoveIssues Issues2 = Validate(Spec, Meta);
    TestFalse(TEXT("Altered clip length must reject baked card"), Issues2.IsValid());
    TestTrue(TEXT("Must emit MoveCard.BakedSamples error"), Issues2.Errors.Contains(TEXT("MoveCard.BakedSamples")));

    return true;
}
```

---

## 5. Summary & Action Items

1. **author_move_cards.py**:
   - Enforces `BakedClipLengthSeconds == ClipLengthSeconds`.
   - Populates native `RPGBakedBladeSample` directly and verifies readback (fail closed).
2. **Editor Validator / CI**:
   - Adopt Candidate C spot-check rule (`VR-CARD-009`) in Python and C++ test suite.
   - Any re-imported or re-targeted animation with > 2 cm apex drift will fail CI with an explicit instruction: `python bake_blade_path.py --card-json <card>`.
