# P1 Native Special Source Addendum & Coordinate Provenance

**Document ID:** `P1_NATIVE_SPECIAL_SOURCE_ADDENDUM`  
**Date:** 2026-10-26  
**Author:** Antigravity (Visual & Technical Animation Investigator)  
**Work Order:** `Docs/BossCombatReview/Execution/ANTIGRAVITY_WORK_ORDER_06.md` (Task **AG06-1**)  
**Governing Documents & Primary Source Anchors:**  
- Requirements Baseline: [`06_REFERENCE_REQUIREMENTS.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Reference/06_REFERENCE_REQUIREMENTS.md) (SHA256: `33087a54fcd823c7213c09c5afebaea10155232dcb79d3762e6ec0ff8ae37746`)
- Cue Source Inventory (REV3): [`P1_CUE_SOURCE_INVENTORY.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/P1_CUE_SOURCE_INVENTORY.md)
- Companion Inventory JSON (REV3): [`P1_CUE_SOURCE_INVENTORY.json`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/P1_CUE_SOURCE_INVENTORY.json)
- Attack Tracker Source: [`Source/OneBossFight/Player/RPGAttackTracker.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp) (SHA256: `f2d2615f1b938aa8bf1f4ad9d7574b1876446823d83b87cd69521ca9d1153f0c`)
- Heal Punish Header: [`Source/OneBossFight/Player/RPGBossHealPunish.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossHealPunish.h) (SHA256: `fea3f2755835a25f4bc047fe2aad77c9965d009c51fc47ef319c2d70ee8d4a64`)
- Heal Punish Source: [`Source/OneBossFight/Player/RPGBossHealPunish.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossHealPunish.cpp) (SHA256: `1e63046d9c215fd0d7a5f894ee1b4539d64ddbefd9c80812cecbbae89c476906`)
- Shockwave Header: [`Source/OneBossFight/Player/RPGBossShockwave.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossShockwave.h) (SHA256: `4d1973ffe41672e8db4d52029d584f98c9b6df2f8a61cff63b2e3eee39c4d7cd`)
- Shockwave Source: [`Source/OneBossFight/Player/RPGBossShockwave.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossShockwave.cpp) (SHA256: `9632381f60e92d3f2d7cc7362883cbc03c3b258191abbbb4755a4bc9591cf3a4`)

---

## 1. Executive Summary

This addendum fulfills Task **AG06-1** of Technical Lead Codex's Work Order 06 (`[X-167]` / `Docs/BossCombatReview/Execution/ANTIGRAVITY_WORK_ORDER_06.md`).

It establishes the rigorous, source-grounded technical separation of configured C++ defaults, raw notify exports, and runtime probe samples across the native special attacks:
1. **Move A4 (Low Sweep):** Distinguishes configured tracker timing from sampled probe crossing, and source-verifies dynamic runtime montage generation (`PlaySlotAnimationAsDynamicMontage`).
2. **Move A5 (Javelin Throw):** Replaces artificial composed total duration with grounded C++ parameters (`RPGBossHealPunish.h`), records native actor spawning (`ARPGBossJavelin::StaticClass()`), and re-confirms visual hand-release capture is strictly parked.
3. **Move A6 (Leap & Shockwave):** Distinguishes the pack central damage hit from the native radial ground wave component (`RPGBossShockwave.cpp`).
4. **Helper Hardening Verification:** Documents the two semantic validator fixes in `audit_cue_source_inventory.py`.

---

## 2. Move A4 Low Sweep (`INV-ROUTE-A4`) Source Provenance

### 2.1 Dynamic Montage Generation vs Static Asset Existence
A primary source audit of [`Source/OneBossFight/Player/RPGAttackTracker.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L148-L170) resolves the nature of the A4 montage wrapper:
- **Source Lines 111–116:**
  > `"A pack montage is found by its own name; a dynamic montage (A4, A5) has a generated name, so it is found by the animation its first segment plays."`
