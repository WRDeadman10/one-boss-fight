# Queue BB Codex X11–X15 — Sevarog card and framework plans

**Status:** X11 dry-run passed. X12–X15 design plans complete; these do not create or edit game assets. No Sevarog data asset or project map was saved. Card timing remains provisional pending Lead's frame/trace review.

## X11 — S6 `Ultimate_Swing_120fps`

The transient Editor dry-run at `Scripts/Editor/dryrun_sevarog_s6_ultimate.py` copies provisional numeric defaults from the existing F5 HeavySlam candidate, then substitutes S6 identity and the C-1242 visual timeline. Values exercised: Phase 2 candidate, 90–180 cm range, 55 damage, 25 cm window radius, no warp, tell through 0.600 s, active 0.667–0.867 s, recovery end 2.633 s, play rate 1.0. These are validator inputs, not approved gameplay tuning.

`Documentation/Boss/C1242_SEVAROG_CONTACT_MARKING.md:20` marks one visually observed active interval at 0.667–0.867 s. The independent probe table `Docs/BossCombatReview/Execution/Antigravity/MoveCards/PROBE_DERIVED_TIMINGS.md:39` reports two notify-derived intervals, 0.6583–0.7833 and 0.8333–0.9167 s. That disagreement remains open; a single broad window is only a provisional dry-run candidate and must not be treated as verified contact timing.

**Validation:** `Scripts/Editor/run_c1274_s6_locked_dryrun.ps1` completed with `S6_PASS=True`, `NO_PACKAGES_SAVED=1`, and both C-1155 locks released. The transient card passed the production C++ validator. No PIE hit or card selection was claimed. Evidence: `Docs/BossCombatReview/Execution/Codex/C1274_S6_DRYRUN/`.

## X12 — Subjugation area-effect add-on design

Current card windows provide live socket sweeps, a secondary window, or a boss-centered outward ring (`Source/OneBossFight/Player/RPGBossMoveCard.h:45-63`). The executor processes secondary windows after direct windows and a ring is centered on the boss (`Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:289-323`). Neither representation expresses a delayed target-ground cast with a snare.

Proposed optional `AreaEffect` payload for a card, default absent/off:

| Field | Contract |
|---|---|
| `Enabled` | false by default; no behavior change for existing cards |
| `ReleaseSeconds` | one finite card-local time within the clip; Subjugation candidate 0.800–0.867 s from C-1242, not approved |
| `DelaySeconds` | finite non-negative delay after release |
| `RadiusCm`, `Damage` | finite positive radius and finite non-negative damage, validated against explicit project limits |
| `SnareSeconds`, `SnareScale` | optional bounded movement slow; zero duration means no snare |
| `Targeting` | snapshot target ground location at release; do not follow target during delay |
| `HitIdentity` | one effect instance per card instance; one damage application per target for that instance |
| `CancelPolicy` | card abort/death/reset cancels pending effect and clears any owned snare immediately |

The effect should spawn at the stored ground point when `ReleaseSeconds + DelaySeconds` is reached, query eligible targets once, resolve damage through the existing resolver, and retain a per-target hit set for this effect instance. It should not be implemented as `bRing`: the existing ring expands around the boss, while Subjugation requires a fixed ground location. Overlap with direct windows must define priority explicitly; the default design is a separate effect identity, with no accidental shared-HitGroup suppression. Lead/owner chooses final values and visual/audio presentation.

## X13 — Soul Siphon channel/drain add-on design

The source card data currently describes one HP damage value and a list of windows; executor hit payloads use the window's HitGroup (`RPGBossMoveCard.h:73-120`, `RPGFrameworkMoveExecutor.cpp:293-305`). Reusing one HitGroup for repeated ticks would collide with same-attack hit deduplication, while changing HitGroup per tick would conflate effect scheduling with weapon windows.

Proposed optional `ChannelDrain` payload, default absent/off:

