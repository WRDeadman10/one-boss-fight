# Queue BD Batch 1: X01–X05 framework integration map

## X01 — native-health and HUD binding

`ARPGFrameworkBossCharacter` implements `IRPGNativeBossHealth` (`Source/OneBossFight/Boss/RPGFrameworkBossCharacter.h:17,71–76`). Existing `URPGBossHud` creation is gated by `IsPackBoss` (`Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:888–892`), and its health/victory path reads the pack `Attribute.Health` adapter (`Source/OneBossFight/Player/RPGBossHud.cpp:407–452`). No framework-native binding is established by this source path. Proposed seam remains: bind HUD to one encounter-owned health provider that can use the native interface or pack adapter. Display metadata and encounter policy must be separately owned.

## X02 — death and encounter ownership

Framework `ApplyHit` subtracts native health and invokes `Die` on depletion (`RPGFrameworkBossCharacter.cpp:771–798`). `Die` is idempotent, stops movement, aborts the executor, and logs proof result (`:1008–1018`). The inspected path does not signal `URPGBossEncounter`, HUD victory, music, or retry. This remains a source-level integration gap; no gameplay execution was used to characterize it.

## X03 — proof route versus production route

`InitializeWithProfileForTest` enters the standalone same-world proof initialization route (`RPGFrameworkBossCharacter.cpp:66–73,90–158`). The generic encounter selection path currently requires a pack boss/player binding (`RPGEncounterSelectionSubsystem.cpp:161–195`, as documented in `BB_X26_X30_FRAMEWORK_BINDING_AUDIT.md`). These are distinct routes. The test bridge does not establish a production GameMode/encounter owner, spawn policy, or UI binding.

## X04 — reset and generation ownership

`CanRestart` requires initialized, non-failed terminal state and a strictly newer generation (`RPGFrameworkBossCharacter.h:78–80`). `RestartEncounter` rearms the executor and resets actor-owned per-generation state (`RPGFrameworkBossCharacter.cpp:988–1006`). The proof fixture checks restart eligibility before rewriting target health (`RPGFrameworkProofFixture.cpp:99–110`). These guards support the isolated fixture path; they do not define production retry ownership, player reset, actor replacement, or cross-actor generation coordination.

## X05 — Lead acceptance checklist

Before any production integration is accepted, Lead should establish: (1) one encounter owner for framework boss and player, (2) health provider bound to HUD for the same generation, (3) idempotent death completion delivered once, (4) victory/music/retry transition ownership, (5) reset/replacement generation monotonicity, and (6) teardown of HUD, executor, movement, and stale callbacks. Live PIE/build/package evidence is Lead-owned; this checklist does not authorize implementation or infer acceptance.

## Scope

Static source/documentation audit only. No runtime test, native test, build, Editor, PIE, asset, lock, commit, or push operation was performed. Supporting audit: `Documentation/Boss/BC_X11_X15_FRAMEWORK_LIFECYCLE.md` and `Documentation/Boss/BB_X26_X30_FRAMEWORK_BINDING_AUDIT.md`.
