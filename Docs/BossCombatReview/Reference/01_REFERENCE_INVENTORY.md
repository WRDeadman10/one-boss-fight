# Boss Combat Reference Inventory

## Scope and method

- Reference root: `Unreal_Boss_Combat_Engineering_Kit/`.
- The supplied reference was already expanded. No matching ZIP was present at the project root or one directory below it, so nothing was extracted or overwritten.
- Total files: **60**.
- Fully inspected: **60**. Inaccessible or unreadable: **0**.
- Text files were read completely. `README.md` was read first, followed by `MASTER_GUIDE.md` sequentially from line 1 through line 1864. The 23 chapter files were then cross-checked; 20 are verbatim copies of master-guide sections apart from relative image paths, while chapters 13, 15, and 16 were separately read in full because their relative paths differ.
- Every PNG was visually inspected. Every SVG parsed successfully; its source structure and labels were cross-checked against the corresponding PNG. The concept sheet was visually inspected.
- The package's code is reference scaffolding only. It was read, but not compiled or integrated. The package's tests were read, but not run, because this phase is analysis-only.

Status legend: **Full-text** = read completely; **Visual+source** = raster visually inspected and SVG source parsed/cross-checked; **Visual** = raster visually inspected.

## Root documents

| File | Status | Notes |
|---|---|---|
| `README.md` | Full-text | Scope, reading order, file map, disclaimers and practical architecture recommendation. |
| `MASTER_GUIDE.md` | Full-text | Complete 23-chapter integrated guide, read sequentially without skipped sections. |

## Chapter documents

| File | Status | Primary subject |
|---|---|---|
| `docs/00_Design_Goals_and_Definitions.md` | Full-text | Fairness contract, terminology, invariants. |
| `docs/01_System_Architecture.md` | Full-text | Runtime ownership, data flow, failure recovery. |
| `docs/02_Player_Model_and_Awareness.md` | Full-text | Observable context, perception, memory, reactions. |
| `docs/03_Attack_Selection_Utility_AI.md` | Full-text | Hard gates, utility scoring, variety and traceability. |
| `docs/04_Combo_Branching_and_Decision_Tree.md` | Full-text | Conditional graph, legal gates, branch policy. |
| `docs/05_Attack_Timing_Telegraphs_and_Pacing.md` | Full-text | Timelines, holds, pressure and rhythm. |
| `docs/06_Animation_RootMotion_And_Tracking.md` | Full-text | Montages, motion ownership, warping and rotation limits. |
| `docs/07_Hit_Detection_Damage_Geometry.md` | Full-text | Geometry families, swept traces, defense resolution. |
| `docs/08_Punish_Windows_and_Fairness.md` | Full-text | Openings, commitment, build-sensitive punish math. |
| `docs/09_Movement_Spacing_and_Arena.md` | Full-text | Range bands, EQS, walls, arena constraints. |
| `docs/10_Defense_Stagger_Poise_And_Interruptions.md` | Full-text | Health, posture, armor, guard, parry and grab. |
| `docs/11_Phases_Reactions_and_Behavior_Adaptation.md` | Full-text | Phase policy, heal reactions and anti-cheese. |
| `docs/12_Unreal_55_Blueprint_Implementation.md` | Full-text | Blueprint-first vertical-slice recipe. |
| `docs/13_Cpp_Scaffolding.md` | Full-text | Suggested source layout and component contracts. |
| `docs/14_Ashen_Bellwarden_Boss_Spec.md` | Full-text | Illustrative 12-move case-study boss. |
| `docs/15_Attack_Catalogue_and_Balance_Sheet.md` | Full-text | Data fields, timing formulas and tuning order. |
| `docs/16_Debug_Telemetry_and_QA.md` | Full-text | Debug views, event schema, analytics and profiling. |
| `docs/17_Production_Roadmap_and_Deliverables.md` | Full-text | Milestones, dependencies, roles and exit gates. |
| `docs/18_Polish_VFX_SFX_Camera_Accessibility.md` | Full-text | Readability, camera, audio, VFX and accessibility. |
| `docs/19_Multiplayer_And_Replication.md` | Full-text | Optional authority, replication and latency concerns. |
| `docs/20_References_Glossary_and_Caveats.md` | Full-text | Official links, terms and accuracy boundaries. |
| `docs/21_Animation_Authoring_and_Asset_Pipeline.md` | Full-text | MoveCard handoff, markers, sockets and retargeting. |
| `docs/22_Failure_Modes_and_Anti_Patterns.md` | Full-text | Symptom/cause/correction playbook. |

