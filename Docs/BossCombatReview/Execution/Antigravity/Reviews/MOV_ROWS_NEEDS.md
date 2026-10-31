# Witness Requirements & Existing Repo Infrastructure for 12 NOT YET Rows

This document specifies the exact witness requirements (data, code, observable log, and PIE scenario) and verified repository citations for 12 open `NOT YET` combat ledger rows, prepared per Claude instruction `[C-544]`.

---

### `BOSS-MOV-002` (Combat positioning)
- **Requirement**: Candidate positions score reachability, distance, LOS, wall/hazard clearance, flank, and variety with center-arena bias.
- **Witness Needs**: Profile scoring weights; candidate evaluation in controller scoring wall clearance vs target band; log `[FrameworkProof] positioning_candidate ...`; PIE run with target at wall verifying center bias.
- **Existing Pieces**: `Source/OneBossFight/Boss/RPGFrameworkBossController.cpp:8` (`ARPGFrameworkBossController::WalkToBand`); `Source/OneBossFight/Player/RPGBossFrameworkProfile.h:51` (`BandMinCm`); `Content/OneBossFight/Maps/L_SevarogArena.umap`.
- **Gaps**: Zero candidate scoring or wall clearance logic exists in C++ today; locomotion is purely direct band navigation in `WalkToBand`.

### `BOSS-MOV-003` (Movement commitment)
- **Requirement**: Strafe/approach choices have minimum commitment duration and hysteresis; boss does not flip direction every frame.
- **Witness Needs**: Authored commitment duration / lock window; timer latch in controller/character preventing goal abortion/flip; log `[FrameworkProof] move_goal_commit ...`; PIE run with rapid target crossing verifying stable heading.
- **Existing Pieces**: `Source/OneBossFight/Player/RPGBossFrameworkProfile.h:55` (`WalkTimeoutSeconds`); `Source/OneBossFight/Boss/RPGFrameworkBossController.h:17` (`OwnedRequest`); `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:71, 87` (`WalkToBand` init latch and arrival stop).
- **Gaps**: Locomotion currently stops immediately upon reaching band; no multi-frame strafe direction commitment or hysteresis latch exists.

### `BOSS-MOV-004` (Wall-safe attacks)
- **Requirement**: Root-motion/warp paths predict walls and use correction, fallback or decline; forward travel clamps at arena boundary without clipping.
- **Witness Needs**: Collision sweep lookahead distance on attack cards; pre-attack/per-tick sweep in executor clamping displacement; log `[FrameworkProof] attack_wall_clamp travelRequested=... clamped=...`; PIE travel attack near wall.
- **Existing Pieces**: `Source/OneBossFight/Player/RPGBossMoveCard.h:69` (`bUsesRootMotion`); `Source/OneBossFight/Player/RPGBossMoveCard.cpp:45` (rejects root motion with `MoveCard.UnsupportedRootMotion`); `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:58` (`SetCapsuleSize`).
- **Gaps**: Executor backend is currently in-place only; root motion is actively refused by compiler validator; zero wall-clamping sweep exists.

### `BOSS-MOV-005` (Arena-valid responses)
- **Requirement**: Unreachable/elevated/outside targets trigger reposition, search, leash, or reset to center rather than infinite chase.
- **Witness Needs**: Out-of-bounds / unreachable target trigger; leash-to-center state in character; log `[FrameworkProof] leash_reset targetUnreachable=1 action=LeashToCenter`; PIE scenario with target teleported outside navmesh.
- **Existing Pieces**: `Source/OneBossFight/Boss/RPGFrameworkBossController.cpp:18, 28` (`Framework.Nav.Projection` & `NoFullPath`); `Source/OneBossFight/Player/RPGBossFrameworkProfile.h:101` (`RepositionMax`); `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:169` (`reposition attempt` log); `Docs/BossCombatReview/Execution/Claude/B_SHIFT/pie_shift_run1_late_and_far/editor_raw.log:1784` (`Framework.Selector.NoCandidate`).
- **Gaps**: Fails closed on unreachable target (`NoCandidate`); no dedicated leash-to-center locomotion task implemented yet.