- **Source Lines 152–169:**
  ```cpp
  UAnimSequenceBase* Clip = LoadObject<UAnimSequenceBase>(nullptr, *Timing.ClipPath);
  ...
  return Anim->PlaySlotAnimationAsDynamicMontage(Clip, SlotName, 0.1f, 0.2f, 1.f, 1, -1.f, 0.f) != nullptr;
  ```
- **Conclusion:** There is **no static `AM_Boss01_A4_LowSweep.uasset`** asset in the repository. The dynamic montage wrapper is generated transiently in memory at runtime by the engine. Requesting an export of a static `.uasset` montage wrapper is an error; notify analysis applies to the underlying raw clip [`Content/OneBossFight/Boss01/Animations/AN_Boss01_A4_LowSweep.uasset`](file:///c:/UnrealProject/OneBossFight/Content/OneBossFight/Boss01/Animations/AN_Boss01_A4_LowSweep.uasset).

### 2.2 Configured vs Sampled Timing Separation
| Parameter / Event | Source Anchor | Coordinate / Value | Clock Domain | Evidence Classification |
|---|---|---|---|---|
| Raw Clip Asset Length | Source comments in `RPGAttackTracker.cpp:78` (`1.767 s`); raw `.uasset` header readback unverified | $1.767\text{ s}$ | Montage Local | Source-Comment Citation (Raw Readback Unverified) |
| Configured Commit Time | `RPGAttackTracker.cpp:84` | $0.400\text{ s}$ | Montage Local | C++ Configured Default |
| Configured Active Damage Start | `RPGAttackTracker.cpp:85` | $0.600\text{ s}$ | Montage Local | C++ Configured Default |
| Configured Active Damage End | `RPGAttackTracker.cpp:86` | $0.900\text{ s}$ | Montage Local | C++ Configured Default |
| Configured Recovery End | `RPGAttackTracker.cpp:87` | $1.750\text{ s}$ | Montage Local | C++ Configured Default |
| Configured Tracking Turn Rate | `RPGAttackTracker.cpp:88` | $180.0\text{ deg/s}$ | Simulation / Yaw | C++ Configured Default |
| Sampled Floor Blade Crossing | `E-008:5` (Probe `p0_a4_geometry.py`) | $[0.609\text{ s}, 0.879\text{ s}]$ | Montage Local | Sampled Probe Telemetry |
| Sampled Peak Reach Coordinate | `E-008:5` (Probe `p0_a4_geometry.py`) | $0.855\text{ s}$ | Montage Local | Sampled Probe Telemetry |
| Geometric Query Reach Mismatch | `E-008:8` | $380\text{ cm}$ (query) vs $312\text{ cm}$ (mesh tip) = $68\text{ cm}$ | 3D Spatial (cm) | Physical Geometry Observation |

---

## 3. Move A5 Javelin Throw (`INV-ROUTE-A5`) Source Provenance

### 3.1 Contact Source & Native Actor Spawning
In [`Source/OneBossFight/Player/RPGBossHealPunish.cpp:179`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossHealPunish.cpp#L179), the spawned actor is explicitly:
```cpp
if (ARPGBossJavelin* Javelin = GetWorld()->SpawnActor<ARPGBossJavelin>(
    ARPGBossJavelin::StaticClass(), From, Direction.Rotation(), Parameters))
```
- **Actor Class:** Native C++ class `ARPGBossJavelin::StaticClass()`.
- **Finding:** The earlier reference to `BP_Boss01_Javelin_C` was an inferred blueprint convention, not the actual C++ instantiation. The contact source is the native `ARPGBossJavelin` spherical query sweep ($R = 25.0\text{ cm}$).

### 3.2 Dynamic Montage Wrapper
Like Move A4, Move A5 is played via [`URPGAttackTracker::PlayClip`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L169), dynamically wrapping [`AN_Boss01_A5_JavelinThrow`](file:///c:/UnrealProject/OneBossFight/Content/OneBossFight/Boss01/Animations/AN_Boss01_A5_JavelinThrow.uasset) in memory. No static `AM_Boss01_A5_JavelinThrow.uasset` file exists.

### 3.3 Configured vs Sampled Timing & Flight Parameter Separation
Artificially composing a total duration (e.g. $1.600\text{ s}$) conflated boss character animation with projectile flight. These are strictly separate systems:

| System / Field | Source Anchor | Coordinate / Value | Clock Domain | Evidence Classification |
|---|---|---|---|---|
| Raw Clip Asset Duration | Source comments in `RPGAttackTracker.cpp:91` (`1.0 s`); raw `.uasset` header readback unverified | $1.000\text{ s}$ | Montage Local | Source-Comment Citation (Raw Readback Unverified) |
| Authored Sidecar Marker | Freeze 16 / Sidecar Frame 12 | $0.400\text{ s}$ | Montage Local | Historical Authoring Marker |
| Configured Commit Time | `RPGAttackTracker.cpp:97` | $0.450\text{ s}$ | Montage Local | C++ Configured Default |
| Configured Active Release Window | `RPGAttackTracker.cpp:98-99` | $[0.450\text{ s}, 0.500\text{ s}]$ | Montage Local | C++ Configured Default |
| Configured Recovery End | `RPGAttackTracker.cpp:100` | $0.950\text{ s}$ | Montage Local | C++ Configured Default |
| Configured Track Turn Rate | `RPGAttackTracker.cpp:101` | $240.0\text{ deg/s}$ | Simulation / Yaw | C++ Configured Default |
| Sampled Runtime Spawn | `E-007:5` (PIE Telemetry) | $0.470\text{ s}$ | Simulation Time | Sampled Runtime Telemetry |
| Punish Trigger Selection Max Range | `RPGBossHealPunish.h:40` (`MaxRange`) | $1000.0\text{ cm}$ | AI Targeting Distance | C++ Configured Tunable |
| Projectile Flight Time | `RPGBossHealPunish.h:54` (`FlightTime`) | $1.200\text{ s}$ | Projectile Simulation | C++ Configured Tunable |
| Projectile Min Speed Clamp | `RPGBossHealPunish.h:57` (`MinSpeed`) | $450.0\text{ cm/s}$ | Projectile Simulation | C++ Configured Tunable |
| Projectile Max Speed Clamp | `RPGBossHealPunish.h:60` (`MaxSpeed`) | $2500.0\text{ cm/s}$ | Projectile Simulation | C++ Configured Tunable |
| Javelin Collision Radius | `RPGBossHealPunish.h:65` (`JavelinRadius`) | $25.0\text{ cm}$ | Projectile Collision | C++ Configured Tunable |
| Javelin Max Flight Range | `RPGBossHealPunish.h:68` (`JavelinMaxRange`) | $3000.0\text{ cm}$ | Projectile Simulation | C++ Configured Tunable |
| Heal Punish Cooldown | `RPGBossHealPunish.h:44` (`Cooldown`) | $4.000\text{ s}$ | Subsystem Cooldown | C++ Configured Tunable |
| Visual Hand Departure Frame | Viewport High-Speed Capture | **PARKED AS UNVERIFIED** | Visual Telemetry | Explicitly Parked per Owner Directive |

---

## 4. Move A6 Leap Attack & Ground Shockwave (`INV-ROUTE-A6-PACK`)

Move A6 combines a pack-derived central leap strike with a native radial ground wave component:

### 4.1 Two Independent Damage Sources
1. **Central Leap Strike (Pack-Derived):**
   - Montage: `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_LeapAttack_Montage`
   - Active Window: $[0.754\text{ s}, 1.175\text{ s}]$ (opened by `ANS_CollisionTrace_C` at landing impact).
   - Priority: Central hit takes priority over shockwave (`RPGBossShockwave.cpp:106-111` / `CentralPriorityCount`).
2. **Radial Ground Wave (Native Component):**
   - Managed by: [`URPGBossShockwave`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossShockwave.h).
   - Lifecycle: `RPGBossShockwave.cpp:129-171` (`TickComponent()`) and `cpp:64-127` (`Resolve()`).
   - Trigger: In `RPGBossShockwave.cpp:153-157`, `TickComponent()` polls `Tracker->GetCurrentMove() == MoveId && Tracker->IsActiveWindow() && Tracker->GetAttackInstance() != LastInstance`. Native launch occurs on the first qualifying tick poll after the native tracker's active window opens (`ActiveStartTime = 0.75f`, `ActiveEndTime = 1.17f` in `RPGAttackTracker.cpp:72-73`). The exact runtime timestamp of the first qualifying poll is unmeasured. Coordinates $[0.754\text{ s}, 1.175\text{ s}]$ belong strictly to the raw pack notify window (`ANS_CollisionTrace_C` in `GS_LeapAttack_Montage`), not a direct native code event.

### 4.2 Authoritative Shockwave Parameters (`RPGBossShockwave.h:39-57`)
| Parameter | Source Anchor | Configured Value | Unit | Gameplay Meaning |
|---|---|---|---|---|
| Start Radius | `RPGBossShockwave.h:42` | $200.0$ | $\text{cm}$ | Initial wave ring radius at boss's feet |
| Max Radius | `RPGBossShockwave.h:45` | $1100.0$ | $\text{cm}$ | Outward propagation threshold for wave stop |
| Expansion Speed | `RPGBossShockwave.h:49` | $1000.0$ | $\text{cm/s}$ | Outward radial velocity along arena floor |
| Wavefront Thickness | `RPGBossShockwave.h:53` | $180.0$ | $\text{cm}$ | Width of damaging radial band |
| Jump Clearance | `RPGBossShockwave.h:57` | $50.0$ | $\text{cm}$ | Minimum feet height above floor to clear wave |
| Base Damage | `RPGBossShockwave.h:39` | $48.0$ | $\text{HP}$ | Health deducted on hit ($120 \times 0.4$) |
| Nominal Travel Time | Derived: $\frac{MaxRadius - StartRadius}{Speed}$ | $0.900$ | $\text{s}$ | Nominal time to reach MaxRadius boundary ($900\text{ cm} / 1000\text{ cm/s}$) |
| Nominal Passage Duration | Derived: $\frac{Thickness}{Speed}$ | $0.180$ | $\text{s}$ | Nominal geometric passage time of wave band over a stationary ground point ($180\text{ ms}$); not an empirical contact/reaction duration |

> [!NOTE]
> **Nominal vs Terminal Tick Semantics:** In `RPGBossShockwave.cpp:167-170`, `Stop(TEXT("max radius"))` evaluates *after* the tick update and `Resolve()` when `Radius > MaxRadius`. Due to discrete frame deltas $\Delta t$, the wave overshoots $1100\text{ cm}$ on the final tick before stopping. Furthermore, the outer damaging band edge is `Radius + Thickness * 0.5f` ($Radius + 90\text{ cm}$), meaning the hazard reaches $\approx 1190\text{ cm}$ or further on the final tick. Thus, $0.900\text{ s}$ is a nominal geometric duration, not an exact simulation lifetime clamp.

---

## 5. Semantic Validator Helper Hardening Verification

In response to Codex review `AG05_REV3_REVIEW.md`, [`audit_cue_source_inventory.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/audit_cue_source_inventory.py) was updated with two mandatory fixes:

1. **Mandatory Companion Report Presence:**
   - Previous logic silently skipped Markdown validation if `os.path.exists(md_path)` returned false.
   - Updated logic in `validate_inventory()`:
     ```python
     if check_markdown:
         if not os.path.exists(md_path):
             errors.append(f"Companion Markdown report missing at: {md_path}")
     ```
   - An unreadable or missing Markdown report now immediately produces a validator error and non-zero exit code.
2. **Error-Specific Negative Test Assertion:**
   - Previous logic in `run_negative_test_suite()` printed a warning on expected substring mismatch but incremented the pass counter.
   - Updated logic strictly enforces substring matching:
     ```python
     if matched:
         passed_probes += 1
     else:
         print(f"  [-] FAIL: Probe '{label}' rejected, but expected substring '{expected_err_sub}' was NOT found in errors: {messages}")
         return False
     ```
   - Added an automated **verifier meta-test** within the suite proving that an intentionally mismatched expected substring fails the test harness.
   - Added negative probe case specifically testing for a missing companion Markdown report.
   - **Verification:** All 13 negative probes + verifier meta-test pass with zero warnings.
