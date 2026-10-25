# 20 — References, Terminology and Accuracy Boundaries

## Official Unreal Engine documentation

These are links to Epic Developer Community documentation. They may currently default to a newer UE documentation branch; this kit targets **UE 5.5/5.5.4** and individual node/plugin availability should be verified in that editor before implementation.

- [Behavior Tree quick start](https://dev.epicgames.com/documentation/en-us/unreal-engine/behavior-tree-in-unreal-engine---quick-start-guide)
- [Environment Query System quick start](https://dev.epicgames.com/documentation/en-us/unreal-engine/environment-query-system-quick-start-in-unreal-engine)
- [AI Perception](https://dev.epicgames.com/documentation/en-us/unreal-engine/ai-perception-in-unreal-engine)
- [StateTree overview](https://dev.epicgames.com/documentation/en-us/unreal-engine/overview-of-state-tree-in-unreal-engine)
- [Animation Montages](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-montage-in-unreal-engine)
- [Animation Notifies / Notify States](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-notifies-in-unreal-engine)
- [Root Motion](https://dev.epicgames.com/documentation/en-us/unreal-engine/root-motion-in-unreal-engine)
- [Motion Warping](https://dev.epicgames.com/documentation/en-us/unreal-engine/motion-warping-in-unreal-engine)
- [Gameplay Ability System overview](https://dev.epicgames.com/documentation/en-us/unreal-engine/understanding-the-unreal-engine-gameplay-ability-system)
- [Animation debugging and optimization](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-debugging-and-optimization-in-unreal-engine)
- [Rewind Debugger](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-rewind-debugger-in-unreal-engine)
- [Animation Insights](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-insights-in-unreal-engine)
- [Networking and replication](https://dev.epicgames.com/documentation/en-us/unreal-engine/networking-and-multiplayer-in-unreal-engine)

## Critical accuracy distinction

We can *observe* attack timing, enemy reaction, combo branches and facing behaviors in published games. We cannot establish exact private proprietary decision algorithms, source code, exact frame tables or internal thresholds without authoritative disclosures. All formulae, exact seconds, score weights, Bellwarden moves and unreal programming architecture in this kit are **design recommendations / examples**, not claims about Elden Ring internals.

## Terminology

| Term | Meaning |
|---|---|
| BT | Behavior Tree (high-level modes/actions) |
| Blackboard | Key-value world/AI state shared with BT |
| StateTree | Alternative hierarchical state selection system |
| EQS | Samples and scores possible world positions |
| Utility AI | Compares desirability of eligible actions |
| LOS | Line of sight |
| Montage | Sequence/section-based animation control asset |
| Notify | Event at a specific animation point |
| Notify State | Duration event with Begin/Tick/End |
| Root Motion | Character displacement extracted from animation root bone |
| Motion Warping | Bounded root-motion adjustment during warp window |
| Hitbox | Collision volume capable of detecting an attack contact |
| Hurtbox | Target collision volume used by combat damage |
| i-frames | Window in which specified attacks cannot damage actor |
| Wind-up | Anticipation before active damage |
| Active frames | Time when an attack can make damaging contact |
| Recovery | Commitment after attack's danger ends |
| Hit confirm | Verified contact/collision result |
| Whiff | Missed attack |
| Poise/posture | Accumulated break metric, typically independent of health |
| Hyperarmor | Interrupt resistance in specific state/window |
| Commit | No longer permitted to retarget freely |
| Pressure budget | Optional balancing resource preventing endless offense |
| Seed | Stored RNG value for reproducible decisions |

## Recommended build philosophy

**Observe → prototype → profile → tune.** Avoid reverse-engineering claims, copyrighted asset extraction and attempting to reproduce a specific game's boss identically. The original Ashen Bellwarden exists to illustrate how to make a combat experience with comparable *design depth*, not to copy an existing commercial character.
