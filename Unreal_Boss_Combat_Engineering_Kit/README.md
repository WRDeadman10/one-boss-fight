# UNREAL BOSS COMBAT ENGINEERING KIT
## Build an original, Soulslike, player-responsive boss in Unreal Engine 5.5 / 5.5.4

![Original boss concept](concept_art/Ashen_Bellwarden_Concept_Sheet.png)

**Audience:** Unreal Engine gameplay programmers, technical animators, combat designers, AI designers, technical artists.  
**Target:** UE 5.5/5.5.4; third-person, single-player, 60 FPS baseline.  
**Case study:** **Ashen Bellwarden**, an original halberd-wielding dark-fantasy boss.  
**Status:** detailed implementation design, diagrams, data templates, and reference code sketches — **not** a compiled Unreal project or a licensed Elden Ring asset pack.

This is a **combat systems** guide, not a lore or environment design book. Its focus is how a boss *chooses*, *commits to*, *performs*, *branches*, *connects*, and *recovers from* attacks in response to the player.

## The essential thesis

A responsive boss is a tightly coordinated system:

`Observe → Understand → Select → Commit → Animate → Hit-Test → Recover → Learn from encounter context → Repeat`

The crucial distinction is that player-responsive selection occurs at **legal decision gates**. A committed swing should not magically snap to the player's new location unless the move explicitly permits tracking.

![Architecture](diagrams/01_system_architecture.png)

## Start here

1. Read `docs/00_Design_Goals_and_Definitions.md` and `docs/01_System_Architecture.md`.
2. Read `docs/02_Player_Model_and_Awareness.md`, `docs/03_Attack_Selection_Utility_AI.md`, `docs/04_Combo_Branching_and_Decision_Tree.md`.
3. Use `docs/12_Unreal_55_Blueprint_Implementation.md` for a functional vertical slice, then `docs/13_Cpp_Scaffolding.md` for a scalable code path.
4. Implement the **three attacks** in `docs/14_Ashen_Bellwarden_Boss_Spec.md`'s first milestone before attempting all 12.
5. Tune timing and punish rules against `data/attack_catalogue.csv`, then run `tests/qa_scenarios.csv`.
6. Inspect diagrams before authoring animation: all attack windows must be designed before collision and VFX are wired.

## Documentation map

| File | Purpose |
|---|---|
| `00_Design_Goals_and_Definitions.md` | Fairness rules, vocabulary, acceptance definition |
| `01_System_Architecture.md` | Runtime ownership, events, data, update cadence |
| `02_Player_Model_and_Awareness.md` | Sensing, snapshots, state, distance/angle, reactions |
| `03_Attack_Selection_Utility_AI.md` | Gates, scoring, cooldowns, repetition, pseudocode |
| `04_Combo_Branching_and_Decision_Tree.md` | Attack graph, windows, sections, conditional branches |
| `05_Attack_Timing_Telegraphs_and_Pacing.md` | Timeline, anticipation, delay, recovery, pressure |
| `06_Animation_RootMotion_And_Tracking.md` | Montages, sockets, Motion Warping, root motion, lock-on |
| `07_Hit_Detection_Damage_Geometry.md` | Swept traces, thrust/sweep/AoE/beam/grab, damage |
| `08_Punish_Windows_and_Fairness.md` | Meaningful openings, commitment, exploit vs skill |
| `09_Movement_Spacing_and_Arena.md` | Position choices, strafing, EQS, arena constraints |
| `10_Defense_Stagger_Poise_And_Interruptions.md` | Hit reaction, posture, hyperarmor, parries, grabs |
| `11_Phases_Reactions_and_Behavior_Adaptation.md` | Phase graphs, heal reaction, anti-spam/anti-cheese |
| `12_Unreal_55_Blueprint_Implementation.md` | Click-by-click editor asset and event graph recipe |
| `13_Cpp_Scaffolding.md` | Data model, component contracts, pseudocode and files |
| `14_Ashen_Bellwarden_Boss_Spec.md` | Fully designed original case-study boss |
| `15_Attack_Catalogue_and_Balance_Sheet.md` | Twelve attack specifications and timing calculations |
| `16_Debug_Telemetry_and_QA.md` | Visualization, logging, determinism, performance |
| `17_Production_Roadmap_and_Deliverables.md` | Milestones, workload, dependencies, definition of done |
| `18_Polish_VFX_SFX_Camera_Accessibility.md` | Communication, effects, sound, camera, readability |
| `19_Multiplayer_And_Replication.md` | Authority and determinism boundaries if networking |
| `20_References_Glossary_and_Caveats.md` | Epic docs, terms, verified vs proposed behavior |
| `21_Animation_Authoring_and_Asset_Pipeline.md` | Animation asset checklist, import, retarget, notifies |
| `22_Failure_Modes_and_Anti_Patterns.md` | Problem/symptom/cause/fix playbook |

## Visual library

![Decision tree](diagrams/02_decision_tree.png)
![Attack graph](diagrams/03_attack_graph.png)
![Timing](diagrams/05_attack_timing.png)
![Hit geometry](diagrams/06_hit_geometry.png)

`diagrams/` contains both PNG and, where appropriate, editable SVG. Diagrams are original explanatory designs. The concept sheet is original generated concept art, not Elden Ring artwork.

## Structured files

- `data/attack_catalogue.csv` — designer tuning sheet for **12 hypothetical attacks**. All values illustrative in **seconds / centimeters / degrees**.
- `data/combat_settings.json` — proposed designer defaults.
- `data/decision_rules.csv` — eligibility and score examples.
- `tests/qa_scenarios.csv` — test matrix including attack openings, tracking, collision, and exploit cases.
- `code/` — illustrative C++ / engine setup contracts. **Not validated against a locally installed Unreal toolchain**; integrate and compile in your actual UE 5.5 project.

## Design boundaries and credits

- **This is not a claim about FromSoftware's private source code.** Elden Ring behaviors discussed are observational examples; attack-selection algorithms and tables here are deliberately proposed implementations.
- **Not affiliated with FromSoftware, Bandai Namco, or Epic Games.** No game assets, source, or ripped animation data are included.
- Official Unreal documentation links are in `docs/20_References_Glossary_and_Caveats.md`. Some Epic docs are now served under newer versions; validate exact features/nodes in **UE 5.5.4**.
- Abbreviations: BT = Behavior Tree, BB = Blackboard, EQS = Environment Query System, GAS = Gameplay Ability System, AoE = Area of Effect, ANS = Anim Notify State, ASC = Ability System Component.

## Practical recommendation

Implement **BT + Blackboard (high-level activity) + independent attack utility evaluator + Montage/Notify-driven attack executor** first. Only adopt GAS if you already use it or need a substantial effects/ability framework. Consider StateTree as a valid alternative to BT, **not** a second competing combat brain.