- `StartSeconds`, `EndSeconds`, `TickIntervalSeconds`, `TickDamage`, and `BossHealPerTick`; validate finite ranges, positive interval, end after start, and bounded non-negative damage/heal.
- `ConeRangeCm`, `ConeHalfAngleDegrees`, and target height policy; snapshot boss facing per tick or explicitly lock facing at channel start (default recommendation: facing is sampled each tick).
- Each tick performs one cone eligibility query and resolves at most one damage event per target for that tick. Tick identity is `(card instance, tick index, target)`; it is separate from blade `HitGroup` identities.
- Heal the boss only from actual HP damage accepted by the resolver, capped at `BossMaxHealth`; blocked, parried, invulnerable, missed, or zero-damage ticks do not heal.
- Any accepted interrupt (stance break, death, encounter reset, explicit cancel) stops future ticks, restores any channel-owned movement state, and cannot heal after cancellation. A tick already executing completes atomically before cancellation takes effect.
- Emit start/tick/end/cancel reason diagnostics; never repurpose `RPGBossBleed` for the siphon.

C-1242 marks the pose channel as 0.267–1.267 s but explicitly says no weapon contact. Those marks are animation observations, not approved gameplay tick cadence or cone size. Lead/owner values and interrupt source remain decisions.

## X14 — phase-pool plan using the current selector

The existing selector does support per-phase filtering: it evaluates each candidate through `FRPGBossMoveModel::IsEligible`, and that model refuses a card whose `PhaseId` differs from the decision snapshot (`RPGBossMoveSelector.cpp:38-56`, `RPGBossMoveModel.cpp:32`). The boss snapshots `CurrentPhaseId` for each decision (`RPGFrameworkBossCharacter.cpp:539-542`), and the profile resolver verifies candidates belong to phase one or `PhaseTwoId`, both pools are nonempty, and each pool cannot starve the configured `AttackCount` (`RPGBossFrameworkProfile.cpp:218-226`).

Data-only proposal, pending card/phase approval:

| Pool | Proposed membership |
|---|---|
| Phase 1 | Existing S1–S5 baseline cards (`Swing1_Medium`, `Swing2_Medium`, `Swing3_Slow`, `Speedburst`, `Swing1_FAST_v2`) |
| Phase 2 | The S6–S8 signature cards plus phase-2-specific core-card variants as needed to meet the same pool coverage requirement |

Every card has exactly one phase. If the proposed Phase 2 signature set is fewer cards than `AttackCount` and all have positive cooldowns, the profile resolver will reject it as starvation; include enough distinct Phase 2 core variants or an explicitly approved zero-cooldown card. Keep the first card's Phase 1 ID stable, set the profile's `PhaseTwoId` to the chosen Phase 2 ID, and retain the selector's existing health-threshold transition. This is a design plan only; it does not assert that S6–S8 assets exist or that a phase threshold/value has been approved.

## X15 — Sevarog stun clips on the stagger profile driver

The existing profile fields are `StaggerStartAnim`, `StaggerLoopAnim`, `StaggerEndAnim`, and shared `AnimSlotName` (`Source/OneBossFight/Player/RPGBossFrameworkProfile.h:138-140`). The resolver requires all three clips together, a non-empty slot, posture support, valid loads, skeleton agreement, positive clip durations, and a stagger duration that can contain start plus end (`RPGBossFrameworkProfile.cpp:74-83,276-298`). `StartStagger` plays Start once (`RPGFrameworkBossCharacter.cpp:833-840`); `TickStaggerAnim` fills the middle with Loop and starts End so the sequence fits `StaggerSeconds` (`RPGFrameworkBossCharacter.cpp:957-977`).

Mapping: Sevarog's `Stun_Start` → `StaggerStartAnim`; `Stun_Loop` → `StaggerLoopAnim`; `Stun_End` → `StaggerEndAnim`. Bind them on the Sevarog framework profile, preserving its current shared `AnimSlotName` only after confirming the Sevarog AnimBP contains that slot. Before authoring the profile, Lead must confirm the three sequence paths resolve, their skeleton is the boss mesh skeleton, the slot routes through the active montage/sequence playback graph, and `StaggerSeconds >= StartLength + EndLength`. Loop count is computed by the existing driver; avoid custom timing fields unless the Lead run shows a mismatch. No clip paths or durations are claimed as disk-verified by this plan.

## Batch disposition

- X11: dry-run PASS; visual/probe timing reconciliation and live acceptance remain Lead-owned.
- X12–X15: plans delivered; no production code or assets changed.
- No game content, map, or pack asset was modified. No further engine run was needed for these plans.
