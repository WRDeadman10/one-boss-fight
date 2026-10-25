# 09 — Movement, Strafing, Distance Management, Arena Awareness

![Arena](../diagrams/09_arena_and_spacing.png)

## Distinguish navigation from combat locomotion

Long-range travel can use NavMesh and `AI MoveTo`. Combat strafe, orbit, small pivots, retreats and commitment movement need tighter animation-aware control. Do not issue new `MoveTo` constantly while root motion attacks play.

### Desired range bands (original Bellwarden values)

- `0–160 cm` — danger close; poke, backhook, retreat. Avoid all attacks being long telegraphs.
- `160–380 cm` — ideal halberd range; sweep/overhead/feint.
- `380–700 cm` — approach, lunge or guarded advance.
- `700–1100 cm` — sprint/gap closer or projectile in phase 2.
- `>1100 cm` — reacquire/approach; avoid endless boss ranged spam.

## Movement decisions

| Position | Possible action | Why |
|---|---|---|
| Too far / LOS good | Chase / sprint | Re-enter gameplay range |
| Too close, straight ahead | Retreat step or short thrust | Recover weapon leverage |
| Close side | Pivot / side sweep | Manage vulnerable flank |
| Close rear | Rear hook / step-out | Counter permanent rear camping |
| Ideal range | Strafe clockwise/counterclockwise | Probe player space, vary approach |
| Near wall | Reverse strafe, move inward | Avoid clipping into arena edge |
| Player pinned at wall | Approach with safeguards | Avoid unfair inescapable contact |
| Player elevated | Reposition to valid terrain | No melee damage through floor |

## Choosing positions with EQS

Generate candidate points on a ring around the player or boss. Score by navigation reachability, desired distance, visibility, arena wall clearance, hazard avoidance, approach vector, player facing, and recent movement history. Reject unreachable points. Move to the highest candidate using a short action commitment; don't re-query each animation frame.

Proposed scoring: `0.30*DistanceScore + 0.25*NavReachable + 0.15*Sight + 0.15*WallClearance + 0.10*PreferredFlank + 0.05*Variety`. This is a tuneable start, not an Epic default.

## Feet and root motion

- Maintain foot placement and floor projection during pivots; snap-to-ground must not create visible skating.
- Attack Montages with root motion should handle translation; stop AI requested velocity before play.
- Long moves that hit arena wall need collision-aware correction and authored fallback animation.
- Stop boss movement if the player enters invalid arena/death state; reset encounter after rule-defined leash time.

## Arena shape impacts attack balance

Measure effective diameter, obstacles, edges, stairs, line-of-sight occluders, and safe recovery zones. A radial shockwave requiring movement out of a 500cm radius is unfair in a 700cm-wide arena if its wind-up is too short. Validate any place the player can stand, jump, climb or clip, and how camera behaves at the edge.

## Telemetry

Log `playerDistance`, `bossWallDistance`, `idealRangeError`, `EQSScore`, `movementMode`, `rootMotionActive`, `wallCollisionDuringAttack`, and how long boss took to reacquire after whiff. A high percentage of wall hits usually means poor arena movement selection, not necessarily a bad attack animation.
