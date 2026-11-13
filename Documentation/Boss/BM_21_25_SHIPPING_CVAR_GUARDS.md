# BM-21..25: Shipping console-variable guard census (lane BM, batch 5 of 10; KI-168 / KI-185)

C (implementer), 2026-11-12.

New file: `Scripts/Tools/test_shipping_cvar_guards.py`. Source-only: nothing was compiled or run. No source change. The binary-level Shipping proof of KI-168 stays **engine-gated**.

## BM-21: census

Every `TAutoConsoleVariable` and `FAutoConsoleCommand*` declaration in `Source/OneBossFight/**/*.cpp`, including declarations that span several lines: **52**.

| Guard | Count |
|---|---|
| none (Shipping-visible) | **6**: `rpg.BossOverlay` (`RPGFrameworkBossCharacter.cpp:53`), `rpg.CloseTelegraph` (`RPGAttackTracker.cpp:27`), `rpg.Build` (`RPGBuildLoadout.cpp:19`), `rpg.CameraDebug` (`RPGCameraRig.cpp:22`), `rpg.Legend` and `rpg.LegendShakeScale` (`RPGLegend.cpp:29,32`) |
| `#if !UE_BUILD_SHIPPING`, or the `#else` of `#if UE_BUILD_SHIPPING` | 43 |
| `#if UE_BUILD_DEVELOPMENT` | 3 (`rpg.AttackTracker.A2PreviewClip`, `rpg.Art.Tier1`, `rpg.Art.Tier2`) |

## BM-22: KI-168, source classification

**The 6 Shipping-visible controls are exactly KI-168's list.** The source classification still matches the team's C-702 disposition. The packaged-binary registry or symbol check remains **not done** (engine-gated).

## BM-23: KI-185 pattern (a guarded CVar referenced from Shipping-compiled code)

**Found: none.** Every reference to each of the 46 guarded variables sits inside a non-Shipping region.

The first scan showed one apparent hit, `RPGBossRemains.cpp:137`. Reading the source showed it is in the `#else` branch of `#if UE_BUILD_SHIPPING` (`:134-138`), so it is correctly guarded. The scanner now treats that `#else` as a non-Shipping region. Comments are ignored, which also removed the `RPGFrameworkMoveExecutor.cpp:722` comment hit.

**Note on KI-185's text:** it cites "35 explicit guarded CVar declarations". The current tree has **46** guarded declarations (43 + 3), because the code has grown since that audit.

## BM-24: regression test

`python -m unittest discover -s Scripts/Tools -p test_shipping_cvar_guards.py -v` → **`Ran 3 tests ... OK`**. It checks:
- the Shipping-visible set equals the 6 KI-168 controls;
- the census size is 52;
- no guarded CVar is referenced from Shipping-compiled code.

## BM-25: limits

- **A textual preprocessor model:**
  - It handles `#if`, `#elif`, `#else` and `#endif` nesting with these three guard forms.
  - It does not evaluate macros, `#ifdef` or composite conditions such as `#if !UE_BUILD_SHIPPING && X`. A condition it does not recognize is treated as not guarding, which is the conservative choice.
- References are found by identifier match within the declaring `.cpp` only; cross-file use of a CVar through `extern` would not be seen.
- **This is not proof of Shipping compile success:** BUILD-222-style packaging stays engine-gated.
