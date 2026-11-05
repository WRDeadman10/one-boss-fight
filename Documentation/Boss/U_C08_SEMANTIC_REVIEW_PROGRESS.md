# U-C08 semantic review progress

Status: in progress. The static inventory in `U_C08_ERROR_PATH_AUDIT.md` now reports 316 candidate tokens, 185 with at least one native test source reference, and 131 with none. These counts are lexical triage; a source mention is not proof that its production branch executes or that a test observes the emitted diagnostic.

## Reviewed and extended in source

- `ActivationWorld.ReleaseNotGameThread`, `ActivationWorld.RebindRetagNotGameThread`, and `ActivationWorld.RebindRetagLeaseUnavailable`: `RPGBossActivationWorldTests.cpp` now drives off-thread release/rebind-release, off-thread retag, and game-thread retag without a lease, asserting refusal and exact tokens.
- `Actor.Missing`, `Ability.Missing`, `Item.ExpectedABI`, `Item.DeclaredBaseIdentity`, `Style.Missing`, `Item.Identity`, `Ability.Identity`, and `Style.Identity`: `RPGCombatCatalogTests.cpp` now routes these inputs through the typed ABI validator and checks the expected token suffix.
- `Catalog.Builds` and `Catalog.Weapons` missing-definition paths: a non-Shipping startup fixture corrupts a local copy of the catalog soft-reference array, never the asset, then verifies fail-closed publication and the exact error. `Catalog.SchemaVersion` also has a dedicated startup case; empty build/weapon arrays assert the empty-catalog diagnostic.
- `EncounterSelection.NotGameThread` and `EncounterSelection.WorldState`: a new transient-world test calls the guarded request off-thread and with a foreign game instance's world, expecting exact refusal tokens before definition resolution.

## Evidence boundary

The new C++ cases are authored only. Codex did not compile or execute Unreal automation; Lead must run the native suite before any coverage can be called executed. The offline scanner fixture passes 1/1 and the generated inventory matches the current scanner output. Other candidate tokens still need branch-by-branch review, and difficult paths should remain explicitly unresolved when they lack a safe fixture seam.
