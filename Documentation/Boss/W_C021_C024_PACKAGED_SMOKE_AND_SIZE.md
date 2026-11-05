# Queue W-C021–W-C024 — packaged checks and size delta

## W-C021 Shipping benchmark smoke

Added `Scripts/ShippingSmoke.ps1`. It defaults to dry-run output and needs explicit `-Execute` to package Shipping, run `RunBenchmark.ps1` with `-RPGBenchmark -RPGBenchmarkFight -RPGBenchmarkQuit` via that wrapper, then scan the Shipping binary for `rpg.Art.Tier2`, `BuildStamp.txt`, and `DEVELOPMENT BUILD`. Added `CheckShippingFeatureSymbols.py`; scanner behavior is covered for clean, ASCII-hit, and UTF-16-hit bytes. This environment did not package or launch a game.

## W-C022 compile-guard static audit

`test_shipping_feature_guards.py` verifies the Tier 2 CVar declaration is inside `UE_BUILD_DEVELOPMENT`, the build stamp has a Development implementation and Shipping no-op, and optional benchmark capture/ProfileGPU/upscaler telemetry code is inside `!UE_BUILD_SHIPPING` blocks. It also checks the wrapper invokes the binary string checker. This is source-shape evidence; only an actual Shipping binary scan proves the compiled artifact is clean.

## W-C023 packaged recovery helper

Added `Scripts/RunPackagedRecovery.ps1` for the two V-C062 arms (missing asset and wrong-class cooked Niagara object). It defaults to printing exact launch arguments and needs explicit `-Execute` to launch. Each executed arm receives an isolated packaged-run log; screenshots and visual-state verdict remain manual Lead evidence. Dry-run only here.

## W-C024 package-size delta after Tier 1 VFX

| Measure | Pre-change staged baseline | Post-Tier-1 VFX package | Delta |
|---|---:|---:|---:|
| Staged total bytes | 4,351,585,036 | not measured | not measurable |
| IoStore `.ucas` bytes | 3,249,584,880 | not measured | not measurable |
| Cooked VFX package bytes | not available | not measured | not measurable |

The old stage has no verified configuration/build identity and predates these code changes. The Tier 1 VFX hook has no newly assigned authored effect references in the reviewed V-C036–V-C040 evidence. No size savings are claimed until Lead supplies matching pre/post package identities and a per-package cook-size export.

No package, game, or Unreal process was run.
