# Phase Two Aura Production Authoring Plan

**Document Version:** 1.0  
**Status:** PROPOSED (No apply until Owner selects aura option)  
**Reference:** C-1133 Lead Directive, C-1128, AU-C19  
**Auditor:** Antigravity (Art/Review/Audit)  

---

## 1. Context and Objective

Candidate assets `NS_Boss_PhaseTwoAura_Boost` and `NS_Boss_PhaseTwoAura_BoostLite` were generated for rapid, non-destructive A/B/C evaluation across:
- **Baseline (Approved):** $100\text{ p/s}$ continuous, bounds $\pm 100\text{ cm}$, `mean_gray = 47.2–54.4` (Boss readable, aura subtle).
- **Boost Candidate:** $205\text{ p/s}$ continuous, bounds $\pm 250\text{ cm}$, `mean_gray = 88.5` (Heavy aura, boss silhouette fully covered).
- **BoostLite Candidate:** $152.5\text{ p/s}$ continuous, bounds $\pm 175\text{ cm}$, `mean_gray = 65.0` (Stronger fiery visual, boss silhouette preserved).

Per `[C-1133]`, binary byte-patching of serialized uasset blocks is strictly permitted for candidate generation only. Once the project owner selects the definitive visual direction, the approved production asset (`NS_Boss_PhaseTwoAura.uasset`) must be authored cleanly through standard Unreal Engine pipelines before shipping.

---

## 2. Production Authoring Options

### Option A (Recommended): Parameterize via Niagara User Parameters
Instead of hardcoding compiled constant values in emitter rapid iteration tables, bind the scalable properties to first-class `User.` parameters on `NS_Boss_PhaseTwoAura`:
1. **User Parameter Schema:**
   - `User.Sparks1_SpawnRate` (Float) — Default: 70.0 (BoostLite) or 40.0 (Baseline)
   - `User.Sparks2_SpawnRate` (Float) — Default: 52.5 (BoostLite) or 30.0 (Baseline)
   - `User.Sparks1_SizeMin` (Vector2D) — Default: (5.0, 50.0)
   - `User.Sparks1_SizeMax` (Vector2D) — Default: (10.0, 100.0)
   - `User.Scale_All` (Float) — Default: 1.25
   - `User.Color_Smoke` / `Color_Sparks1` / `Color_Sparks2` / `Color_Spiral1` (LinearColor) — Emissive values $2.0\times$
2. **Advantages:**
   - Fully inspectable in the Unreal Editor Details panel.
   - Modifiable dynamically via Blueprint or C++ (`UNiagaraComponent::SetVariableFloat`).
   - Clean, standard serialization compatible with UE cooking, DDC, and packaging.
   - Eliminates all reliance on raw binary patching.

### Option B: Direct Niagara System Editor Stack Authoring
If runtime parameterization is not required, author the constants directly in the Niagara Editor:
1. Open `NS_Boss_PhaseTwoAura` in Niagara System Editor under `ENGINE_LOCK`.
2. In Emitter `Sparks1` -> `Spawn Rate`, set `SpawnRate` to target value ($70.0$).
3. In Emitter `Sparks2` -> `Spawn Rate`, set `SpawnRate` to target value ($52.5$).
4. In Emitter `Sparks1` -> `Initialize Particle` -> `Sprite Size`, set uniform/min/max.
5. In System Overview -> `Fixed Bounds`, enable fixed bounds and set Min `(-175, -175, -175)`, Max `(175, 175, 175)`.
6. Apply changes and save asset.

---

## 3. Promotion & Verification Pipeline (When Owner Decides)

When Owner confirms selection:
1. **Acquire Lock:** Acquire `ENGINE_LOCK.json`.
2. **Apply Authoring:** Execute Option A or Option B on `NS_Boss_PhaseTwoAura`.
3. **Readback Audit:** Run `python Scripts/Tools/diff_phase_two_auras.py` to confirm exact matching target floats.
4. **Automated Verification:**
   - Execute AU-C19 paired PIE capture (`pie_aura_comparison.py`) to confirm target mean gray (`~65.0` for BoostLite).
   - Run native automated test suite (`487/487` tests passing).
5. **Candidate Retirement:**
   - Remove transient candidates `NS_Boss_PhaseTwoAura_Boost.uasset` and `NS_Boss_PhaseTwoAura_BoostLite.uasset` from git once production asset is updated.
6. **Documentation Update:** Update `KNOWN_ISSUES.md`, `PROJECT_STATE.md`, and `OWNER_REVIEW_PACK.md`.
