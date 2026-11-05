# Parry visual and sound inventory (Queue D24)

Scope: read-only inventory of parry-specific presentation in maintained source, current guidance, and asset-path names. No asset was opened, edited, or run in Editor; no code/test/build/PIE execution.

## Inventory

| Status | Area | Evidence and limit |
|---|---|---|
| Present | Grade label and telemetry | `URPGPlayerParry::NotifyParried` stores `LastGrade`; `LastGradeName` returns Perfect/Good/Late/None (`Source/OneBossFight/Player/RPGPlayerParry.cpp:121-144`). `RecordParriedContact` logs grade and calls the boss reaction/recovery handoff (`Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:35-45`). Boss overlay can display the grade (`RPGFrameworkBossCharacter.cpp:734-752`). This is text/log feedback, not animation or audio. |
| Present, opt-in | Boss posture/stagger reaction | `NoteParried` defers profile-scaled posture reaction to the next boss tick (`RPGFrameworkBossCharacter.h:43-49`; `.cpp:237-240`); `PARRY_HOWTO.md` describes the BUILD-150 posture/stagger proof. No player parry pose is implied. |
| Present, opt-in | Extra boss recovery | `ParryRecoveryScale` adds an extra neutral interval after a card finishes; the current guide says it is not live-proven (`PARRY_HOWTO.md`, “What the parry does”). This is timing/AI behavior, not a visual/audio cue. |
| Present, generic move cues | Boss attack-card VFX/SFX | Move cards carry generic cue data with `None`, `HitSpark`, `DodgeDust`, or `BloodBurst` visuals (`Source/OneBossFight/Player/RPGBossMoveCard.h:28-40,111`). The executor preloads cue sounds and fires authored time/hold-release cues through flipbook effects and `PlaySoundAtLocation` (`Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:479-530`). These cues are independent of the resolver's `Parried` outcome at `:282-294,405-416`; their existence does not establish a parry-triggered effect. `rpg.CueMode` controls visual/audio accessibility modes (`:48`). |
| Asset present; use unknown | Generic hit-spark flipbook/material | `Content/OneBossFight/Effects/Flipbook/T_FB_HitSpark.uasset` and `MI_Boss01_FB_HitSpark.uasset` exist by path. This inventory did not inspect package contents, cue assignments, or runtime appearance, and the asset names do not prove parry use. |
| Asset present; presentation unknown | Parry proof content | `DA_Sevarog_ParryReaction_PARRY.uasset` and `L_SevarogFrameworkProofPARRY.umap` exist by path. `PARRY_HOWTO.md` says the documented BUILD-150 proof shows posture/stagger, not parry animation or sound. Package contents were not read back here. |
| Not found in reviewed source | Dedicated player parry animation/audio trigger | The parried-result branches in the executor call `RecordParriedContact` and log contact; `URPGPlayerParry` records grade/stamina/tags. Those inspected paths contain no montage, animation, sound, Niagara, or particle dispatch tied to the parry result. This is bounded to maintained source paths reviewed, not all pack Blueprints. |
| Unknown | Pack ability/Blueprint presentation | Sword/Claymore style setup and `GA_PlayerParry` behavior are pack assets outside the inspected native dispatch path. Their actual authored montages, audio, and event behavior require Editor/package readback and runtime observation; asset existence alone cannot settle it. |

## Conclusion

The framework has text/log grade feedback, deferred boss posture/stagger reaction, optional recovery timing, and generic attack-card visual/audio cues. No dedicated player-facing parry animation or sound dispatch was found in the reviewed C++ paths, and the documented PARRY proof expressly lacks those cues. Pack Blueprint behavior and actual asset assignments remain unknown; do not call presentation globally absent based on this source audit.

## Verification boundary

Static C++/documentation/path inventory only. The generic hit-spark path and proof-map assets were identified by filename, not opened or validated. No feature/runtime or pack-Blueprint presentation claim is made.
