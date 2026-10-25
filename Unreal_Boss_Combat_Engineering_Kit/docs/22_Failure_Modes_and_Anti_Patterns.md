# 22 — Anti-patterns, Symptoms, Root Causes and Corrections

| Symptom | Likely underlying problem | Corrective action |
|---|---|---|
| Boss seems to read every roll | Reaction selected after player input, zero delay | React only to visible committed state and at legal gates; add cooldown/latency |
| Boss rotates 180° during heavy swing | Target-facing Tick fights root motion | Freeze/limit turn after attack commit and disable competing orientation |
| Player hit outside visible blade | Broad overlap collider or lagging socket | Use swept multi-sample trace; visualize and tune geometry |
| Blade passes through player without hit | Low FPS/tunneling, trace only at socket endpoints | Sweep between frames with blade interior samples and adaptive substeps |
| Two damage events per swing | Multiple mesh body overlaps | Per-instance victim dedupe and resolver ownership |
| Boss stuck attacking after stagger | Montage interrupted before end notify | Central cleanup on interrupt/OnMontageEnded + watchdog |
| Boss attacks forever | Unlimited branch graph, no pressure budget | Max combo depth, recovery guarantees, cooldown, aggression budget |
| Boss stands doing nothing at distance | All attacks invalid and no fallback | Reposition, approach, or controlled neutral wait when no candidates |
| Weak builds can't punish | Recovery tested only with fast weapon | Compute punish margins for multiple player startups and distances |
| Boss swings through wall repeatedly | EQS/warp not checked against arena | Predict path, cap warp, collision-safe fallback |
| Healing always punished across arena | Context uses raw input/ignores LOS or reach | Require visible heal state, travel/reaction budget and cooldown |
| Attack suddenly becomes different hit shape | Mid-animation branch without tell | Only branch at explicit authored gates with visible transition |
| Radial AoE damages while wave has passed | Whole disk collision instead of annulus | Test swept annulus and per-victim hit once |
| Missed grabbed player remains frozen | Capture montage interrupted and control not restored | Paired grab state cleanup and release/fallback position |
| Root motion and NavMesh fight | `MoveTo` continues during attack montage | Switch movement authority at attack start/end |
| Phase 2 interrupts every attack strangely | Immediate HP event overrides active state | Queue transition and apply after safe neutral gate |
| CPU spikes during weapon use | Huge traces every tick / expensive object queries | Trace only while active, cap samples, profile packaged build |
| Montage notify fires twice | Blends / duplicate Montage tracks / old attack instance | Validate instance + event state; log all notify calls |
| Hit FX but zero damage unexplained | Cosmetic traces differ from authoritative resolver | Centralize contact trace and explicitly log defense outcome |
| Attack data unused | Hardcoded Blueprint constants override assets | Centralize tuning values, inspect in debug overlay |

## Diagnostic loop

1. Reproduce with fixed player location and RNG seed.
2. Inspect boss state, selected move and last rejection trace.
3. Scrub Rewind Debugger around animation commitment.
4. Overlay collision against animation sockets.
5. Check active window, hit policy, target i-frames and damage resolver outcome.
6. Verify phase/branch/cooldown and movement authority.
7. Fix one root cause; rerun regression test matrix.

## Principle

Never 'fix' a fundamentally unfair attack by merely adding more VFX or raising boss HP. First correct the event, geometry or decision timing that causes the unfairness.
