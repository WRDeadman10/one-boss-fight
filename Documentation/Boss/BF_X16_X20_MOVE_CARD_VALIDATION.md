# Queue BF Batch 4 — MoveCard validation boundaries

Status: source audit and focused regressions are complete; the locked Development build and pinned suite are the remaining verification for this batch. No Unreal Editor, asset authoring, save, commit, or push was performed.

## Numeric validator inventory and coverage

`RPGBossMoveCards::Validate` funnels scalar card values through `Number` (`RPGBossMoveCard.cpp:18-23`): finite, `0 <= value <= 1,000,000`, with selected fields additionally strictly positive. Domain-specific rules run after those checks. Metadata clip length uses the same helper.

| Input group | Numeric fields | Additional rule | Native regression coverage |
|---|---|---|---|
| Card timeline / combat | PlayRate, CommitSeconds, ActiveStartSeconds, ActiveEndSeconds, RecoveryEndSeconds, TrackDegreesPerSecond, MinRangeCm, MaxRangeCm, FrontConeDegrees, MaxVerticalDeltaCm, HPDamage | PlayRate positive; ordered timeline; FrontCone <= 360; MinRange <= MaxRange | `MoveCard.Numbers`, `MoveCard.Rejections` |
| Warp | WarpStartSeconds, WarpEndSeconds, WarpMaxDistanceCm, WarpMaxAngleDegrees, WarpStandoffCm | Active warp: distance <= 1000, angle <= 180, commit <= start < end <= active end; defaults remain off | `MoveCard.Numbers`, `MoveCard.Rejections` |
| Hold | HoldAtSeconds, HoldMinSeconds, HoldMaxSeconds | If enabled: commit <= at < active start; 0 < min <= max <= 3 | `MoveCard.Numbers`, `MoveCard.Rejections` |
| AreaEffect (only when enabled) | ReleaseSeconds, DelaySeconds, RadiusCm, Damage, SnareSeconds, SnareSpeedScale | Radius positive; delay <= 10, radius <= 2000, snare <= 30, scale <= 1; release/timing, snare pairing, effect-not-empty and defensive exclusion | `MoveCard.AreaEffect` (all numeric members swept for NaN/Infinity and domain/bounds) |
| ChannelDrain (only when enabled) | StartSeconds, EndSeconds, TickIntervalSeconds, TickDamage, HealFraction, ConeRangeCm, ConeHalfAngleDegrees | Interval, damage, range and half-angle positive; 1–64 ticks; heal <= 1, range <= 2000, angle <= 180; timeline and add-on exclusivity | `MoveCard.ChannelDrain` (all numeric members swept for NaN/Infinity plus domain/bounds) |
| Cue | each `TimeSeconds` | Within card recovery unless it is a hold-release cue | `MoveCard.Rejections` (new NaN/Infinity cases) |
| Blade window | StartSeconds, EndSeconds, RadiusCm; conditional GrabReleaseSeconds | Radius and grab release positive; time ordered and inside active/recovery | `MoveCard.Numbers`, `MoveCard.Rejections` |
| Ring window | Start radius, speed, thickness, height, plus common start/end | Speed/thickness/height positive; no blade sockets or baked samples | `MoveCard.Rejections` (new NaN/Infinity sweep for all four ring members) |
| Baked blade samples | TimeSeconds, BaseCS, TipCS components | Finite, strictly increasing/ordered time; vectors finite and abs max <= 100,000; samples cover full window | `MoveCard.BakedLastEndpointBoundary`, `MoveCard.BakedSampleEndpointMutation` and existing baked-sample cases |

The test sweep now also includes `MaxVerticalDeltaCm`, all five warp scalars, and all three hold scalars. Existing AreaEffect and ChannelDrain tests already cover every enabled add-on numeric member. Disabled add-ons remain skipped by validation, default false, and copied into immutable compiled snapshots; `MoveCard.SnapshotAndFailure` asserts this behavior.

## Phase membership and fail-closed combinations

The C++ rule rejects more than four additional phase IDs, `NAME_None`, the primary phase repeated as an additional phase, and duplicate additional IDs (`RPGBossMoveCard.cpp:60-65`). `CompileMetadata` resets its output before validation and only publishes on a clean result (`RPGBossMoveCard.cpp:220-228`). The native `MoveCard.Numbers` cases now include mixed arrays with a valid phase plus `NAME_None`, and a valid phase plus a duplicate, so a valid member cannot mask an invalid one.

The authoring preflight had two contract gaps: it accepted an empty additional phase string and did not apply the C++ generic `1,000,000` numeric ceiling. The script now validates nonempty string names, list type, four-item maximum, primary/additional distinction, uniqueness, finite representable numeric values, and the same generic ceiling. Focused tests cover each refusal class and the mixed-valid/invalid combinations.

## Authoring preflight result (offline only)

Read-only `read_f5_cards` + `build_candidate_specs` + approved S1/S2 range overlay produced these eight candidate IDs in order:

`Move_Sevarog_Swing1_Medium`, `Move_Sevarog_Swing2_Medium`, `Move_Sevarog_Swing3_Slow`, `Move_Sevarog_Speedburst`, `Move_Sevarog_Swing1_FAST_v2`, `Move_Sevarog_Ultimate_Swing_120fps_C1277`, `Move_Sevarog_Subjugation_C1277`, `Move_Sevarog_Soul_Siphon_C1277`.

Static unresolved gates: none. All current row numeric fields and enabled optional add-on values passed the strengthened preflight. This was not the Unreal C++ dry-run bridge and establishes no asset load/save or live acceptance. Exact fail-closed reasons are covered offline: nonfinite, negative, above-ceiling or unrepresentable number; malformed/empty/duplicate/primary-colliding/overlong phase set; unresolved source/profile gates.

## Verification

- `Scripts/Tools/test_bf_x16_x20_move_card_contract.py`: **3/3 PASS**.
- Native changes are limited to `RPGBossMoveCardTests.cpp`; C-1155 Development build exit **0** and DD27j-pinned `OneBossFight` suite **509/509 passed**, 0 failed; both locks released.
- Receipt: `Docs/BossCombatReview/Execution/Codex/BF_X16_X20_MOVE_CARD_VALIDATION/Run_20261110_192136/`.
- No authored `/Game` path was touched; no output was saved.
