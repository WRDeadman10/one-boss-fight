# Shipping guard inventory audit (S181)

Static review of source console-variable registrations and their build guards, refreshed against `Documentation/Boss/TEST_HOOKS.md`. No build or Shipping binary was inspected.

## Inventory and guard result

- `py Scripts/Tools/check_shipping_guards.py --root .` reported `registered_cvars=45 unguarded=6` (exit 0). The 45 consist of 38 literal registrations and seven macro-generated performance registrations; counting the separate FireShadows CVar gives eight performance controls and 37 other runtime/proof controls.
- All test/proof/measurement registrations other than the six runtime controls below are inside `#if !UE_BUILD_SHIPPING` spans on source review. This includes `BossProof*`, `BossComboDuplicateGate`, `Catalog*`, `WakeClip`, `RemainsFormSeconds`, `CueMode`, `CameraProbe`, `Screenshot*`, `ParryStaminaCost`, `Debug`, and the `rpg.Perf.*` controls. The performance macro's Shipping branch contains no console-variable registration.
- The six source-visible controls are `rpg.BossOverlay`, `rpg.CloseTelegraph`, `rpg.Build`, `rpg.CameraDebug`, `rpg.Legend`, and `rpg.LegendShakeScale`. `TEST_HOOKS.md` classifies them as intentional Shipping-visible runtime controls, and mailbox C-702 recorded the same disposition. Feature decisions also document `Build`, `Legend`/shake accessibility, and the owner-selected close-telegraph default.
- Refreshed `TEST_HOOKS.md`: its prior 44 total / 36 named count was stale. Current source is 45 total / 37 non-performance controls / eight performance controls. Removed duplicate table entries for `CatalogSource` and `BossProofCenterBias` so each named control appears once.

## Disposition

At source level, test/proof/measurement controls remain behind the intended non-Shipping guard; the six exceptions have an existing team disposition as runtime controls. Acceptance is met for registration guards/documented exceptions. Lead recorded the remaining binary-verification limit as KI-168. This is not proof of the compiled Shipping binary's symbol table or runtime console registry. No build, binary inspection, tests, or Editor/runtime run was performed.
