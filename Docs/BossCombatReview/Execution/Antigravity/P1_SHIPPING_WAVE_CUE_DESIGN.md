# P1 Shipping Shockwave Cue Gap & Production Architecture Design

**Document ID:** `P1_SHIPPING_WAVE_CUE_DESIGN`  
**Date:** 2026-10-26 (Revised per Codex Lead Reviews `AG06_A117_REVIEW.md` and `AG06_A118_REVIEW.md`)  
**Author:** Antigravity (Visual & Technical Animation Investigator)  
**Work Order:** `Docs/BossCombatReview/Execution/ANTIGRAVITY_WORK_ORDER_06.md` (Task **AG06-2**)  
**Governing Documents & Primary Source Anchors:**  
- Requirements Baseline: [`06_REFERENCE_REQUIREMENTS.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Reference/06_REFERENCE_REQUIREMENTS.md) (`BOSS-ANM-002`, `BOSS-PAC-001`, `BOSS-PAC-003`, `BOSS-QA-006`, `BOSS-QA-007`)
- Codex Lead Reviews: [`AG06_A117_REVIEW.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/AG06_A117_REVIEW.md) & [`AG06_A118_REVIEW.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/AG06_A118_REVIEW.md)
- Primary Shockwave Header: [`Source/OneBossFight/Player/RPGBossShockwave.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossShockwave.h) (SHA256: `4d1973ffe41672e8db4d52029d584f98c9b6df2f8a61cff63b2e3eee39c4d7cd`)
- Primary Shockwave Source: [`Source/OneBossFight/Player/RPGBossShockwave.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossShockwave.cpp) (SHA256: `9632381f60e92d3f2d7cc7362883cbc03c3b258191abbbb4755a4bc9591cf3a4`)
- Attack Tracker Source: [`Source/OneBossFight/Player/RPGAttackTracker.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp) (SHA256: `f2d2615f1b938aa8bf1f4ad9d7574b1876446823d83b87cd69521ca9d1153f0c`)
- Leap Montage Notifies Export: [`montage_notifies_2026-10-25.txt`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/Evidence/exports/montage_notifies_2026-10-25.txt) (SHA256: `950c611ee5eae7bcdd7abca1ea56c051c3b42d988b427cf64452829142ab0b31`)
- Installed Engine Headers:
  - `Engine/Plugins/FX/Niagara/Source/Niagara/Public/NiagaraComponent.h`
  - `Engine/Plugins/FX/Niagara/Source/Niagara/Public/NiagaraFunctionLibrary.h`
  - `Engine/Source/Runtime/Engine/Classes/Components/DecalComponent.h`
  - `Engine/Source/Runtime/Core/Public/Misc/App.h`

---

## 1. Executive Summary & Production Gap Identification

### 1.1 The Shipping Cue Absence Gap
Move A6 (Phase 2 Leap Attack) features a dual-damage architecture:
1. **Central Landing Strike (Pack Melee Trace):** Handled by pack collision notifies in `GS_LeapAttack_Montage` ($[0.754\text{ s}, 1.175\text{ s}]$).
2. **Radial Ground Shockwave (Native Component):** Handled by native C++ component [`URPGBossShockwave`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossShockwave.h), which expands a damaging ground band from $StartRadius = 200.0\text{ cm}$ outward at $Speed = 1000.0\text{ cm/s}$ until $Radius > MaxRadius = 1100.0\text{ cm}$, deducting $48.0\text{ HP}$ from grounded players.

