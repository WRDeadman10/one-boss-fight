# 08 — Punish Windows, Attack Commitment, Player Agency

## What a punish window really is

It is not just the boss montage's recovery duration. The **usable** player punish window varies by player travel and attack startup:

```text
UsablePunish = GuaranteedBossLockRemaining
             - PlayerTravelTime
             - PlayerAttackStartup
             - SafetyBuffer
```

Example after a slam: 0.95s recovery, 0.18s travel, 0.34s light startup, 0.12s safety buffer ⇒ **0.31s remaining**. A heavier move with 0.72s startup yields **-0.07s** and is not reliably punishable from that same position. This encourages position selection instead of memorizing timing alone.

## Four opening types

1. **Guaranteed:** boss is in unrecoverable follow-through long enough for a defined player response (usually after heavy committed move).
2. **Conditional:** an apparent recovery can turn into a follow-up when player remains in a defined zone; a patient player confirms the branch first.
3. **Spacing-created:** move whiffs due to good positioning, allowing an attack even if the nominal recovery is short.
4. **Resource-created:** boss is posture-broken, guard broken or has spent a pressure budget and temporarily cannot retaliate.

**Avoid false punish windows** where the boss appears grounded and vulnerable but can instantly turn/attack without any animation cue. If a counter exists, communicate it consistently.

## Risk/reward targets

| Player choice | Desired boss design property |
|---|---|
| Roll toward flank | Outmaneuver a committed thrust, gain position |
| Roll backward | Avoid short range strike but risk catch-up gap closer |
| Guard | Survive specific sweeps but spend stamina / posture |
| Jump | Counter carefully tagged low ground waves, not arbitrary melee |
| Heavy attack | Only safe during specific long openings or after stance break |
| Heal | Safe when spacing, obstacle, or long boss recovery permits |

A player should have **multiple** valid responses to many attacks, not one invisible magic answer. Difficulty can come from recognizing the best of several choices.

## Recovery design policies

- Fixed early recovery starts when active hit ends, not when weapon visually comes to rest unless animation supports it.
- Keep `RecoveryMinimumLock` separate from cinematic animation length; boss cannot transition before that minimum.
- If phase changes recovery lengths, communicate altered rhythm.
- Combo gates must occur at an understandable interval so players can identify an actual finisher.
- Add a long guaranteed opening to at least some high-commitment high-damage moves.
- Don't make every dodge punishable; that negates core player defense mechanics.

## Tracking limits make punishes possible

Facing lock at 0.65s permits player to step behind before active strike. Without tracking lock, a large overhead swing that rotates with the player can hit anywhere and generate no spatial solution. Conversely, a truly radial shockwave should provide a temporal, vertical or distance-based solution rather than positional blind spot.

## Evaluation metrics

- Successful punishes per boss attack by attack type and player skill band.
- Posture/HP damage earned during recovery vs traded hits.
- Average `seconds_between_valid_player_offense_opportunities`.
- Rate of player deaths within 0.3s after attacking an apparent opening.
- Time player spends in neutral retreat without a reachable opening.
- Win rates by player build; avoid making slow weapons disproportionately invalid.

## Fairness tests

- Can a player bait a targeted thrust to create a side punish? **Yes**, reliably with learned spacing.
- Does a backward dodge into lunge range produce an understandable chase punish? **Yes**, if telegraphed.
- Can the boss rotate unlimited degrees after active starts? **No**, unless attack is explicitly an AoE spin and visually supports it.
- Can every big attack cancel into an instant fast counter? **No**. Reserve meaningful guaranteed openings.
- Does staying far away cause endless unpunishable projectiles? **No**. Add cooldowns, approach windows and positional solutions.
