# Proposal: RPGAttackTracker Timing Coverage Gap (Mid01 & SprintFollowUp)

**Authority:** Claude directive `[C-1158]` item 1 (Proposal only, no apply).  
**Context:** Statically identified in `[X-1614]`, runtime contact positions measured in `[C-1132]`.

---

## 1. Where the Timing Table Lives
- **Struct Definitions:** `Source/OneBossFight/Player/RPGAttackTracker.h`
  - `FRPGAttackTiming` (`lines 13–71`): Defines `MoveId`, `MontageName`, `FallbackMontageName`, `MontagePath`, `CommitTime`, `ActiveStartTime`, `ActiveEndTime`, `RecoveryEndTime`, `TrackTurnRate`, `bBranchStage`, and `bAuthoredWindup`.
  - `FRPGAttackTrackerConfig` (`lines 74–84`): Contains `TArray<FRPGAttackTiming> Attacks`.
- **Table Initialization & Default Constructor:** `Source/OneBossFight/Player/RPGAttackTracker.cpp:30–109` (`FRPGAttackTrackerConfig::FRPGAttackTrackerConfig()`).
- **Lookup & Matching Engine:** `Source/OneBossFight/Player/RPGAttackTracker.cpp:122–143` (`URPGAttackTracker::FindTimingIndex`).

---

## 2. Proposed Exact Timing Rows

### Row 1: `Mid01_Anim_Montage` (Single Medium Strike)
```cpp
// Mid01: Pack medium slash observed in C-1132 with 5 contacts clustered at 0.696 - 0.795 s.
FRPGAttackTiming Mid01;
Mid01.MoveId = TEXT("Mid01");
Mid01.MontageName = TEXT("Mid01_Anim_Montage");
Mid01.FallbackMontageName = TEXT("");
Mid01.MontagePath = TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/ExampleSwordMob/Mid01_Anim_Montage.Mid01_Anim_Montage");
Mid01.CommitTime = 0.60f;        // Locks heading ~0.096 s before earliest contact (0.696 s)
Mid01.ActiveStartTime = 0.68f;   // Immediately precedes observed impact window
Mid01.ActiveEndTime = 0.82f;     // Encompasses latest observed contact (0.795 s)
Mid01.RecoveryEndTime = 1.50f;   // Blends out to neutral
Mid01.TrackTurnRate = 240.f;     // Standard tracking turn rate before commitment
Mid01.bBranchStage = false;
Mid01.bAuthoredWindup = true;    // MANDATORY: Prevents UpdateTelegraph from artificially slowing down playback
Attacks.Add(Mid01);
```

### Row 2: `GS_SprintAttackFollowUp_Montage` (Dual-Contact Sprint Follow-Up)
```cpp
// GS_SprintAttackFollowUp: Sprint follow-up observed in C-1132 with two contacts: 0.070 s and 0.456 s.
FRPGAttackTiming SprintFollowUp;
SprintFollowUp.MoveId = TEXT("SprintFollowUp");
SprintFollowUp.MontageName = TEXT("GS_SprintAttackFollowUp_Montage");
SprintFollowUp.FallbackMontageName = TEXT("");
SprintFollowUp.MontagePath = TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_SprintAttackFollowUp_Montage.GS_SprintAttackFollowUp_Montage");
SprintFollowUp.CommitTime = 0.00f;        // Instant commit: first strike contacts at 0.070 s
SprintFollowUp.ActiveStartTime = 0.05f;   // Immediately precedes hit 1
SprintFollowUp.ActiveEndTime = 0.50f;     // Encompasses hit 2 (0.456 s)
SprintFollowUp.RecoveryEndTime = 1.20f;   // Recovery
SprintFollowUp.TrackTurnRate = 120.f;
SprintFollowUp.bBranchStage = false;
SprintFollowUp.bAuthoredWindup = true;    // MANDATORY: Must never apply CVarRPGCloseTelegraph scaling
Attacks.Add(SprintFollowUp);
```

---

## 3. Systems That Consume These Timings

1. **Yaw Commitment & Steering (`RPGAttackTracker.cpp:380–430`):**
   - Before `CommitTime`: Turns boss towards player at `TrackTurnRate`.
   - Between `CommitTime` and `ActiveEndTime`: Heading is captured and locked (`MaxYawDrift` enforcement), preventing the boss from pivoting mid-swing.
2. **Telegraph & Play-Rate Scaling (`RPGAttackTracker.cpp:314–349`):**
   - If `bAuthoredWindup == false`, `UpdateTelegraph` dynamically slows down the montage so windup matches `CVarRPGCloseTelegraph` (0.4s). Marking `bAuthoredWindup = true` bypasses this distortion.
3. **Parry Deduplication Key (`RPGPackParryContact.cpp:76–80, 222`):**
   - When tracked, `CurrentAttackKey` returns `RPGPackParry::BuildAttackKey(Generation, BossId, MoveId, Instance, ...)`, promoting contacts from the untracked centisecond-quantized key space (`G|B|U|T`) to the exact tracked instance key space (`G|B|M|I`).
4. **Diagnostic & Trace Telemetry (`RPGTraceAudit.cpp:201–202` & `LogRPGAttack`):**
   - `RPGTraceAudit` reports the concrete `MoveId` instead of generic `pack` / instance `-1`.
   - `LogRPGAttack` records formal phase lifecycle (`Windup -> Committed -> Active -> Recovery -> None`).

---

## 4. Risks and Complications of Adding Them

1. **Multi-Hit Window Bridging on Sprint Follow-Up:**
   - `FRPGAttackTiming` only supports a single `[ActiveStartTime, ActiveEndTime]` interval.
   - For `GS_SprintAttackFollowUp_Montage`, contacts land at `0.070 s` and `0.456 s`. Bridging this as `0.05–0.50 s` forces yaw lock across the entire 450 ms interval, freezing the boss's orientation across the dead space between the two swings.
2. **Artificial Play-Rate Distortion:**
   - If `bAuthoredWindup` were accidentally left `false`, `URPGAttackTracker::UpdateTelegraph` would downscale play rate during windup to stretch it to `0.40 s`. For an attack contacting at `0.07 s`, this would severely disrupt combat responsiveness.
3. **Root-Motion / Steering Conflicts:**
   - `GS_SprintAttackFollowUp_Montage` is initiated during or after sprinting. If the pack AI relies on root-motion translation/rotation during this attack, the tracker's forced yaw locking (`Actor->SetActorRotation`) could cause unnatural sliding or snapping.
4. **Test Baseline & Contract Impact:**
   - `Source/OneBossFight/Tests/RPGPackParryContactTests.cpp:68–73` explicitly uses `Mid01_Anim_Montage` as the canonical test fixture for **untracked** attack keys (`NAME_None`, centisecond-quantized). Registering `Mid01` into native defaults would invalidate the conceptual separation in existing characterization tests.
   - Any test asserting `RPGBossAttackTrackerAdapters::IsNativeDefault()` or checking `Attacks.Num()` will require synchronization.
