# C-1124 parry hotfix and C-1126 aura candidate selector

## Parry source change

Claude's C-1124 BUILD-269 report says the 150-second natural fight exercised tracker moves A1b/A2/A3a/A3b/A1, but not A4. The old A4-only watcher therefore could not generate an attempt. The full-fight driver now treats any known tracker move with an active window as eligible, and keys attempts to a tracker instance/window edge. PARRY_DIAG includes tracker-active transitions alongside montage changes. A4 sweep-count changes remain an additional witness; the player's reflected `GetParriedCount()` delta is the success source.

`URPGPlayerParry` now exposes BlueprintPure `GetPressCount()` and `GetParriedCount()` accessors. Native source contracts assert their values; offline driver contracts assert that the success path reads the player counter and that A4 is only fallback/extra telemetry. The capture receipt validates player counter delta and press count and accepts same-montage inactive-to-active diagnostic edges.

## Aura candidate selector

C-1126 requested transient comparison support for Antigravity's proposed `NS_Boss_PhaseTwoAura_BoostLite`. The Lead-only comparison reads `AURA_COMPARE_CANDIDATE`, defaulting to the existing Boost asset. The selected object path must be under `/Game/OneBossFight/VFX/` and have matching package/object names with an `NS_Boss_PhaseTwoAura_` prefix. The receipt validator accepts that same constrained candidate namespace while keeping the approved asset fixed. This only selects an already-authored asset for Lead's transient PIE comparison; it does not author or save assets.

Example Lead environment value after the candidate asset exists:

```text
AURA_COMPARE_CANDIDATE=/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura_BoostLite.NS_Boss_PhaseTwoAura_BoostLite
```

## A4 data-gating audit limit

Source confirms A4 is a tracker move and has a low-sweep implementation. The serialized G044 encounter/attack-selection assets are `.uasset` files; the available source exports do not establish whether its A4 card is phase-two- or range-gated. C-1124's 150-second BUILD-269 observation proves only that A4 did not occur in that witnessed run. No data was changed and no stronger gating conclusion is claimed.

## Verification and ownership

`python -m unittest Scripts.Editor.test_pie_aura_comparison_contract Scripts.Tools.test_aura_warmup_receipt Scripts.Tools.test_fight_capture_receipt Scripts.Editor.test_pie_full_fight_offline -q`: 69 passed. Lead owns BUILD-270/full suite and the natural-fight rerun; Lead also owns AU-C19's BoostLite comparison. Codex did not run Unreal, PIE, Editor, or build.
