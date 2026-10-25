# Reference Ambiguities, Assumptions and Open Decisions

## Accuracy boundary

The package repeatedly and correctly states that its architecture, Bellwarden design, timings, weights and algorithms are original proposals. They are not verified Elden Ring internals. Any later project audit must compare against the extracted requirements, not assume the illustrative boss or exact values are mandatory.

## Implementation gaps and inconsistencies

| ID | Ambiguity or limitation | Consequence / decision needed | Source |
|---|---|---|---|
| AMB-001 | The C++ samples are explicitly uncompiled and omit the executor, trace, resolver, posture, phase and debug implementations. | Treat them as schemas, not compile-ready proof; validate every UE 5.5.4 API/integration choice. | `code/README.md`, `docs/13_Cpp_Scaffolding.md` |
| AMB-002 | The master utility formula has six positive terms plus repeat/risk penalties; the C++ sketch uses only range/angle/opportunity and deterministic max; the Python sandbox adds more terms and seeded near-best sampling. | Select one production model and document which reference omissions are intentional. | `docs/03_Attack_Selection_Utility_AI.md`, `code/BossAttackDecisionComponent.cpp`, `code/combat_decision_reference.py` |
| AMB-003 | `FBossCombatContext.TargetActor` is a `TObjectPtr`, while the prose recommends weak references for runtime targets. | Choose lifetime semantics appropriate to the real owner and prove target destruction safety. | `code/BossCombatTypes.h`, `docs/13_Cpp_Scaffolding.md` |
| AMB-004 | `BossAttackData.h` lacks many fields recommended by the docs: active windows, resource/action gates, vertical tolerance, detailed hit shapes, cancel policy, armor, pressure and recovery class. | Extend the eventual data model or prove equivalent ownership elsewhere; do not equate this header with full compliance. | `code/BossAttackData.h`, `docs/15_Attack_Catalogue_and_Balance_Sheet.md` |
| AMB-005 | CSV has both signed `MinYawDeg/MaxYawDeg` and absolute `MinAbsYawDeg/MaxAbsYawDeg`; samples use the absolute fields. | Define one canonical angle representation and migration/validation rules. | `data/attack_catalogue.csv`, `code/combat_decision_reference.py` |
| AMB-006 | Python cooldown input treats membership as cooldown-active, whereas C++ compares next-ready world time. | Offline results are not a complete runtime cooldown model. | `code/combat_decision_reference.py`, `code/BossAttackDecisionComponent.cpp` |
| AMB-007 | The C++ angle-fit center can favor the middle of an allowed sector rather than a move-specific preferred angle; the Python script special-cases families. | Add an explicit preferred-angle curve or justify the chosen fit. | `code/BossAttackDecisionComponent.cpp`, `code/combat_decision_reference.py` |
| AMB-008 | Cooldown and reaction time bases under global time dilation are left as a design choice. | Decide game time versus unscaled time per system and test hitstop/slow motion. | `docs/05_Attack_Timing_Telegraphs_and_Pacing.md` |
| AMB-009 | “Player recovery remaining” assumes the boss can observe a reliable public value, but the exact visibility/estimation contract is not defined. | Decide whether this is exact exported state, categorized activity or uncertain estimate so it does not become omniscience. | `docs/02_Player_Model_and_Awareness.md` |
| AMB-010 | Stance-break behavior during hyperarmor is explicitly “delay break or break per rule.” | Author a state-by-hit-class interruption matrix and visible policy. | `docs/10_Defense_Stagger_Poise_And_Interruptions.md` |
| AMB-011 | Guard mitigation, posture transfer, guard break, parryability and grab-versus-guard are principles without concrete per-geometry tables. | Specify per-attack defense policy before implementation/QA. | `docs/07_Hit_Detection_Damage_Geometry.md`, `docs/10_Defense_Stagger_Poise_And_Interruptions.md` |
| AMB-012 | Impact-plus-splash, multi-hit and persistent-zone policies are named, but exact direct/AoE precedence and tick caps are per-attack decisions. | Every relevant attack needs explicit victim-set scope, precedence and maximum hits. | `docs/07_Hit_Detection_Damage_Geometry.md` |
| AMB-013 | Dynamic hold fairness is described, but the source of short/long variant choice and how it is communicated are not fixed. | Author selection timing, probabilities and unmistakable variant cues. | `docs/05_Attack_Timing_Telegraphs_and_Pacing.md` |
| AMB-014 | Pressure-budget costs/regeneration are illustrative; reservation for emergency disengage is suggested without a formal policy. | Choose whether to use a budget at all, then define its interaction with phase, combos and defense. | `docs/05_Attack_Timing_Telegraphs_and_Pacing.md`, `data/combat_settings.json` |
| AMB-015 | Phase transition may be deferred, interruptible or cinematic; deferred is recommended, not required. | Select one policy and specify behavior for active, stagger, grab, death and persistent hazards. | `docs/11_Phases_Reactions_and_Behavior_Adaptation.md` |
| AMB-016 | Old attack callbacks are instance-scoped, but encounter reset/generation invalidation is not fully specified. | Decide how delayed projectiles, timers and persistent actors are invalidated across reset/new encounters. | `docs/01_System_Architecture.md`, `docs/11_Phases_Reactions_and_Behavior_Adaptation.md` |
| AMB-017 | EQS is recommended for positions but query cadence, candidate count and dynamic-obstacle policy are unspecified. | Set performance/commitment bounds from the actual arena and AI budget. | `docs/09_Movement_Spacing_and_Arena.md` |
| AMB-018 | Root-motion collision correction near walls is described as correction/fallback without choosing slide, truncate, abort or alternate animation. | Author per-move wall policy and visual recovery. | `docs/06_Animation_RootMotion_And_Tracking.md`, `docs/09_Movement_Spacing_and_Arena.md` |
| AMB-019 | Motion Warping target refresh is allowed “once or at specifically authorized early gate,” leaving update cadence open. | Define snapshot/update rules per move and prove the commit cutoff. | `docs/06_Animation_RootMotion_And_Tracking.md` |
| AMB-020 | Player prototype timings/iframes, boss/player stats, target fight length and all twelve move numbers are placeholder assumptions. | Re-measure against the actual player kit, animation, boss scale and arena. | `docs/14_Ashen_Bellwarden_Boss_Spec.md`, `data/attack_catalogue.csv` |
| AMB-021 | “30/60/120 FPS parity” defines logical stability but no numeric tolerance for notify/contact timing or movement divergence. | Set acceptable timing, position, damage-count and rotation tolerances. | `docs/16_Debug_Telemetry_and_QA.md` |
| AMB-022 | Performance guidance gives bounded sampling examples but no CPU/GPU/frame-time budget. | Allocate a platform-specific cost budget and profile packaged builds. | `docs/16_Debug_Telemetry_and_QA.md` |
| AMB-023 | Camera, shake, effect and accessibility guidance has no concrete settings schema or acceptance thresholds. | Define camera framing cases and reduced-feedback equivalence criteria. | `docs/18_Polish_VFX_SFX_Camera_Accessibility.md` |
| AMB-024 | Multiplayer is optional and conceptual; montage replication, prediction and lag compensation choices remain unresolved. | If co-op is in scope, create a separate authority/replication specification before implementation. | `docs/19_Multiplayer_And_Replication.md` |
| AMB-025 | Epic documentation links may default to a newer engine branch than 5.5.4. | Verify node/API/plugin behavior in the target engine before relying on the recipe. | `docs/20_References_Glossary_and_Caveats.md` |
| AMB-026 | `decision_rules.csv` says “nav/wrap feasibility,” likely meaning “nav/warp feasibility.” | Treat as a wording defect; confirm intended Motion Warping/path check. | `data/decision_rules.csv` |

