# Gap-closer animation asset inventory (Queue D33)

Scope: read-only inventory of maintained source references, candidate content filenames, and what cannot be established without asset/editor readback. No asset was opened or modified; no build, tests, or Editor run.

## Maintained source

- `RPGBossGapCloserRules::ShouldClose` is a pure range/hysteresis decision and is explicitly documented as unwired; its caller owns chase state and action start/stop (`Source/OneBossFight/Player/RPGBossGapCloserRules.h:6-16`; `Documentation/Boss/RULES_REFERENCE_116_GAP_CLOSER.md:3`). It contains no `UAnimSequence`, `UAnimMontage`, slot name, soft object path, or asset assignment.
- `RPGBossApproach` supplies smoothstep distance-profile math and is consumed by the generic framework executor's optional warp ease (`Source/OneBossFight/Player/RPGBossApproachRules.h:5-27`; `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:422-477`). This supports a generic card warp path described as gap-closer motion, but does not identify a specific assigned gap-closer animation or connect the separate `ShouldClose` rule to that card.
- The generic framework move card carries a sequence and slot (`Source/OneBossFight/Player/RPGBossMoveCard.h`; `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:151-173`), but source does not associate a card or sequence with a specific gap-closer action. This generic playback route is not evidence of an assigned gap-closer asset.
- The native pack melee timing inventory in `RPGAttackTracker.cpp:44-95` names boss attacks A1/A1b/A3a/A3b/A4/A5/A6 and their montage/clip refs; no entry is identified as a gap-closer.

## Content filename inventory and evidence boundary

- A read-only path-name scan under `Content/OneBossFight` found proof/attack animation assets and a `Move_Sevarog_BandGap_MOV001` framework card, but no path named gap-closer. A path-name scan cannot establish sequence contents, Blueprint assignment, slot configuration, or whether an ambiguously named asset is used for gap closing.
- No target Blueprint, data asset, sequence, montage, or AnimBP was reflected/read back in Editor. Therefore the assigned animation, montage, slot, root-motion setting, and actual move-to-asset binding are **UNKNOWN**, not missing.
- `Documentation/Boss/RULES_REFERENCE_116_GAP_CLOSER.md` and `Documentation/Boss/TEST_COVERAGE.md` establish pure rule coverage and unwired status; they do not provide asset assignment evidence.

## Disposition

No confirmed missing asset or assignment defect. The only supported source conclusion is that the native gap-closer range rule has no animation dispatch and is documented unwired. To identify an authored candidate, inspect the actual move/action data and animation references in Editor, recording object paths and slot/sequence assignments before making an assignment claim.
