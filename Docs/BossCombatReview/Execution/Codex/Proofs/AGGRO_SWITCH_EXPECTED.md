# Aggro switch proof expectations

Status: setup contract for a rerun; the existing R13 log pair does not isolate the dodge-rate trigger.

## Enabled run

- Profile gate: `bAggroEnabled=true`; dodge-rate window `5.0 s`; enter threshold `0.6 dodges/s`; exit threshold `0.3 dodges/s` (`Source/OneBossFight/Player/RPGBossFrameworkProfile.h`, aggro fields; `B_AGGRO/make_aggro_switch_profile.py:16–19`).
- Hold target range in the neutral distance band (strictly above the close exit threshold and below the far exit threshold), with hug/kite inputs false. This prevents range-only selection from masquerading as a dodge-rate switch (`RPGBossAggroRules.h:9–27`).
- At the enter boundary, three observed dodges in five seconds produce `3 / 5 = 0.6`; expected trace is `dodge_observed` for all three followed by `aggro_switch from=0 to=2` (Balanced → Far). Threshold comparison is inclusive on entry (`>=`).
- At the exit boundary, one observed dodge in five seconds produces `1 / 5 = 0.2`, at or below the `0.3` exit threshold; expected trace is `aggro_switch from=2 to=0` (Far → Balanced). Two in five seconds gives `0.4`, above the exit threshold, and must keep Far.
- Required evidence: `player_dodges_scheduled count=3`, three successful `player_dodge_started` events, three corresponding `dodge_observed` events, then the exact band changes in that order, with timestamps/range proving the target stayed in the neutral distance band.

## Negative control

- Use the same map, range hold, schedule, timing, and selector inputs with only `bAggroEnabled=false`.
- Expected: three successful scheduled/observed dodges may appear, but no `aggro_switch` line appears. Ordinary selection remains available; no preferred-band change is attributed to the disabled feature.

## Existing evidence limitation

`B_AGGRO/pie_enabled/editor_raw.log` records `aggro_switch from=0 to=1` at the first decision with `range=153.517`, before the first scheduled dodge (`player_dodge_started` follows later). Since the close-range gate is 250 cm by the profile defaults, this is consistent with range-driven selection and does not prove the 0.6 dodge-rate entry threshold. The same run records only two `dodge_observed` lines although three dodges were scheduled. The control log has no `aggro_switch`, which supports the negative-control expectation for that run. Keep both runs as evidence, but do not label the enabled run a dodge-rate threshold proof. A new run must keep range away from range thresholds and verify all three observed events.

## Setup
## Control
## PASS
## FAIL
