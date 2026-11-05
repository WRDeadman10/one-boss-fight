# H3 — A7 Option B legacy retirement plan

**Plan only.** The owner decided to retire legacy startup later, after the
release gates close. Legacy remains fallback and parity control now; this
document authorizes no Source, asset, default, or route change.

## Likely later change surface

| Area | Candidate touchpoint | Retirement work to review |
|---|---|---|
| Startup routing | `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:100-200` | Replace the empty-selection legacy branch with the owner-approved post-retirement behavior; preserve fail-closed semantics for requested selected routes. Keep the J049 setter route. |
| Legacy boss registration | `RPGPlayerMovesSubsystem.cpp:644-745` (`AttachLegacyBossPrelude` / `AttachLegacyBossBundle`) and `:746-775` (`Attach`) | Remove only legacy auto-registration after proving selected-mode replacements own required consumers; preserve separately owned player setup and diagnostics where still needed. |
| Spawn/lifecycle branch | `RPGPlayerMovesSubsystem.cpp:233-294` | Reassess late-spawn attachment and reset/rebind paths so no spawn can silently fall back to legacy. |
| Header/API declarations | `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.h:44-54` (`Attach`, player/legacy attachment helpers) | Remove or split only declarations made dead by the reviewed implementation. Do not remove the approved `SetSelectedDefinition` API (`RPGEncounterSelectionSubsystem.h:30`). |
| Runtime and PIE tests | `Source/OneBossFight/Tests/RPGBossStartupActivationTests.cpp:293-312` (`AbsentPreservesLegacyStartup`), `:313-352` (`SelectedStartupActivatesExactParticipants`), `:353-419` (respawn/rebind); `Scripts/Editor/pie_selection_refusal.py` | Replace the current no-selection/legacy expectation with the decided post-retirement behavior. Keep missing/invalid selected refusal, no legacy component leakage, valid setter activation and fresh process lifecycle cases. Re-run all current 31-driver parity coverage with selected-route baselines; old legacy-vs-data pairs cannot be treated as a post-retirement control. |
| Drivers/benchmark | `Scripts/RunDrivers.ps1`; A4/A5 parity pair runners; `Scripts/RunBenchmark.ps1` | Remove legacy arm only after approved replacement evidence exists; preserve G1's Development-only selected benchmark entry. |
| Content/assets | `/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter`; `/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Boss_EmberWarden_Draft`; `/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Player_Hero_Draft_V3`; `/Game/OneBossFight/Levels/L_SevarovArena` | H1/H2 must establish caller/dependency scope first. No asset deletion is identified by current source evidence. If any map/Blueprint caller or dependency must change, list exact asset and referencers and obtain the required approval before modifying it. |
| Documentation | `J041_J045_SELECTED_ROUTE_OPERATIONS.md`, `J049_OWNER_DECISION_PACKET.md`, `L026_L030_SHIPPING_SELECTOR_AUDIT.md`, `P15_A7_PARITY_SUMMARY_DRAFT.md`, `G5_A7_J049_OWNER_BRIEF.md`, `G1_A7_BENCHMARK_EXPECTED.md`, `G4_SAVE_CONTENT_COMPATIBILITY_AUDIT.md`, `TASKS.md`, `PROJECT_STATE.md`, `TEST_PLAN.md`, `KNOWN_ISSUES.md`, `GATE4_RUNBOOK.md` | Update fallback/recovery instructions, decision state, test inventory, and benchmark/control descriptions to the approved final route. |

## Required green gates before a retirement change

1. J049-A Blueprint caller inventory complete; packaged Shipping setter call
   activates the selected G044 route; empty selection/fallback behavior is
   dispositioned for the exact retirement rollout.
2. H2 dependency closure reconciled with the authoritative Shipping cook
   manifest; packaged selected activation and refusal recovery pass.
3. G1 selected-route Development benchmark meets average FPS, p99, and
   legacy-comparison thresholds on RTX 2060 Super in the physical console
   session; retain raw frame files and summaries.
4. Accepted A5 parity evidence and all disclosed WARN decisions are preserved;
   required replacement tests cover selected startup, valid setter selection,
   respawn/rebind, missing/invalid refusal, and no legacy auto-attachment.
5. Claude reviews the complete implementation diff and full native/offline/
   packaged suite before any later owner-approved removal.

No exact asset retirement/deletion is proposed here. The component/source list
is provisional until H1/H2 and the final selected-route implementation are
reviewed.
