# 10 — Damage Reactions, Stance/Poise, Hyperarmor, Parries, Guard, Grabs

## Distinguish health, stagger and posture

- **Health:** determines death/phase thresholds.
- **Hit reaction:** immediate response depending on attack damage class, animation window, armor and current state.
- **Posture:** hidden or exposed break meter that accumulates posture damage, may recover after quiet time, and triggers a special break state.
- **Hyperarmor:** temporary interruption resistance for certain committed moves; health and posture may still be affected depending on policy.
- **Super armor:** sometimes used more broadly; define terminology in team and be consistent.

## Sample posture design

`MaxPosture = 100`, regular slash = 12, heavy = 28, charged = 38; regeneration starts after `4s` without posture damage at `8 units/s`. On reaching 100, enter `StanceBroken`, disable active attack windows, play a specific break montage, expose critical hit for e.g. `2.2s`, then reset posture to a chosen value. Numbers are illustrative and need build-specific balance.

## Interruption matrix (design example)

| Boss state | Light hit | Heavy hit | Parry | Posture threshold | Death |
|---|---|---|---|---|---|
| Neutral | Small flinch maybe | Strong stagger | N/A | Stance break | Always |
| Wind-up normal | Flinch/cancel eligible | Interrupt | Some moves | Break | Always |
| Heavy hyperarmor active | Damage, no flinch | Damage, maybe no flinch | Only tagged parry | Delay break or break per rule | Always |
| Active committed | Usually no flinch if armor | Depends on move | Very specific windows | Usually break if armor absent | Always |
| Recovery | Flinch if allowed | Stagger | N/A | Break | Always |
| Stance-broken | No repeated endless flinches | Critical if eligible | N/A | Already broken | Always |

A different matrix is valid, but it **must be consistent**.

## Guard, block, parry and dodge

- Define shield-facing cone and stamina cost; guard penetration may be partial.
- Perfect parry windows are short, clearly tagged on attacks and should trigger a dedicated response.
- Dodge i-frames use explicit timer/montage tags from the player; avoid simply checking movement speed.
- AoE, grabs and normal blade strikes can each have separate guard/parry/dodge response.
- If boss can dodge, grant reaction startup and recovery; never let it perfectly evade every player hit.

## Interrupt safety

`AbortAttack` must close trace, clear scheduled AoEs if linked to boss commitment (unless persistently spawned by design), end warping, stop/transition Montage, restore movement modes, clear stale combo gates and unlock decision after suitable hit reaction. Preserve provenance in telemetry: InterruptedByStance, Parry, Death, Phase, TargetLoss, MontageError, ArenaReset.

## Grab mechanics

Synchronized grabs are technically difficult: capture, valid directional contact, authority, warp align both actors, temporary input restrictions, damage moment, throw trajectory, release to valid nav/collision position, interrupted/death recovery. Never disable input permanently if the paired montage gets interrupted.