In [`Source/OneBossFight/Player/RPGBossShockwave.cpp:164-166`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossShockwave.cpp#L164-L166), visual representation is currently implemented as:
```cpp
#if !UE_BUILD_SHIPPING
    DrawDebugCircle(GetWorld(), FVector(Origin.X, Origin.Y, GroundZ + 8.f), Radius, 64,
                    FColor(255, 140, 40), false, -1.f, 0, 8.f,
                    FVector(1, 0, 0), FVector(0, 1, 0), false);
#endif
```

### 1.2 Bounded Evidence & Inspected Paths
Evidence for the Shipping cue absence gap is strictly bounded to the following inspected paths:
- **`RPGBossShockwave.h:19` Comment:** `"Placeholder visual: a debug ring (not in shipping); the real wave effect is an art request."`
- **`RPGBossShockwave.cpp:164-166` Preprocessor Guard:** The `#if !UE_BUILD_SHIPPING` preprocessor block definitively proves that `DrawDebugCircle` is excluded from packaged Shipping builds at compile time.
- **`montage_notifies_2026-10-25.txt:35-39` (`GS_LeapAttack_Montage`):** Raw notify dump inspection confirms that this specific montage track contains only two `ANS_SetDesiredRotation_C` notifies and one `ANS_CollisionTrace_C` notify. There are **zero audio notifies and zero Niagara/cascade particle notifies** in this montage block.
- **Content Inspection:** No dedicated shockwave visual or audio assets exist under `Content/OneBossFight/` (e.g. no `NS_Boss01_Shockwave` or `M_Boss01_Shockwave`). Candidate demonstration assets exist in pack folders (`Content/AdvancedARPGCombat/...`), but are unreferenced by `URPGBossShockwave`.
- **Classification:** Production-cue absence is verified *for these named inspected paths*. Whether alternative Blueprint, ability, or sound paths trigger independent cues in shipping remains unverified without exhaustive project-wide graph tracing or packaged visual capture.

---

## 2. Authoritative Shockwave Geometry, Order & Terminal Tick Semantics

### 2.1 Authoritative Contact Band Geometry
From [`Source/OneBossFight/Player/RPGBossShockwave.cpp:71-75`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossShockwave.cpp#L71-L75):
```cpp
const float Inner = Radius - Thickness * 0.5f;
const float Outer = Radius + Thickness * 0.5f;
```
- **Centerline:** `Radius` (starts at $200.0\text{ cm}$, advances by $Speed \times \Delta t$).
- **Thickness:** $Thickness = 180.0\text{ cm}$ (`RPGBossShockwave.h:53`).
- **Contact Band:** $[Radius - 90.0\text{ cm},\ Radius + 90.0\text{ cm}]$. The debug circle drawn at line 165 represents the **centerline**, not the inner or outer collision edges.
- **Origin:** Boss actor ground origin at launch ($Origin = \text{Boss Actor Location}$ with $GroundZ = Origin.Z - CapsuleHalfHeight$).
- **Jump Clearance:** $FeetZ - GroundZ \ge 50.0\text{ cm}$ (`RPGBossShockwave.h:57`).

### 2.2 Authoritative Tick Execution Order
In [`URPGBossShockwave::TickComponent`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossShockwave.cpp#L129-L171), the per-frame sequence is strictly:
1. **Advance Radius:** `Radius += Speed * DeltaTime;` ($Speed = 1000.0\text{ cm/s}$).
2. **Resolve Contact:** `Resolve();` checks player distance against $[Inner, Outer]$ and applies 48 HP damage via `RPGDamageResolver`. If central leap damage already landed, central hit takes priority (`RPGBossShockwave.cpp:106-111`).
3. **Debug Draw:** `DrawDebugCircle(...)` (executed only if `!UE_BUILD_SHIPPING`).
4. **Terminal Stop Evaluation:** `if (Radius > MaxRadius) Stop(TEXT("max radius"));` ($MaxRadius = 1100.0\text{ cm}$).

### 2.3 Nominal vs Terminal Tick Semantics
- **Nominal Travel Time:** $\frac{MaxRadius - StartRadius}{Speed} = \frac{1100 - 200}{1000} = 0.900\text{ s}$.
- **Discrete Overshoot:** Because `Stop` evaluates *after* the radius advance and hit resolution when `Radius > MaxRadius`, discrete frame deltas $\Delta t$ (e.g. at 60 FPS, $\Delta t \approx 16.67\text{ ms}$, advancing $\approx 16.67\text{ cm}$) cause `Radius` to overshoot $1100.0\text{ cm}$ on the final active tick before stopping.
- **Outer Hazard Reach:** Because the damaging band extends to $Outer = Radius + 90.0\text{ cm}$, the outer hazard edge reaches $\approx 1190.0\text{ cm}$ (or further depending on final tick $\Delta t$) on the terminal tick.
- **Observer Constraint:** A visual cue component must act strictly as an **observer of authoritative C++ state**. It must **not** independently integrate its own simulation clock, nor clamp or terminate earlier than the C++ component.

---

## 3. Comparison of Production-Cue Architecture Alternatives

```mermaid
flowchart TD
    subgraph Gameplay ["URPGBossShockwave (Authoritative Gameplay)"]
        Tick["TickComponent(DeltaTime)"]
        State["Origin, GroundZ, Radius, Speed, Thickness, AttackInstanceId, Generation"]
        Resolve["Resolve() -> 48 Damage (Unchanged)"]
    end

    subgraph AltA ["Alternative A: C++ Procedural Material Ring Component (Author Recommended)"]
        CompA["URPGShockwaveRingComponent<br>(UDecalComponent or Mesh with Dynamic Material)"]
        Tick -->|Tick update| CompA
        State -->|Centerline, Band [R-90, R+90], Origin| CompA
    end

    subgraph AltB ["Alternative B: Parameter-Driven Niagara System"]
        CompB["UNiagaraComponent<br>(SpawnSystemAtLocation / SetVariableFloat)"]
        Tick -->|SetVariableFloat per tick| CompB
        State -->|Radius, Thickness, Origin| CompB
    end

    subgraph AltC ["Alternative C: Decoupled Authored Timeline Cue"]
        CompC["Triggered Particle/Sequence Cue<br>(Fixed Expansion Curve)"]
        Tick -.->|Launch Event Only| CompC
    end
```

### 3.1 Architectural Trade-Off Analysis

| Architectural Vector | Alternative A: Procedural Material Ring Component (Author Proposed) | Alternative B: Parameter-Driven Niagara System | Alternative C: Decoupled Authored Timeline Cue |
|---|---|---|---|
| **Author Recommendation** | **Recommended by Author (Proposed, Unapproved)** | Not Recommended as Primary (Viable Alternative) | Rejected (High Desync Risk) |
| **Authoritative Source** | Driven per-tick directly from `URPGBossShockwave` state | Driven per-tick via Niagara user parameters | Independent asset playback timeline |
| **Contact Band Alignment** | Intended state-transfer property: shader directly consumes C++ `Radius`; not an empirical render proof | Medium-High: Requires continuous parameter binding; subject to Niagara particle tick order | Poor: Independent asset duration/speed can desync if C++ parameters change |
| **Asset Dependency** | Requires authored material shader asset (or decal) and valid dynamic instance binding | Authored `UNiagaraSystem` asset required | Authored Niagara/Cascade particle asset required |
| **Simulation Drift** | Intended design property: zero simulation drift against game thread; render agreement unmeasured | Potential 1-frame tick order latency between Actor and Niagara component | Independent playback curve diverges from game thread tick rate |
| **Scalability & Culling** | Standard decal / mesh distance culling | Niagara scalability culling may kill particles on low settings | Standard particle culling |
| **Speculative CPU Cost** | Estimated $\approx 3 - 6\ \mu\text{s}$ per tick (updating MID scalar parameters; unmeasured) | Estimated $\approx 8 - 15\ \mu\text{s}$ per tick (Niagara parameter interface; unmeasured) | Estimated $\approx 2\ \mu\text{s}$ (launch trigger only; unmeasured) |
| **Speculative GPU Cost** | Estimated $\approx 0.02 - 0.04\text{ ms}$ (quad decal / simple ring mesh; unmeasured) | Estimated $\approx 0.05 - 0.12\text{ ms}$ (GPU particle emitter; unmeasured) | Estimated $\approx 0.05 - 0.10\text{ ms}$ (unmeasured) |
| **Headless Behavior** | Explicitly bypassed when `!FApp::CanEverRender() \|\| IsRunningCommandlet()` | Explicitly bypassed when `!FApp::CanEverRender() \|\| IsRunningCommandlet()` | Explicitly bypassed when `!FApp::CanEverRender() \|\| IsRunningCommandlet()` |
| **Failure Mode** | Requires fallback asset/geometry contract; if material/parameters fail, outcome is **UNKNOWN** (no guaranteed gray ring) | System missing fails to spawn; requires explicit C++ fallback | Asset missing fails silently; hazard boundary unrendered |

> [!IMPORTANT]
> **Author Recommendation Status:** Alternative A (Procedural Material Ring Component) is proposed by Antigravity as the cleanest and lowest-drift architecture because it avoids particle simulation drift against the authoritative contact band, has direct C++ tick ownership, and does not require authoring complex binary Niagara emitters. **This recommendation is an author proposal and is NOT an approved project decision.**

---

## 4. Detailed Specification: Alternative A — Procedural Material Ring Component

### 4.1 Interface Contract & Disambiguation Identity
To prevent cross-instance contamination, stale visual persistence, or multi-world overlap, the visual component consumes an explicit data payload on each event:

```cpp
// Visual cue configuration payload
struct FRPGShockwaveVisualConfig
{
    FVector Origin;             // Ground contact point (Origin.X, Origin.Y, GroundZ)
    float StartRadius;          // 200.0 cm
    float MaxRadius;            // 1100.0 cm
    float Speed;                // 1000.0 cm/s
    float Thickness;            // 180.0 cm
    int32 AttackInstanceId;     // Disambiguates successive leap attacks
    int32 EncounterGeneration;  // Disambiguates encounter resets / duel restarts
};
```

### 4.2 Lifecycle & Teardown Protocol
The visual component's lifecycle is strictly bound to `URPGBossShockwave`:
1. **Launch:** `Launch()` instantiates or activates the visual component at `Origin` ($GroundZ$), initializes dynamic material parameters (`InnerRadius`, `OuterRadius`, `Thickness`), and records `AttackInstanceId` and `EncounterGeneration`.
2. **Tick Update:** In `TickComponent()`, after `Radius` advances, the component updates shader parameters:
   ```cpp
   if (DynamicMaterialInstance)
   {
       DynamicMaterialInstance->SetScalarParameterValue(TEXT("CenterlineRadius"), Radius);
       DynamicMaterialInstance->SetScalarParameterValue(TEXT("InnerRadius"), Radius - Thickness * 0.5f);
       DynamicMaterialInstance->SetScalarParameterValue(TEXT("OuterRadius"), Radius + Thickness * 0.5f);
   }
   ```
3. **Terminal Stop (`Stop(Reason)`):**
   - Max Radius reached: Triggers proposed optional material opacity fadeout ($\le 0.1\text{ s}$).
     > [!NOTE]
     > **Proposed Presentation Timing:** The $\le 0.1\text{ s}$ fadeout is a proposed presentation smoothing duration only; it is NOT an approved damage cutoff or early hazard termination.
   - Boss Death (`bDead`): Immediately deactivates and hides component (`SetVisibility(false)`).
   - Encounter Reset / Generation Change: Immediately destroys or unregisters component to prevent stale visual bleed into new fight attempts.
   - Stance Break / Phase Cancel: Immediately halts expansion and fades material.
4. **World Teardown (`EndPlay`):** Component is unregistered cleanly in `EndPlay`.
5. **Multi-World / Multi-Local Viewport:** Instantiated strictly within the owning actor's `UWorld` (`GetWorld()`). Note: Component ownership within `UWorld` is an intended architectural isolation boundary; it is **not** an empirically proven leak-free or multi-viewport correctness guarantee.

### 4.3 Headless, Dedicated Server & Automation Guards
Rendering must be bypassed entirely under headless, commandlet, or dedicated server contexts:
```cpp
// Proposed helper pseudocode:
bool ShouldCreateVisualCue(const UWorld* World)
{
    if (!World || !World->IsGameWorld()) return false;
    if (World->GetNetMode() == NM_DedicatedServer) return false;
    // FApp::CanEverRender() (Core/Public/Misc/App.h:397-404) explicitly covers UE_SERVER, null RHI,
    // commandlet rendering allowance, and dedicated server checks. The additional !IsRunningCommandlet()
    // check is an intentional, stricter project policy to bypass visual initialization during automated
    // commandlet execution. Note: "CanEverRender" does not guarantee a focused, visible, or unoccluded viewport.
    if (!FApp::CanEverRender() || IsRunningCommandlet()) return false;
    return true;
}
```

---

## 5. Specification of Alternative B (Niagara) with Verified UE 5.5 APIs

If Lead/Owner selects Alternative B (Niagara System), the implementation must adhere to verified Unreal Engine 5.5 APIs:

### 5.1 Source-Verified UE 5.5 Niagara Methods
Inspection of installed engine header `NiagaraComponent.h` (`C:\Program Files\Epic Games\UE_5.5\Engine\Plugins\FX\Niagara\Source\Niagara\Public\NiagaraComponent.h`) confirms:
- **Parameter Binding:**
  - `Line 517: NIAGARA_API void SetVariableFloat(FName InVariableName, float InValue);`
  - `Line 526: NIAGARA_API void SetVariableInt(FName InVariableName, int32 InValue);`
- **Activation & Deactivation:**
  - `Line 223: NIAGARA_API virtual void Deactivate() override;` (Stops spawning new particles; active particles finish lifetime).
  - `Line 224: NIAGARA_API virtual void DeactivateImmediate() override;` (Kills all active particles immediately).
- **Spawn Library (`Engine/Plugins/FX/Niagara/Source/Niagara/Public/NiagaraFunctionLibrary.h`):**
  - `Line 42: static NIAGARA_API UNiagaraComponent* SpawnSystemAtLocation(const UObject* WorldContextObject, class UNiagaraSystem* SystemTemplate, FVector Location, FRotator Rotation = FRotator::ZeroRotator, FVector Scale = FVector(1.f), bool bAutoDestroy = true, bool bAutoActivate = true, ENCPoolMethod PoolingMethod = ENCPoolMethod::None, bool bPreCullCheck = true);`
- **Decal Component (`Engine/Source/Runtime/Engine/Classes/Components/DecalComponent.h`):**
  - `Line 125: ENGINE_API virtual class UMaterialInstanceDynamic* CreateDynamicMaterialInstance();`

> [!CAUTION]
> The previously proposed enum `ENiagaraComponentDeactivationType::KillWithoutClearing` does **NOT** exist in UE 5.5 `NiagaraComponent.h`. The correct engine method for immediate abort is `NiagaraComp->DeactivateImmediate()`.

---

## 6. Proposed Failure & Optional-Asset Policy (Harm Prevention)

> [!NOTE]
> The policies below are **unapproved design proposals** submitted for Technical Lead and Owner review. No damage veto or gameplay mutation has been implemented.

If a visual asset fails to load, fails to cook, or is culled by engine scalability:
1. **Proposal 1: Procedural Fallback Asset Contract (Proposed by Author):**
   Requires an explicit fallback asset/geometry contract and dependency validation. If the primary asset fails to load, the system attempts to instantiate a minimal fallback dynamic decal or mesh. If fallback asset/parameters also fail, the visual outcome is **UNKNOWN**; there is no guaranteed default render behavior.
2. **Proposal 2: Audio Redundancy (`BOSS-QA-007`):**
   Spawn a synchronized ground rumble / crack sound at `Origin`. Note: Audio alone cannot guarantee player visibility of exact boundary edges, and provides zero mitigation under `-nosound` or muted gameplay.
3. **Proposal 3: Damage Suppression Veto (Strict Safety Proposal):**
   If all visual cues fail completely, gameplay damage could theoretically be suppressed to prevent invisible player damage. If fallback fails, retain Lead/Owner policy alternatives without activating damage veto. *Status: Open design question for Lead/Owner; Antigravity will not implement gameplay damage veto without explicit Lead authorization.*

---

## 7. Bounded Offline Source & Dependency Manifest

This manifest documents the exact inspected files, candidate assets, source-confirmed APIs, and missing runtime evidence across the three wave-render alternatives:

### 7.1 Inspected Files, Exports & Primary Hashes
| File / Artifact | Location / Relative Path | SHA256 Hash / Reference | Inspected Evidence / Relevance |
|---|---|---|---|
| `RPGBossShockwave.h` | `Source/OneBossFight/Player/RPGBossShockwave.h` | `4d1973ffe41672e8db4d52029d584f98c9b6df2f8a61cff63b2e3eee39c4d7cd` | Authoritative parameters: `StartRadius = 200`, `MaxRadius = 1100`, `Speed = 1000`, `Thickness = 180`, `JumpClearance = 50`, `Damage = 48` |
| `RPGBossShockwave.cpp` | `Source/OneBossFight/Player/RPGBossShockwave.cpp` | `9632381f60e92d3f2d7cc7362883cbc03c3b258191abbbb4755a4bc9591cf3a4` | `TickComponent:129-171`, `Resolve:64-127`, `DrawDebugCircle:164-166` under `#if !UE_BUILD_SHIPPING` |
| `RPGAttackTracker.cpp` | `Source/OneBossFight/Player/RPGAttackTracker.cpp` | `f2d2615f1b938aa8bf1f4ad9d7574b1876446823d83b87cd69521ca9d1153f0c` | A6 tracker configuration lines 70-76 (`ActiveStartTime = 0.75f`, `ActiveEndTime = 1.17f`) |
| `montage_notifies_2026-10-25.txt` | `Docs/BossCombatReview/Execution/Claude/Evidence/exports/` | `950c611ee5eae7bcdd7abca1ea56c051c3b42d988b427cf64452829142ab0b31` | Lines 35–39: `GS_LeapAttack_Montage` has 0 sound notifies and 0 particle notifies |
| `NiagaraComponent.h` | `Engine/Plugins/FX/Niagara/Source/Niagara/Public/NiagaraComponent.h` | Lines 224, 517, 526 | Verified UE 5.5 APIs: `DeactivateImmediate`, `SetVariableFloat`, `SetVariableInt` |
| `NiagaraFunctionLibrary.h` | `Engine/Plugins/FX/Niagara/Source/Niagara/Public/NiagaraFunctionLibrary.h` | Line 42 | Verified UE 5.5 API: `SpawnSystemAtLocation` |
| `DecalComponent.h` | `Engine/Source/Runtime/Engine/Classes/Components/DecalComponent.h` | Line 125 | Verified UE 5.5 API: `CreateDynamicMaterialInstance` |
| `App.h` | `Engine/Source/Runtime/Core/Public/Misc/App.h` | Lines 397–404 | Verified UE 5.5 API: `FApp::CanEverRender()` |

### 7.2 Candidate vs Unknown Production Assets
| Candidate Asset Path (Relative to `Content/AdvancedARPGCombat/`) | SHA256 Hash | Status / Knowns | Unexported Properties (UNKNOWN) |
|---|---|---|---|
| `MagicCombatSystem/DemoAssets/AuroraVFX/Meshes/SM_Shockwave_Disc.uasset` | `7e1d6df35f837c88d893eb6887e2d6c0e0e69f7144943ba8af407712c16a8621` | Candidate static mesh disc on disk | Material domain, vertex layout, UV mapping, cook closure: **UNKNOWN** (requires operator readback) |
| `MagicCombatSystem/DemoAssets/AuroraVFX/Materials/Shockwaves/M_Shockwave_Soft.uasset` | `edfcceb024b0a0aec82622a20a9326693008ac48fd1c75857351edffc7078fc5` | Candidate material on disk | Material Domain (Surface vs Decal), parameter names, blend mode: **UNKNOWN** (requires operator readback) |
| `AdvancedCombatFramework/AbilitySystem/DataAssets/BP_Niagara_ImpactEffect.uasset` | `82947d7d454f11668042d62958c4749a5dd143346add17254f025b89e1c703ad` | Candidate Niagara container on disk | Internal system structure, parameter bindings, cook dependencies: **UNKNOWN** (requires operator readback) |

- **Dedicated Assets (Non-Existent on Disk):**
  - No dedicated `Content/OneBossFight/Boss01/FX/NS_Boss01_Shockwave.uasset` exists on disk.
  - No dedicated `Content/OneBossFight/Boss01/Materials/M_Boss01_ShockwaveDecal.uasset` exists on disk.
  - Valid ring shader behavior cannot be inferred from filenames alone; production asset selection requires future operator readback.

### 7.3 Source-Confirmed C++ APIs vs Pseudocode
- **Source-Confirmed C++ APIs:**
  - `UDecalComponent::CreateDynamicMaterialInstance()` (`DecalComponent.h:125`)
  - `UMaterialInstanceDynamic::SetScalarParameterValue(FName, float)`
  - `UNiagaraFunctionLibrary::SpawnSystemAtLocation(...)` (`NiagaraFunctionLibrary.h:42`)
  - `UNiagaraComponent::SetVariableFloat(FName, float)` (`NiagaraComponent.h:517`)
  - `UNiagaraComponent::SetVariableInt(FName, int32)` (`NiagaraComponent.h:526`)
  - `UNiagaraComponent::DeactivateImmediate()` (`NiagaraComponent.h:224`)
  - `FApp::CanEverRender()` (`App.h:397-404`), `IsRunningCommandlet()`, `World->GetNetMode()`
- **Explicit Pseudocode:**
  - Shader procedural distance-field ring mask math in Section 4.2 is pseudocode representing material graph logic.
  - `ShouldCreateVisualCue(World)` in Section 4.3 is a design sketch / pseudocode helper.

### 7.4 Speculative Planning Estimates & Assumptions
> [!NOTE]
> All performance figures below are **speculative planning estimates** with explicit assumptions and unknowns, NOT measured UE5.5 hardware facts or approved budgets:
> - **Assumptions:** Target hardware RTX 2060 Super, 1080p, 60 FPS ($16.67\text{ ms}$ frame budget), standard deferred renderer, forward decals enabled.
> - **Estimated CPU Overhead:** $\approx 3 - 6\ \mu\text{s}$ per tick for Alternative A (parameter writes to MID; unmeasured); $\approx 8 - 15\ \mu\text{s}$ for Alternative B (Niagara parameter updates; unmeasured).
> - **Estimated GPU Overhead:** $\approx 0.02 - 0.04\text{ ms}$ for Alternative A (single unlit decal/mesh quad; unmeasured); $\approx 0.05 - 0.12\text{ ms}$ for Alternative B (GPU sprite emitter; unmeasured).
> - **Unknowns:** Actual render thread time under packaged shipping conditions, draw call count impact with multi-pass post-process, and GPU particle culling efficiency under heavy scene load.

### 7.5 Missing Runtime Evidence
1. **No Packaged Shipping Capture:** No video or image capture of packaged Shipping execution exists to verify actual runtime visual appearance.
2. **Visual-to-Collision Boundary Agreement:** Collision-to-visual edge alignment has not been measured empirically in engine. When implemented, measured edge disagreement must be recorded and submitted for Lead/Owner review (no arbitrary $\pm 20\text{ cm}$ pass gate is approved).
3. **Scalability Culling Behavior:** Visual behavior under `sg.EffectsQuality = 0` (Low) is unverified.
