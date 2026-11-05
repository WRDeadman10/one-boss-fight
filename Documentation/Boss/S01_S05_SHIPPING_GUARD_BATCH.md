# Queue S batch S01–S05: Shipping guard audit

Date: 2026-11-05. Scope: source-only audit and offline tooling; no Unreal, package, or C++ build was run by Codex.

## S01 — non-Shipping declarations and references

The new checker scans all `Source/**/*.h` and `Source/**/*.cpp` for explicit `TAutoConsoleVariable`, `FAutoConsoleVariableRef`, and `FAutoConsoleVariable` declarations in Development-only preprocessor branches, then checks same-file identifier references reachable in Shipping. Run result: 35 explicit declarations, zero Shipping-visible references. The first-line report is deliberately scoped to CVar declarations and is not a C++ parser.

| Declaration / use | Audit result |
|---|---|
| `Boss/RPGFrameworkMoveExecutor.cpp:48` `CVarCueMode`; use at `:519` | Lead guarded the read at `:518` and Shipping fallback is `Mode=0` at `:520-521`; keeps existing CVar default (visual and sound). |
| Other explicit declarations printed by `python Scripts/Tools/check_shipping_guards.py` | All 34 remaining declarations have no Shipping-reachable identifier use according to conditional-branch analysis. Full declaration paths/lines are emitted by the command. |
| `Arena/RPGPerfSwitches.cpp:7` macro-generated `CVar##Func` | Not in the explicit-declaration count. Manual inspection: Development macro declares and reads each CVar; Shipping macro expands each public helper to `return true`, so no generated CVar symbol is referenced. `CVarFireShadows` is explicit and uses `-1` in its Shipping `#else` at `:21`. |
| Other non-Shipping test/debug declarations and their use sites | Reviewed `#if !UE_BUILD_SHIPPING` locations across runtime Source. Test/debug implementation blocks remain branch-guarded; header APIs retained for UHT have Shipping no-op/false bodies (e.g. `Player/RPGCombatDebug.h:87` and implementation guards). No additional unguarded missing identifier found in the source review. |

The checker detects the BUILD-222 failure class only for its documented explicit CVar declaration forms. Macro-generated declarations and general C++ declarations still require the manual audit above; no compiler result is claimed.

## S02 — remaining unguarded CVar use

No remaining explicit CVar use violation was reported. The known BUILD-222 use was fixed by Claude before this audit; the fix preserves the declared default `0` in Shipping. No additional Source changes were needed by Codex.

## S03 — offline checker and fixtures

`Scripts/Tools/check_shipping_guards.py` scans Source and exits nonzero on an unguarded Shipping-visible CVar identifier. `Scripts/Tools/test_check_shipping_guards.py` covers a guarded declaration/use, an unguarded seeded use (must fail), and a reference in the Shipping `#else` branch. Both normal and isolated runs pass 3/3; Source scan reports `declarations=35 shipping_uses=0`.

## S04 — editor/dev-automation guards in runtime code

| Area / symbol | Runtime-source finding |
|---|---|
| `Combat/RPGSkeletonUtils.cpp:12-49` | Mesh socket mutation uses editor-only APIs under `WITH_EDITOR`; packaged branch returns zero. |
| `Audio/RPGArenaAmbience.cpp:22`, `Arena/RPGArenaDressing.cpp:85`, `Arena/RPGGreyboxArena.cpp:236`, `Arena/RPGFireSource.cpp:136`, `Arena/RPGEmberField.cpp:26` | `RerunConstructionScripts` calls are guarded by `WITH_EDITOR`, as required by the API's availability. |
| `Scratch/RPGScratchRouteA.cpp:20-24,92+` | Asset registry/package/save includes and asset creation body are editor-only. Runtime task class remains, but authoring operation returns false outside editor. |
| `Player/RPGBossHydrationPreparation.{h,cpp}` | Fault injection globals, scopes, owned-component test accessors, and registration failure hooks are declared/used inside `WITH_DEV_AUTOMATION_TESTS`; production path has no test hook state. |
| Runtime headers with dev-only test accessors (`RPGBossEncounter.h:88+`, `RPGBossPreparationRegistry.h:104+`, `RPGBossHydrationPreparation.h`) | Declarations are inside `WITH_DEV_AUTOMATION_TESTS`; their definitions/callers are likewise conditional. |
| `Boss/RPGFrameworkBossCharacter.h:23-25` | Conditional block contains only a comment; `InitializeProof` declaration itself is unconditional. No conditional-only symbol leaks from this block. |
| `Tests/**/*.cpp` | Test translation units are gated by `WITH_DEV_AUTOMATION_TESTS`; editor fixture calls are nested under `WITH_EDITOR`. |

No unguarded editor-only or automation-only symbol use was found in this targeted runtime-source review. This was a source inspection, not a Shipping compile.

## S05 — packaged CVar behavior (no behavior change)

| CVar / feature | Compile-time and default behavior | Player-facing effect / evidence |
|---|---|---|
| `rpg.CueMode` | Registration and tunable read are non-Shipping only (`Boss/RPGFrameworkMoveExecutor.cpp:47-48,518-522`). Shipping forces `Mode=0`, the existing default. | Every boss cue retains visual and sound feedback in Shipping; modes 1–3 are Development-only adjustments. |
| `rpg.Legend` | CVar is registered in runtime source (`Player/RPGLegend.cpp:23-24`) with default `1`; it is not compiled out by a Shipping guard. | Default enables legend hit-stop/slow-motion/shake and phase-two music swap. A packaged override path was not verified here; do not claim the setting is console-accessible to players. |
| `rpg.Build` | CVar is registered in runtime source (`Player/RPGBuildLoadout.cpp:19-21`) with default empty. | Empty means no selected build and the pack-provided weapon remains; valid names choose the loadout. The packaged override path was not verified here. |
| `rpg.WakeClip` | Development-only test variable (`Player/RPGBossDormantWake.cpp:94-97`); Shipping always plays the authored wake clip. | Test timing skip cannot remove the wake animation from a Shipping fight. |
| `rpg.Debug` | Registration and debug paths are non-Shipping (`Player/RPGCombatDebug.cpp:32-40` and guarded methods). | Combat diagnostic overlay/logging is absent in Shipping. |

Queue S task text implies all listed CVars become fixed defaults in Shipping. Source evidence contradicts that generalization for `rpg.Legend` and `rpg.Build`: their registrations are not under a Shipping guard. Their registration/default is documented; actual packaged override availability is left unasserted pending a packaged console test.
