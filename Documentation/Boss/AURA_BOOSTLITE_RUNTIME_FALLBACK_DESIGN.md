# Boost Lite Runtime Override Fallback Design

**Document Version:** 1.0  
**Authority:** Claude Lead Directive `[C-1202]` (2026-11-09).  
**Owner:** Antigravity (`Art/Review/Audit`).  
**Status:** DESIGN ONLY (Plan-only / No Apply until Codex graph prototype outcome is known).  
**Reference:** `Documentation/Boss/AURA_PRODUCTION_AUTHORING_PLAN.md`, `Documentation/Boss/AURA_BOOST_PROVENANCE_AND_BOOSTLITE_SPEC.md`

---

## 1. Executive Summary

In `[C-1199]` and `[A-689]`, the round-trip proof verified that serialized uasset byte-patching of rapid iteration tables drifts upon Editor re-save (re-synthesizing uncompiled graph defaults). While Codex prototypes a graph-level editor authoring path (`NS_Boss_PhaseTwoAura_BoostLite_Authored`), this document specifies the **Runtime Parameter Override Fallback**: driving Boost Lite aesthetics via first-class `UNiagaraComponent::SetVariable...` runtime API calls in `URPGTier2BossPresentation`.

This approach requires **zero uasset modifications**, is 100% data-driven per boss, and is completely immune to Unreal Editor cooking or serialization graph-recompile drift.

---

## 2. Technical Mechanism

### 2.1 Call Site & Integration Point
In [`Source/OneBossFight/Boss/RPGTier2BossPresentation.cpp`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Boss/RPGTier2BossPresentation.cpp#L45-L60):
When Phase 2 activates and `PhaseTwoAuraEffect.LoadSynchronous()` spawns the component:

```cpp
PhaseTwoAuraComponent = UNiagaraFunctionLibrary::SpawnSystemAttached(
    Aura, Mesh, SocketName, FVector::ZeroVector, FRotator::ZeroRotator,
    EAttachLocation::SnapToTarget, true);

if (PhaseTwoAuraComponent && bEnableAuraBoostLiteOverrides)
{
    // Apply Boost Lite Runtime Overrides (C-1203)
    // 1. System Fixed Bounds ([-175, 175] cm)
    PhaseTwoAuraComponent->SetSystemFixedBounds(FBox(FVector(-175.0f, -175.0f, -175.0f), FVector(175.0f, 175.0f, 175.0f)));

    // 2. User Parameter Overrides
    PhaseTwoAuraComponent->SetVariableFloat(TEXT("User.Scale_All"), 1.25f);
    PhaseTwoAuraComponent->SetVariableFloat(TEXT("User.Scale_Sparks1"), 1.25f);
    PhaseTwoAuraComponent->SetVariableFloat(TEXT("User.Scale_Sparks2"), 1.25f);

    PhaseTwoAuraComponent->SetVariableLinearColor(TEXT("User.Color_Smoke"), FLinearColor(20.0f, 2.8296f, 0.0f, 1.0f));
    PhaseTwoAuraComponent->SetVariableLinearColor(TEXT("User.Color_Sparks1"), FLinearColor(200.0f, 29.7466f, 0.0f, 1.0f));
    PhaseTwoAuraComponent->SetVariableLinearColor(TEXT("User.Color_Sparks2"), FLinearColor(20.0f, 1.8574f, 0.0f, 1.0f));
    PhaseTwoAuraComponent->SetVariableLinearColor(TEXT("User.Color_Spiral1"), FLinearColor(60.0f, 8.3257f, 0.0f, 1.0f));
}
```

### 2.2 Data Configuration
In accordance with `C-1177` per-boss data architecture, parameters are encapsulated within an optional struct `FRPGAuraPresentationConfig` inside boss definition data (`FRPGBossTier2Config`), defaulting to identity / baseline when unset.

---

## 3. Fidelity Impact Audit: What Boost Lite Loses vs Retains

| Aura Attribute | Full Boost Lite Spec (Graph) | Runtime Override Fallback | Delta / Visual Impact |
|---|---|---|---|
| **User.Scale_All** | `1.25` | `1.25` (Set via API) | **RETAINED 100%:** System spread scales up by 25%. |
| **User.Scale_Sparks1/2** | `1.25` | `1.25` (Set via API) | **RETAINED 100%:** Particle velocity/orbit scales up. |
| **Emissive Colors (2.0x)** | `(200.0, 29.75)` etc. | `(200.0, 29.75)` (Set via API) | **RETAINED 100%:** Full fiery intensity and glow achieved. |
| **Sparks1 SpawnRate** | `70.0 p/s` | `40.0 p/s` (Baseline graph) | **LOST (-42.8%):** Fewer individual ember sparks per second. |
| **Sparks2 SpawnRate** | `52.5 p/s` | `30.0 p/s` (Baseline graph) | **LOST (-42.8%):** Fewer fine floating ember flecks. |
| **Continuous Total Rate** | `152.5 p/s` | `100.0 p/s` (Baseline graph) | **LOST (-34.4% total density):** Overall particle volume is lower. |
| **Sparks1 SpriteSizeMax** | `(10.0, 100.0) cm` | `(8.0, 80.0) cm` (Baseline graph) | **LOST (-20% size):** Spark streaks are slightly shorter and thinner. |
| **Sparks1 SpriteSizeMin** | `(5.0, 50.0) cm` | `(4.0, 40.0) cm` (Baseline graph) | **LOST (-20% size):** Smallest sparks are slightly smaller. |
| **Fixed Culling Bounds** | `[-175.0, 175.0] cm` | `[-175.0, 175.0] cm` (Set via API, C-1203) | **RETAINED 100%:** `SetSystemFixedBounds` applies +/-175cm box at runtime. |

---

## 4. Assessment & Recommendation

1. **Aesthetic Assessment:**
   - The runtime override successfully delivers the **most visible visual cues**: the $2.0\times$ emissive brightness increase and the $1.25\times$ overall emitter scale expansion.
   - However, it produces a **sparser** aura ($100\text{ p/s}$ vs $152.5\text{ p/s}$) with $20\%$ shorter spark streaks compared to the Owner-reviewed Boost Lite audition clips.
2. **Recommendation:**
   - **Primary Target:** Support Codex's graph-level authoring prototype (`NS_Boss_PhaseTwoAura_BoostLite_Authored`), which preserves 100% of the Owner's chosen particle density and streak dimensions.
   - **Contingency:** If the Niagara Editor C++/Python graph API proves intractable without manual UI interaction, the runtime fallback provides a clean, zero-drift, ship-safe compromise.