## Reference code and contracts

| File | Status | Notes |
|---|---|---|
| `code/README.md` | Full-text | Integration limits; sample cannot run a boss by itself. |
| `code/Animation_Notify_Contract.md` | Full-text | Commit, hit window, combo, tracking, recovery and armor notify contracts. |
| `code/BossCombatTypes.h` | Full-text | Example state, geometry, hit-policy, context, damage and decision types. |
| `code/BossAttackData.h` | Full-text | Example attack and combo-edge data schema. |
| `code/BossAttackDecisionComponent.h` | Full-text | Example selector interface and cooldown map. |
| `code/BossAttackDecisionComponent.cpp` | Full-text | Deterministic V0 eligibility and best-score selector. |
| `code/combat_decision_reference.py` | Full-text | Seeded near-best offline decision sandbox. |

## Structured data and tests

| File | Status | Notes |
|---|---|---|
| `data/attack_catalogue.csv` | Full-text | Twelve illustrative attacks A01-A12 and their initial tuning. |
| `data/combat_settings.json` | Full-text | Illustrative phase, awareness, utility, executor, trace, posture and pressure defaults. |
| `data/decision_rules.csv` | Full-text | Example neutral and combo-gate rules. |
| `tests/qa_scenarios.csv` | Full-text | Twenty-two reference QA scenarios. |
| `tests/test_decision_reference.py` | Full-text | Five unit tests for the offline decision sandbox. |

## Diagrams

Each PNG/SVG pair was treated as one visual design plus an editable-source representation. Both files were inspected.

| Files | Status | Interpretation focus |
|---|---|---|
| `diagrams/01_system_architecture.png`, `diagrams/01_system_architecture.svg` | Visual+source | Player observation through awareness, high-level AI, utility, executor, montage, trace, resolver, combo feedback and telemetry. |
| `diagrams/02_decision_tree.png`, `diagrams/02_decision_tree.svg` | Visual+source | Legal-gate start, validity/executor/phase checks, hard filtering, fallback, scoring and seeded selection. |
| `diagrams/03_attack_graph.png`, `diagrams/03_attack_graph.svg` | Visual+source | A02 gate branching to A07, A05, normal recovery or long recovery, then neutral. |
| `diagrams/04_combat_state_machine.png`, `diagrams/04_combat_state_machine.svg` | Visual+source | Neutral/position/wind-up/commit/active/recovery/stagger/phase/death transitions and priority implications. |
| `diagrams/05_attack_timing.png`, `diagrams/05_attack_timing.svg` | Visual+source | A03 anticipation 0-0.70, hold 0.70-0.98, active 0.98-1.17 and recovery 1.17-2.15; tracking begins to lock before contact. |
| `diagrams/06_hit_geometry.png`, `diagrams/06_hit_geometry.svg` | Visual+source | Distinct top-down thrust, sweep, slam, annulus, lane and grab volumes. |
| `diagrams/07_tracking_and_commit.png`, `diagrams/07_tracking_and_commit.svg` | Visual+source | High early tracking, reduced late tracking, zero commit/recovery tracking, neutral re-acquisition. |
| `diagrams/08_pressure_rhythm.png`, `diagrams/08_pressure_rhythm.svg` | Visual+source | Pressure rises and falls through combo, phase-two burst and reset windows instead of remaining maximal. |
| `diagrams/09_arena_and_spacing.png`, `diagrams/09_arena_and_spacing.svg` | Visual+source | Close-punish, ideal-polearm, approach/lunge bands inside a 1500 cm illustrative boundary. |
| `diagrams/10_damage_pipeline.png`, `diagrams/10_damage_pipeline.svg` | Visual+source | Contact validation, dedupe, i-frames, parry, guard, health/posture and logged feedback. |
| `diagrams/11_utility_scoring.png`, `diagrams/11_utility_scoring.svg` | Visual+source | Example eligible ranking A04>A02>A03>A01; A05/A08 rejected before scoring. The two rejection labels visibly overlap, a presentation defect noted in `09_REFERENCE_AMBIGUITIES.md`. |

## Concept asset

| File | Status | Notes |
|---|---|---|
| `concept_art/Ashen_Bellwarden_Concept_Sheet.png` | Visual | Original armored bell-bearing halberd boss; front/back silhouettes and thrust, sweep, slam and radial-ring action thumbnails support the illustrative case study only. |

## Coverage conclusion

No file remains unread, unparsed or visually uninspected. “Inspected” does not mean the reference C++ was compiled, the Python tests were executed, or any claim about the current game was evaluated.
