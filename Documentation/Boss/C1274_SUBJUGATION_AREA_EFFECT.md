# C-1274 / Queue BB X16–X20 — Optional delayed area effect

**Status:** source implementation and locked Development build/full suite pass. Runtime PIE, card authoring, and Sevarog acceptance remain Lead-owned. New data stays disabled by default; no card asset or map was saved.

## Data contract

`FRPGBossAreaEffect` is an optional value on `FRPGBossMoveCardSpec` (`Source/OneBossFight/Player/RPGBossMoveCard.h:72-84,129-134`). The default `bEnabled=false` preserves existing window-only cards. An enabled payload contains release time, delay, radius, damage, and optional snare duration/speed scale.

Validator rules (`RPGBossMoveCard.cpp:60-74,108,175`): all active numbers must be finite and within the project's numeric ceiling; radius is positive and at most 2000 cm; delay is at most 10 s; snare duration is at most 30 s; release plus delay is no later than recovery end; scale is in `(0,1]`; a non-default scale requires positive duration; effect must deal damage or snare; defensive cards cannot carry an area effect. An enabled effect can satisfy the card's hit-window requirement, allowing a spell-only card with no weapon window.

## Runtime behavior

The executor snapshots the explicit encounter target's ground point when card time crosses `ReleaseSeconds`; at `ReleaseSeconds + DelaySeconds`, it checks that same target against the fixed center using radius plus capsule radius (`RPGFrameworkMoveExecutor.cpp:279-280,383-468`). If inside, positive damage flows through the existing `URPGDamageResolver` with the normal move/attack/generation identity and a dedicated `AreaEffect` hit key. Snare begins only when damage is accepted (or when the effect is snare-only) and the target is not invulnerable. It applies a temporary `MaxWalkSpeed` multiplier and rebases when another movement policy changes the unmodified speed; expiry restores the latest captured baseline only if the executor still owns the applied speed. Abort and EndPlay clear the timer and attempt safe restoration.

This implementation currently targets the duel's single explicit player pawn. It is a target-ground placement with one target test, not a general multi-actor overlap query. Runtime acceptance must verify delay placement, capsule edge behavior, guard/i-frame interactions, concurrent speed changes, natural expiry, abort, reset, and teardown. If the production effect needs multiple victims, that requires a separately reviewed target-query extension.

## Tests and evidence

Native automation `OneBossFight.Framework.MoveCard.AreaEffect` (`Source/OneBossFight/Tests/RPGBossMoveCardTests.cpp:56-89`) checks disabled-default compatibility, an enabled effect-only card, and refusal of out-of-recovery release, negative delay, zero radius, scale above 1, and mismatched snare duration/scale.

`Scripts/Editor/run_c1274_area_effect_validation.ps1` used both C-1155 locks and the pinned DD27j manifest hash. Result: Development build exit 0; 504 tests started, 504 passed, 0 failed; area-effect automation passed; suite completed; both locks released. Evidence: `Docs/BossCombatReview/Execution/Codex/C1274_AREA_EFFECT/`. No PIE or content saves were performed.

## Sevarog S7 follow-up

The source contract is implemented, but no Sevarog card is authored. Use Subjugation's C-1242 release mark only as a candidate; final radius, delay, damage, snare, target scope, visuals, audio, and cancellation acceptance need Lead/owner review. The C-1274 X11–X15 planning and S6 timing discrepancy are recorded separately in `Documentation/Boss/BB_X11_X15_SEVAROG_DESIGN.md`.
