# BB-A25: Arena Space & Navigation Review for Sevarog (`L_SevarogArena`)

**Queue Lane:** `QUEUE_BB` Task `BB-A25` (Antigravity)  
**Authority:** `Documentation/Boss/QUEUE_BB.md`, `[C-1267]`  
**Sources:** `Source/OneBossFight/Arena/RPGGreyboxArena.h`, `Documentation/Boss/C1258A_SEVAROG_IN_BAND_NAV_AND_END.md`, `Documentation/Boss/BB_X06_X10_HANDOFF.md`, `Scripts/Editor/author_sevarog_draft_cards.py`  
**Status:** Read-only spatial & nav-coverage review (no map, C++, or card edits)  

---

## 1. Arena Physical Geometry (`RPGGreyboxArena.h`)

| Arena Feature | Source Property (`RPGGreyboxArena.h`) | Measured Radius / Span | Spatial Implication for Sevarog |
|---|---|---:|---|
| Outer Collision Wall | `ArenaRadius` (`line 43`) | `3000 cm` (`30.0 m`, `60.0 m` dia.) | Circular enclosed disc; boundary stops both actor capsules and warps |
| Perimeter Pillar Ring | `PillarRingFraction = 0.9f` (`line 53`), `PillarCount = 12` (`line 49`), `PillarRadius = 120 cm` (`line 56`) | Ring at `2700 cm`; inner cylinder face at `2580 cm` (`25.8 m`) | `12` solid cylinder blockers ring the outer `4.2 m` perimeter |
| Brazier Ring | `BrazierRingFraction = 0.78f` (`line 103`) | Ring at `2340 cm` (`23.4 m`) | Places `12` brazier collision props at `23.4 m`; leaves **unobstructed central combat disc of radius ~`22.0 m` (`~44.0 m` clear diameter)** |
| Sevarog Capsule | `author_sevarog_draft_cards.py:55` | `Radius = 60 cm`, `HalfHeight = 165 cm` | Taller/wider footprint (`120 cm` dia.) than human targets; requires clean pillar-to-wall clearance (`288 cm` gap between adjacent pillar edge and wall) |

---

## 2. Dash & Engagement Lane Fit (`S4 Speedburst` `3.0–6.5 m`)

| Move / Mechanic | Configured Span (`author_sevarog_draft_cards.py`) | Fit Inside Clear Center (`44.0 m` dia.) | Clearance Margin & Edge Cases |
|---|---|---:|---|
| **`S4 Speedburst` Selector Band** | `MinRangeCm = 300 cm` (`3.0 m`), `MaxRangeCm = 650 cm` (`6.5 m`), `FrontConeDegrees = 120°` (`lines 324-326`) | **PASS (`14.8%` of clear diameter at max `6.5 m`)** | A full `6.5 m` dash lane + `4.5 m` bounded warp (`WarpMaxDistanceCm = 450 cm`, `Standoff = 120 cm`, `lines 318-320`) fits comfortably **3x–6x** inside the `44 m` obstacle-free center |
| **`S4 -> S5` (`Swing1_Medium`) Combo Finish** | Ends dash at `120 cm` standoff inside `S5` range `90–185 cm` | **PASS** | Collision-swept `TickWarp` (`RPGFrameworkMoveExecutor.cpp:423-478`) stops cleanly if player kites toward `23.4 m` brazier / `25.8 m` pillar rings |
| **`S1..S3` Close Band + Approach** | Band `110–140 cm` (`line 52`), card max `180 cm` | **PASS in center; wall-corner caution** | Near `PillarRing` (`25.8 m`), pillar diameter (`240 cm`) + Sevarog capsule radius (`60 cm`) can narrow flanking angles, requiring functioning `RecastNavMesh` pathing around pillars |

---

## 3. Navigation Coverage & `BB-X09` Findings Review

From Codex `C1258A_SEVAROG_IN_BAND_NAV_AND_END.md` and `BB_X06_X10_HANDOFF.md` (`X09–X10`):
1. **NavMesh & Controller Confirmed Present:** PIE confirmed one `RecastNavMesh` actor in `L_SevarogArena` and valid `RPGFrameworkBossController` attachment (`nav request=1 ... fullPath=1`).
2. **Spawn Projection Anomaly (`217.275 cm` Vertical Delta):** When `SpawnFrameworkBossForTest` spawned Sevarog in `C1258A`, `ProjectPointToNavigation` resolved from spawn `Z = 227.28 cm` down to `Z = 10.00 cm` (`-217.275 cm`). Following that elevated start, `OnMoveCompleted` emitted `Framework.Nav.MoveFailed` even though a full path had been returned.
3. **`BB-X09` / `BB-X10` Open Root Cause:** `OnMoveCompleted` (`RPGFrameworkBossController.cpp:51-58`) logs `Framework.Nav.MoveFailed` without printing `FPathFollowingResult` (`Code` + `Flags`) or boss position/velocity at failure, leaving `X10` **BLOCKED** until a Lead diagnostic capture logs the exact result code on an elevated vs floor-level (`Z ~ 175 cm` capsule center for `165 cm` half-height) spawn.

### Actionable Arena / Nav Checklist (For Lead / Codex Next Pass)
1. **Diagnostic First (`X09` Follow-Up):** Log `FPathFollowingResult::Code`, flags, and `(BossZ, NavProjectedZ)` inside `RPGFrameworkBossController::OnMoveCompleted` so live `WalkToBand` failures distinguish elevated-spawn `OffNavMesh`/`Blocked` from mid-arena pathing loss around pillars/braziers.
2. **Verify Spawn & Perimeter NavMesh Holes:** Once `FPathFollowingResult` is logged, run one non-test-shortcut `WalkToBand` check across three arena zones: center disc (`r < 10 m`), mid-ring (`r = 18 m`), and outer pillar corridor (`r = 25 m`), verifying `S4` `3.0–6.5 m` lanes never fail path-follow before dash warp handoff.