### `BOSS-MOV-006` (Arena/attack fit)
- **Requirement**: Arena geometry (`L_SevarogArena`) provides clear combat lane with zero snag points; escape and camera visibility valid from all legal positions.
- **Witness Needs**: Spatial grid audit parameters; automated sweep probe sampling arena bounds against attack radii and camera boom; log `[FrameworkProof] arena_fit_probe samples=... snags=0`; PIE perimeter sweep.
- **Existing Pieces**: `Content/OneBossFight/Maps/L_SevarogArena.umap` (production level); `Content/OneBossFight/FrameworkProof/L_SevarogFrameworkProof.umap` (proof map); `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:89` (logs capsule and mesh arena coordinates).
- **Gaps**: Arena geometry exists as asset but lacks an automated camera/navigation sweep harness verifying absence of geometry snags.

### `BOSS-PAC-003` (Guaranteed openings)
- **Requirement**: Heavy finisher (e.g. MC-04) guarantees recovery window unconditionally sufficient for player light or heavy punish counter-attack.
- **Witness Needs**: Authored card `RecoveryEndSeconds - ActiveEndSeconds` >= player attack duration; recovery state latch; log `[FrameworkProof] event ... kind=Recovery`; PIE run where player lands confirmed hit during boss recovery.
- **Existing Pieces**: `Source/OneBossFight/Player/RPGBossMoveCard.h:60` (`RecoveryEndSeconds`); `Docs/BossCombatReview/Execution/Antigravity/MoveCards/move_cards_f5_set.json:25` (`SwingSlow` recovery 1.158s); `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:224` (`kind=Recovery` log); `Docs/BossCombatReview/Execution/Claude/B_SHIFT/pie_shift2/editor_raw.log:1858` (`acceptedHits=2`).
- **Gaps**: Recovery timing exists on cards and executor logs `Recovery`, but lacks dedicated test/PIE script proving player counter-attack window safety.

### `BOSS-PAC-005` (Punish-margin calculation)
- **Requirement**: Opening classification includes travel, player startup and safety buffer, not montage recovery alone; boss recovery exceeds startup + travel by >= 0.3s.
- **Witness Needs**: Loadout startup metrics, travel speed model, margin equation (`Margin = BossRecovery - (PlayerStartup + Travel) >= 0.3s`); test/runtime margin validator; log `[FrameworkProof] punish_margin margin=... >=0.3s`; PIE punish from 0m/1m/2m.
- **Existing Pieces**: `Docs/BossCombatReview/Execution/Antigravity/MoveCards/move_cards_f5_set.json:25` (`SwingSlow` recovery 1.158s); `Docs/BossCombatReview/Execution/Antigravity/Reviews/C5_WEAPON_DATA_AUDIT.md:20` (player weapon startup metrics); `Source/OneBossFight/Tests/RPGFrameworkRuntimeTests.cpp:225` (`ApplyPlayerAttackHit`).
- **Gaps**: Explicit punish margin formula is documented in audit but not asserted in an automated test or runtime telemetry log line.

### `BOSS-SEL-009` (Reaction latency and budget)
- **Requirement**: AI reaction latency to player flask action is bounded by reaction delay window [0.2s - 0.4s] with explicit reaction budget.
- **Witness Needs**: Authored delay range `[0.2s, 0.4s]` and reaction budget in profile; player flask listener triggering deferred response selection; log `[FrameworkProof] reactive_counter stimulus=Flask latency=...`; PIE flask drink during neutral.
- **Existing Pieces**: `Source/OneBossFight/Player/RPGBossFrameworkProfile.h:68` (`Cards`); `Source/OneBossFight/Player/RPGBossMoveSelector.h:17` (`CooldownSeconds` hard filter); `Source/OneBossFight/Player/RPGBossMoveSelector.cpp:24` (`NoteStarted`); `Source/OneBossFight/Tests/RPGFlaskHudTests.cpp:1` (flask test suite).
- **Gaps**: Selector polls every tick without stimulus listeners; zero reaction delay buffer `[0.2s, 0.4s]` or reaction budget exists in C++.