## Visual/document presentation issues

- In `diagrams/11_utility_scoring`, the A05 and A08 rejection labels overlap and are difficult to read. The prose/data make the intended “rejected before scoring” behavior clear.
- Titles in the raster/SVG charts for attack timing, tracking/commit, pressure rhythm and utility scoring use very dark text on a dark background, reducing readability. Body labels remain interpretable.
- The arena diagram states it is not to scale; its rings communicate roles, not exact radii.
- The concept sheet is artistic support only. It provides no rig, dimensions, socket, animation or collision evidence.

## Illustrative values that must not silently become requirements

- Bellwarden HP 10,000, posture 100, phase threshold 55%, intended 2-5 minute fight.
- Player startup/dodge assumptions and all A01-A12 damage/timing/range/cooldown values.
- Utility coefficients, near-best gap 0.12, temperature 0.18 and adaptation examples.
- Tracking ranges, context refresh 8 Hz, reaction latency 0.22 seconds.
- Pressure maximum/cost/regeneration examples.
- Six blade samples, 25 cm travel and 12-degree angular substep thresholds.
- A 1500 cm arena radius and all example range bands.
- Combo depths, recovery locks, posture regeneration and critical duration examples.

## Questions for a future implementation phase

1. What exact player states are safely observable, and which are inferred?
2. What distance/angle/Z convention will every attack use?
3. Which high-level planner is authoritative: BT or StateTree?
4. Is an existing GAS/damage pipeline already authoritative, or is a custom resolver required?
5. What is the complete interrupt/priority matrix, especially posture versus hyperarmor and phase transition?
6. What are the per-attack defense and multi-hit policies?
7. How are persistent projectiles/hazards invalidated on reset or phase change?
8. Which attacks use root motion, Motion Warping or movement-component motion, and where does authority hand off?
9. What are the real montage contact, commit and recovery measurements?
10. What punish margins must be supported for each player build?
11. What arena/camera positions are legally reachable, and what wall fallback does each travel move use?
12. What deterministic seed/event schema will allow scenario replay?
13. What timing and frame-time tolerances define 30/60/120 FPS parity?
14. Are multiplayer and accessibility settings in scope for the first release?
15. Which Bellwarden examples, if any, are relevant design inspiration rather than merely explanatory data?

## Inspection limitations

No reference file was inaccessible. The reference C++ was not compiled, the standalone Python tests were not executed, and linked online Epic documentation was not browsed because the requested phase was to study the supplied package. Those facts limit claims about current UE 5.5.4 API validity, not understanding of the package's stated design.
