# G1 — Binding source and boss-selection store

## Decision for Lead review

Use a **runtime encounter-definition asset selected by a GameInstance-owned selection store**, then create an **ephemeral `ARPGEncounterBinding` from a strict pre-BeginPlay pawn census**. Keep the accepted `RPGBossActivation::ActivateWorld` and `CompileWorldInput` contracts. Do not edit `L_SevarogArena.umap` for the initial integration. This is Option R's typed data source with the existing binding-actor transport; it avoids Option P's binary-map references and avoids changing the accepted compiler to add an Option S overload.

This design is additive and preserves the current library's refusal checks. `OnWorldBeginPlay` currently calls `Attach` on every pawn (`Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:57-65`), while `ActivateWorld` remains a standalone composition API with explicit world, binding, selections and manifest inputs (`Source/OneBossFight/Player/RPGBossActivation.h:39-44`). The DD30 chronology recorded `bindings=0` and `selection_store=NOT_DEFINED`; its options paper predates the current fail-closed direction and incorrectly treats clean fallback to legacy as acceptable. The owner/Lead direction now requires a missing or rejected data activation to leave the framework boss inactive, with no legacy boss bundle fallback.

The selection store should own a soft reference to an authored encounter-definition asset, not actor pointers. The asset should name the encounter instance, boss definition, player definition, exact slot/role/target mapping, selected boss phase, and caller-supplied stable manifest string. At world start, resolve and validate the asset, census exactly one supported boss and player, create an unbegun transient binding actor, and derive the two explicit selections from the same immutable record. Use the existing catalog subsystem only for its published content epoch; current `RPGCombatRegistry::ForWorld` is the compiler's content authority (`RPGBossWorldInputCompiler.cpp:55-94`). The compiler takes a caller-supplied 64-hex manifest string (`RPGBossWorldInputCompiler.cpp:315-351`); do not describe that string as a catalog-derived hash until a source-of-truth implementation exists.

## Why this binding source

- It keeps the existing validator, preparation and owned-registration pipeline intact, so behavior and cleanup remain covered by the current native suites.
- A transient binding avoids stale placed actor references when a player pawn is replaced and avoids changing the main level's binary package.
- A GameInstance-owned selection record survives world transitions while storing definitions/configuration rather than weak pawn identities; each world must recensus actors and mint fresh generation identity.
- The existing `URPGCombatCatalogSubsystem` publishes weapon/build content, not boss-definition selection. Reusing it as a boss-selection database would conflate two domains.
- Failure is unambiguous: no selection, ambiguous actors, unresolved definition/phase, invalid manifest, clean preparation refusal, or unsafe cleanup produces a diagnostic and no legacy framework-boss attach.

## Proposed touch points and test plan

Add a typed encounter-definition asset and a GameInstance selection subsystem; add a world-start resolver/activation lease to `RPGPlayerMovesSubsystem`; preserve the existing low-level compiler/activation APIs initially. Tests must cover selection absence/duplication, exact actor census, definition/phase/manifest mismatch, success, no-fallback refusal, cleanup, world teardown and respawn with a new pawn identity. Then run paired data-path and current legacy-control PIE drivers and record every observable delta before any broader rollout.

## Decision boundary

Lead can choose the additive implementation details and release the code/test work. The owner must select which production boss and hero definitions become the default encounter and approve any change to the main `.umap` or product scope. Until that choice is made, the store has no production default and activation fails closed. Retiring the legacy path is separately owner-gated (roadmap A7).

## Evidence checked

- `Docs/BossCombatReview/Execution/Antigravity/Activation/DD30_DESIGN_OPTIONS.md` (Options R/S, chronology and their stated owner questions).
- `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:57-65` (current startup attaches every existing pawn directly).
- `Source/OneBossFight/Player/RPGBossActivation.h:39-44` and `RPGBossWorldInputCompiler.h:17-58` (standalone explicit-input contracts; no startup caller).
- `Source/OneBossFight/Player/RPGBossWorldInputCompiler.cpp:55-94,315-351` (GameInstance catalog epoch authority; caller-supplied manifest hash shape).
- Lead order C-796/C-797: fail closed with no legacy fallback; additive design choices are Lead-owned; owner decisions are scope/default/irreversible boundaries.
