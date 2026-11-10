# BB-A24: Sevarog Phase-2 Aura Candidates (`PhaseTwoAuraEffect`)

**Queue Lane:** `QUEUE_BB` Task `BB-A24` (Antigravity)  
**Authority:** `Documentation/Boss/QUEUE_BB.md`, `[C-1267]`  
**Status:** SPEC-ONLY (Zero VFX asset edits, zero C++/DataAsset wiring; awaits Owner visual selection and Lead Niagara/PIE verification)  

---

## 1. C++ Slot & Asset Type Constraint (`TSoftObjectPtr<UNiagaraSystem>`)

Inspection of the codebase confirms `PhaseTwoAuraEffect` is strictly typed as **`TSoftObjectPtr<UNiagaraSystem>`**:
- `Source/OneBossFight/Boss/RPGSevarogDirector.h:50` (`TSoftObjectPtr<UNiagaraSystem> PhaseTwoAuraEffect;`)
- `Source/OneBossFight/Player/RPGEncounterBinding.h:359,410` (per-boss encounter presentation config)
- `Source/OneBossFight/Boss/RPGTier2BossPresentation.h:26`

**Critical Compatibility Finding on Disk:**
- `Content/ParagonSevarog/FX/Particles/` contains **35 legacy Cascade `UParticleSystem` assets** (`P_UltimateLooping`, `P_SoulSwirlsBody`, `P_ShadowTrails`, `P_FaceDark`, `P_SoulStageEmbers`, etc.) — **zero** `UNiagaraSystem` (`NS_*`) assets.
- `TSoftObjectPtr<UNiagaraSystem>` **cannot** reference a Cascade `P_*` asset directly; any Paragon Sevarog motif selected below requires either authoring/converting a project-owned `UNiagaraSystem` under `/Game/OneBossFight/VFX/` using Sevarog's existing FX materials (`M_ShadowSwirls_BrightColors`, `M_SiphonSoulsBody`, `M_SevarogSwirls`) or creating a color/palette-shifted project copy (`NS_Sevarog_PhaseTwoAura_*`).

---

## 2. Candidate Matrix (For Owner & Lead Evaluation)

| Candidate ID | Visual Identity & Motif | Repo Source Reference (On Disk) | Implementation Path Required | Boss01 Separation (`[C-1175]`/`[C-1208]`) & Gameplay Notes |
|---|---|---|---|---|
| **Cand A (Spectral Wraith Mantle — Recommended)** | Dark violet/emerald drifting shadow swirls hugging Sevarog's ribcage, shoulder pauldrons, and trailing cape edge (`P_UltimateLooping` + `P_SoulSwirlsBody` look) | Visual motif & materials:<br>- `/Game/ParagonSevarog/FX/Particles/Abilities/Ultimate/FX/P_UltimateLooping`<br>- `/Game/ParagonSevarog/FX/Particles/Abilities/SoulSiphon/FX/P_SoulSwirlsBody`<br>- Materials `/Game/ParagonSevarog/FX/Materials/Smoke/M_ShadowSwirls_BrightColors`, `.../Energy/M_SiphonSoulsBody` | Author new `NS_Sevarog_PhaseTwoAura_Shadow` (`UNiagaraSystem`) in `/Game/OneBossFight/VFX/` mimicking `P_UltimateLooping` orbit/swirl emitters with bounded GPU/CPU sprite count (`<= 60` particles) and `User.Opacity` scale | **Full separation from Ember Warden:** Cool spectral emerald/indigo-violet palette contrasts sharply with Ember Warden's warm orange-crimson `NS_Boss_PhaseTwoAura_BoostLite_Authored`; keeps dark silhouette readable against night arena fog |
| **Cand B (Soul Stack Shoulder Mist)** | Layered dark smoke + subtle ghostly embers rising around spine/pauldrons (`P_SoulStageEmbers` + `P_ShadowTrails`) | Visual motif & materials:<br>- `/Game/ParagonSevarog/FX/Particles/Abilities/SoulStackPassive/FX/P_SoulStageEmbers`<br>- `/Game/ParagonSevarog/FX/Particles/Abilities/SoulStackPassive/FX/P_ShadowTrails`<br>- Material `/Game/ParagonSevarog/FX/Materials/Smoke/M_Sevarog_ShadowSkirt` | Author `NS_Sevarog_PhaseTwoAura_Mist` (`UNiagaraSystem`) attached to `spine_03` socket with low-alpha dark shadow wisps + sparse soul sparks | **Lowest screen clutter:** Zero bright bloom flare (`mean luminance delta < 3`), preserves clear readability of Sevarog's `Swing1_Medium` / `Ultimate_Swing_120fps` hammer windup |
| **Cand C (Re-Tinted Project Niagara Structural Baseline)** | Structural clone of `NS_Boss_PhaseTwoAura_BoostLite_Authored` retargeted from orange-red ember to Sevarog spectral green/indigo via exposed Niagara `User` color/size parameters | Project Niagara baseline:<br>- `/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura_BoostLite_Authored` | Duplicate to `/Game/OneBossFight/VFX/NS_Sevarog_PhaseTwoAura_BoostLite_Cyan` (`UNiagaraSystem`), set exposed color/emissive `User` parameters to spectral emerald/cyan; zero changes to Ember's asset | **Fastest engineering path:** Reuses proven Niagara bounds (`C-1202`/`C-1210`), `PhaseTwoAuraComponent` attach lifecycle, and reset cleanup (`ClearPhaseTwoVisuals`); requires explicit Owner check that silhouette differs clearly from Ember |

**Explicitly Excluded Assets (`DECISIONS.md:1651`):**
- `/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura_Boost` and `/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura_BoostLite` are byte-patched historical review candidates (`C-1210`: do-not-reference).

---

## 3. Opt-In & Performance Guardrails

1. **Default Unassigned:** `DA_Boss_Sevarog_Draft` keeps `PhaseTwoAuraEffect` null/empty until Owner selects a candidate reel and Lead verifies lifecycle cleanup (`EndPlay`, `ResetEncounter`, `Current <= 0.f` in `RPGSevarogDirector.cpp`).
2. **Perf Budget (`AGENTS.md` / `16.67 ms` RTX 2060 Super 60 FPS):** Fixed bounds required (`[C-1202]`), spawn rate capped under Niagara scalability, and prewarmed/bound before Phase 2 threshold trigger so zero first-use compilation hitch occurs during combat.
3. **Zero Pack Edits:** No assets under `/Game/ParagonSevarog/` modified.
