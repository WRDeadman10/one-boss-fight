# Queue BI — X11–X15: Sevarog Phase-Two Aura Source and Evidence Gate

Status: **offline source/documentation audit complete**. No Niagara asset, config, runtime source, Editor, Unreal, build, package, profiler, or test operation was performed. The report separates existing Ember evidence from Sevarog proposals.

## X11 — Existing Ember facts versus Sevarog proposals

`BB_A24_SEVAROG_PHASE2_AURA_CANDIDATES.md` is expressly spec-only and lists three Sevarog visual candidates. `BC_A26_A30_SFX_AURA_COOK_PRECHECK.md` specifies proposed Sevarog fixed bounds of ±220 cm, up to 120 sprites, and proposed `User.Scale`, `User.Opacity`, `User.Color_Primary`, and `User.Color_Secondary` controls. These are proposal/acceptance requirements, not authored Sevarog Niagara facts.

`RPGTier2BossPresentation.cpp` currently assigns the project-owned Ember `NS_Boss_PhaseTwoAura_BoostLite_Authored` path to its generic Tier 2 presentation component. That source fact does not establish that any Sevarog candidate was selected, copied, re-tinted, or visually accepted. No owner choice is inferred.

## X12 — Reference type and exclusions

- Runtime properties are typed `TSoftObjectPtr<UNiagaraSystem>` (`RPGTier2BossPresentation.h:26`; `RPGSevarogDirector.h:50`; `RPGEncounterBinding.h` presentation fields). A legacy Cascade `P_*` asset cannot satisfy that type directly.
- Candidate destination in BB-A24/BC-A26 is project-owned `/Game/OneBossFight/VFX/NS_Sevarog_PhaseTwoAura_*`; the Paragon source motifs are references only, with no pack edits authorized.
- BB-A24 marks `/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura_Boost` and `...BoostLite` as historical do-not-reference candidates under C-1210. This exclusion is distinct from the separately authored and currently referenced `NS_Boss_PhaseTwoAura_BoostLite_Authored` asset; the similarly named paths must not be conflated.

## X13 — Lead readback checklist for any future selected candidate

After an Owner selection and authorized Lead authoring, capture exact asset path and class; system and emitter fixed-bounds mode and extents; scalability/cull settings; emitter count and measured peak active particles; exposed parameter names, types, defaults, and runtime bindings; attachment mesh/socket and relative transform; spawn timing; visibility in both arena backgrounds; and the post-transition/reset/death/EndPlay state. Keep the candidate's source package and the resulting project-owned asset identity/hash in the receipt. A source property or screenshot alone is not proof of a live phase-two visual or cost.

## X14 — Source lifecycle and first-use boundary

The generic component's constructor sets a 0.1-second tick interval in Development, assigns the authored Ember BoostLite soft path, and leaves the attachment socket at `NAME_None`. `TickComponent` reads the Tier-2 toggle and boss health; it clears the component when disabled or when `ShouldShowAura` is false, then synchronously loads the configured `UNiagaraSystem` and attaches it after `ShouldSpawnAura` passes. `bAuraActivatedThisPhase` prevents repeat spawn after success. `ClearAura` destroys the component and resets that latch; `EndPlay` calls `ClearAura`.

The separate `URPGSevarogDirector` has its own `PhaseTwoAuraEffect`, `ApplyPhaseTwoVisuals`, `ClearPhaseTwoVisuals`, and reset path. The inspected source uses `LoadSynchronous` at visual application and cleans up on phase/reset/end paths; no explicit prewarm call is evident in the inspected path. This is a source observation only; it does not establish a runtime hitch, actual selected asset, or missing cleanup in any other lifecycle path. First-use hitch absence requires a measured, authorized run.

## X15 — Batch disposition

The candidate matrix, type constraints, authored-versus-proposed distinction, readback fields, and source lifecycle are recorded here. Owner selection, Niagara authoring, Lead live readback, packaged cook proof, and performance measurement remain separate gates. No project asset or default changed.
