# C-1256a Sevarog runtime spawn bridge

## Scope

Added `SpawnFrameworkBossForTest` as a BlueprintCallable test API on `ARPGFrameworkBossCharacter`. It refuses null classes and non-game worlds, uses collision-safe spawn adjustment, marks the actor transient, and returns no actor in Shipping. The Sevarog PIE driver now calls this API and derives the Speedburst follow-up from the profile's `ComboNodes` instead of naming S5 in code.

## Validation

- Development build: exit 0.
- Full `Automation RunTests OneBossFight`: 500 started, 500 passed, 0 failed; manifest `cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec`.
- PIE self-test under C-1155: `PROFILE PASS`, combo readback `Speedburst -> Swing1_Medium`, all three reflected bridge calls available, transient Sevarog spawned at 205.6 cm, and `Move_Sevarog_Swing1_Medium` started. The driver then stopped PIE. `MAP_SAVED=0`.
- The live self-test confirms only spawn plus one S1 start. Claude owns the full card sequence and its runtime review.
- Python syntax, PowerShell AST parse, and scoped `git diff --check` pass. The project editor and C-1155 locks were closed/released after validation.

Evidence: `Docs/BossCombatReview/Execution/Codex/C1256A_SPAWN_BRIDGE/{build.log,suite.log,pie_self_test.log,*status.txt}`.
