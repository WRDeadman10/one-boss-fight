# 17 — Production Roadmap, Roles, Milestones, Acceptance Gates

## Milestone 0: combat testbed

**Deliver:** third-person player with attack/dodge/health, empty arena with navmesh, damageable dummy, debug actor. **Exit gate:** player defensive states and hits are reliable at 30/60 FPS.

## Milestone 1: first 3 boss attacks

**Build:** boss Character/Controller, awareness snapshot, attack scoring, three test animations, hit traces, two recoveries, AI debug output. **Exit gate:** chooses poke/sweep/slam appropriately by distance+angle, no teleport tracking, no duplicate hits, guaranteed punish on slam.

## Milestone 2: branching combat

**Build:** attack graph, one conditional follow-up, visible decision gate, anti-repeat, cooldowns, pressure budget. **Exit gate:** player can intentionally bait or avoid a branch; graph has no infinite loops; interrupt cleanup is complete.

## Milestone 3: spacing, reaction and poise

**Build:** arena wall tests, strafe, EQS positioning, heal punish limited reaction, boss posture and stagger. **Exit gate:** all 360° zones reachable; counter reaction gated and readable; stance break doesn't leave active hits.

## Milestone 4: full move catalog

**Build:** all 12 montages, spatial hit geometries, wave AoE, grab, phase-two graph. **Exit gate:** each move satisfies quality criteria, all phase thresholds tested, graphics don't cover essential cues.

## Milestone 5: polish and balancing

**Build:** SFX/VFX, adaptive recovery polish, stable camera, parameter balancing, performance checks, accessibility, QA scenarios. **Exit gate:** novice/veteran playtests support learnability and fair deaths, low-FPS parity.

## Suggested dependency order

```mermaid
flowchart LR
 P[Player combat baseline] --> A[Awareness + target]
 A --> D[Decision utility]
 D --> E[Executor and montage]
 E --> H[Hit trace + damage]
 H --> R[Recovery fairness]
 R --> C[Combo graph]
 C --> M[Movement + EQS]
 M --> S[Phases + specials]
 S --> Q[Polish / QA]
```

## Roles and assets required

- **Gameplay programmer:** state machine, decision utility, damage, collision, posture, instrumentation.
- **Technical animator:** rig/root orientation, sockets, montage structure, warping, contact times and notifies.
- **Combat designer:** move catalogue, telegraphs, risk reward, branch conditions, balance tables.
- **VFX/SFX artist:** anticipation and impact readability, spatial audio and camera cues.
- **Technical QA:** reproducible automation, high/low FPS, camera and geometry edge cases.
- **Environment designer:** valid combat navigation, collision-safe and camera-safe arena.

## Asset checklist per attack

- [ ] `DA_Attack` authored, correct cooldown and range.
- [ ] Montages/skeleton verified; root motion correctly configured.
- [ ] Socket trajectory and damage volume visualized.
- [ ] Timing and rotation-lock notifies placed.
- [ ] Sound and VFX cue distinguish move family.
- [ ] Contact works at 30/60/120 FPS with one hit policy.
- [ ] If branchable, gate and default recovery tested.
- [ ] Recovery is meaningfully punishable according to classification.
- [ ] Interruption/death/phase cleanup works.
- [ ] Balance telemetry capture is readable.

## Integration risks

The riskiest work is **animation-to-hit precision**, **root-motion-vs-AI movement conflicts**, **conditional combo timing**, **camera behavior near a giant boss**, and **unfair heal detection**. Prototype them before modeling the final boss at high fidelity.

## Production sizing

Do not interpret this kit as a one-click process. An effective boss requires bespoke animations, iteration, playable character mechanics, audio, VFX, QA, and authored combat. A three-move greybox is a realistic first output; a polished dozen-move encounter is a substantially larger production effort.