### `BOSS-EXE-005` (Explicit priority)
- **Requirement**: Death, phase, stance, special, combo, and completion conflicts follow a documented deterministic order; phase transition supersedes normal stagger.
- **Witness Needs**: Explicit priority enum/order documentation; state resolver enforcing priority across simultaneous events; log `[FrameworkProof] priority_resolve pending=... resolved=...`; PIE simultaneous threshold crossing.
- **Existing Pieces**: `Source/OneBossFight/Player/RPGBossRules.h:8, 54, 70` (`RPGBossRules::ResolveBreak` & `ResolveTransition`); `Source/OneBossFight/Tests/RPGAutomationTests.cpp:214, 220` (unit tests asserting priority); `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:115, 130, 236` (death & phase order).
- **Gaps**: Priority order is unit-tested in `RPGAutomationTests` and `RPGCodexTests`, but simultaneous phase + posture break has not been witnessed live in PIE.

### `BOSS-DEF-004` (Windowed hyperarmor)
- **Requirement**: Interruption resistance exists only for named moves/windows; heavy moves possess hyperarmor during active swing; light attacks do not interrupt swing.
- **Witness Needs**: `HyperarmorStartSeconds`/`EndSeconds` on card; damage intake checking hyperarmor window to suppress hit stun/abort; log `[FrameworkProof] damage_absorbed hyperarmor=1 interrupted=0`; PIE player hit during active heavy swing.
- **Existing Pieces**: `Source/OneBossFight/Player/RPGSwingRules.h:14` & `Source/OneBossFight/Player/RPGWeaponAttackTable.h:42` (`HyperArmorStart`/`End`); `Source/OneBossFight/Player/RPGSwingTracker.h:93` (`IsHyperArmorActive`); `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:230, 247` (`ApplyHit` damage absorption without abort).
- **Gaps**: Framework boss absorbs damage without interrupting active swings (stagger requires posture break), but lacks per-card windowed hyperarmor authoring.

### `BOSS-DEF-005` (Fair boss defense)
- **Requirement**: Boss defensive actions (backstep, block) adhere to fair player counterplay windows with facing, startup, cooldown, cost, and recovery constraints.
- **Witness Needs**: Defensive move cards (backstep, block) with authored recovery and cooldown; defensive branch selector; log `[FrameworkProof] boss_defense action=... state=Recovery vulnerable=1`; PIE player punish during defensive recovery.
- **Existing Pieces**: `Source/OneBossFight/Player/RPGBossMoveModel.h:20` (`ERPGBossMoveModelState::Recovery`); `Source/OneBossFight/Player/RPGBossMoveCard.h:60` (`RecoveryEndSeconds`); `Source/OneBossFight/Player/RPGBossMoveSelector.h:17` (`CooldownSeconds`); `Docs/BossCombatReview/Execution/Antigravity/MoveCards/move_cards_f5_set.json:68` (card cooldowns).
- **Gaps**: Zero dedicated defensive cards (backstep, block, parry) are authored in `RPGBossFrameworkProfile` or candidate move sets.

### `BOSS-PHS-005` (Anti-cheese with counterplay)
- **Requirement**: Extreme player kiting or hugging triggers anti-greed/gap-closer moves, preventing exploit loops.
- **Witness Needs**: Range/yaw exploit thresholds in selector; anti-greed / gap-closer move cards; log `[FrameworkProof] decision ... chosen=Move_Sevarog_AntiGreed_F5 range=...`; PIE sustained player kiting triggering anti-greed.
- **Existing Pieces**: `Docs/BossCombatReview/Execution/Antigravity/MoveCards/move_cards_f5_set.json:68` (`Move_Sevarog_AntiGreed_F5` range 90-185cm, cooldown 2.5s); `Source/OneBossFight/Player/RPGBossMoveSelector.cpp:45` (candidate scoring); `Docs/BossCombatReview/Execution/Claude/B_SHIFT/pie_shift2/editor_raw.log:1784` (`decision attack=2 chosen=Move_Sevarog_AntiGreed_F5 range=183.489`).
- **Gaps**: Card and selector selection proven in PIE (`pie_shift2`), but sustained anti-cheese loop prevention across multiple kiting cycles is unproven.
