# C-1274 / Queue BB X21–X25 — Optional channel/drain add-on

**Status:** source implementation and locked Development build/full suite pass. Runtime PIE, card authoring, and Sevarog acceptance remain Lead-owned. The new payload is disabled by default; no card asset or map was saved.

## Data contract and validation

`FRPGBossChannelDrain` is an optional value on `FRPGBossMoveCardSpec` (`Source/OneBossFight/Player/RPGBossMoveCard.h:89-105,154`). It carries Start/End card time, tick interval and damage, heal fraction, cone range/half-angle, and whether facing follows the boss per tick.

When enabled, validation requires a positive tick interval and damage, Start at/after Commit, End after Start and at/before recovery, at least one and at most 64 inclusive ticks, heal fraction in [0,1], cone range in (0,2000] cm, and half-angle in (0,180] (`Source/OneBossFight/Player/RPGBossMoveCard.cpp:77-97`). A defensive card, an empty channel, or a card that also enables the area-effect add-on is refused. A channel can satisfy the card's effect-only requirement without weapon windows. Disabled channels are ignored, preserving existing cards.

`RPGBossChannelDrainRules::TickCount` uses an inclusive endpoint with a small tolerance for float-authored timing so a nominal 0.267–1.267 s channel at 0.25 s spacing keeps its fourth tick. `CappedHeal` limits the request to actual accepted HP damage times HealFraction and current missing boss health (`Source/OneBossFight/Player/RPGBossChannelDrainRules.h`). The boss healing API independently rejects invalid/dead states and caps at MaxHealth.

## Runtime behavior

The executor starts the channel when observed card time crosses StartSeconds. It schedules deterministic card-local ticks at `Start + n * TickInterval` through End. At each tick it evaluates the single explicit duel target against a horizontal cone and range. Facing is sampled on each tick by default; turning it off captures heading at channel start. A tick inside the cone goes through `URPGDamageResolver` with a unique `ChannelTick_n` key under the same attack instance (`Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:471-515`). Misses and resolver refusals consume that tick but do not damage or heal. Heal is based only on `HPApplied` from an accepted tick and cannot exceed missing boss health; the boss-side API independently caps and validates the heal (`Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:757-765`).

The channel has no independent timer: it runs only while the owning card is active. Any executor abort ends it immediately, including stagger, death, watchdog, leash, encounter reset, or EndPlay; no later tick/heal is issued. This currently targets one configured player pawn, not arbitrary actors in the cone. Runtime acceptance should verify facing mode, frame skips, range/cone boundaries, block/parry/i-frame behavior, heal cap, and each interrupt path before Soul Siphon is authored.

## Tests and evidence

Native automation `OneBossFight.Framework.MoveCard.ChannelDrain` in `Source/OneBossFight/Tests/RPGBossMoveCardTests.cpp:94-119` checks legacy disabled behavior, valid effect-only configuration, invalid cadence/timeline/heal/empty effect refusals, capped heal math, zero-damage/full-health no-heal cases, and inclusive tick-count rounding.

`Scripts/Editor/run_c1274_channel_drain_validation.ps1` used both C-1155 locks and the pinned DD27j manifest hash. Result: Development build exit 0; 505 tests started, 505 passed, 0 failed; ChannelDrain automation passed; suite completed; both locks released. Evidence: `Docs/BossCombatReview/Execution/Codex/C1274_CHANNEL_DRAIN/`. No PIE or content saves were performed.

## Sevarog S8 follow-up

This completes the generic source contract, not a Soul Siphon card. C-1242's 0.267–1.267 s pose range is visual-only. Final cadence, damage, healing fraction, cone, facing policy, effect presentation, and intended interrupts remain Lead/owner choices; no values were authored into content.
