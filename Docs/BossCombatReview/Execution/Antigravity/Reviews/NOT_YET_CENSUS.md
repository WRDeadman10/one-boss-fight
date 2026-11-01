# Track B Remaining Requirements Census: 22 NOT YET Rows

**Document Reference:** `Reviews/NOT_YET_CENSUS.md`  
**Task Reference:** `[C-565]` / `[C-568]` (Track B Direction Selection Census)  
**Source Authority:** `witness_status_v3.json` (exact titles and observables)  
**Total Census:** 22 requirements currently classified as `NOT YET`  

---

## 1. Executive Summary & Classification Matrix

This document classifies all 22 remaining `NOT YET` combat requirements to inform the Owner's strategic roadmap choice across **Direction A** (Framework completion to full duel), **Direction B** (Track B soulslike boss framework polish), and **Direction C** (Pack-level authoring & Greystone integration).

### Classification Definitions:
- **ENGINE-ONLY:** Pure C++ / runtime rules or hooks; no art or external system dependencies.
- **NEEDS ART:** Requires animations, montages, notify tracks, VFX/SFX, or arena mesh assets.
- **NEEDS DESIGN DECISION:** Requires designer threshold parameters, precedence rules, or pacing formulas.
- **NEEDS NEW SYSTEM:** Requires an entire unbuilt architectural subsystem (AoE sweeps, memory buffers, grab state machines).
- **PLAYER-SIDE:** Depends on player character combat mechanics, input buffers, or counter-attack intake.

### Cost Estimate Scale (in Engine Witness Runs):
- **S (Small):** 1-2 runs; a simple log line, query param, or cvar test hook.
- **M (Medium):** 2-4 runs; a new rule struct/method, unit tests, and live PIE proof scenario.
- **L (Large):** 4+ runs; new multi-component system, asset plumbing, and multi-actor interaction harness.

---

## 2. Complete 22-Row NOT YET Census Table

| ID | Exact Title | Exact Observable | Dependency Class | Code Reference & Reason | Cost |
|:---|:---|:---|:---:|:---|:---:|
| **BOSS-AWR-006** | Observable player activity | Player flask drinking or heavy attack commitment raises priority of fast anti-greed card (MC-03). | `PLAYER-SIDE` | no code: boss only reads target HP and transform; player activity tag listener and flask/heavy commitment observer not implemented in framework boss | **M** |
| **BOSS-AWR-007** | LOS and memory | Occlusion by arena pillars triggers search / repositioning behavior instead of blind wall-striking. | `NEEDS NEW SYSTEM` | no code: line-of-sight raycasts and obstacle search memory not implemented in boss selector or perception | **L** |
| **BOSS-AWR-008** | Soft adaptation memory | Histogram of repeated backward player dodges triggers forward roll-catch gap-closer (MC-05) weighting boost. | `NEEDS NEW SYSTEM` | no code: player movement history and dodge histogram tracking not implemented in AI context | **L** |
| **BOSS-SEL-009** | Reaction latency and budget | AI reaction latency to player flask action is bounded by reaction delay window [0.2s - 0.4s]. | `ENGINE-ONLY` | no code: AI reaction delay window [0.2-0.4s] buffering not implemented in boss tick loop | **M** |
| **BOSS-ANM-003** | Bounded holds | Variable windup holds are bounded between min and max duration with distinct visual audio cue at release. | `NEEDS ART` | no code: variable windup hold min/max durations and release cues not authored in move cards or montage tracks | **L** |
| **BOSS-ANM-006** | Bounded Motion Warping | Motion Warping translation and rotation strictly clamped to max warp distance (e.g. 150cm) and angle (e.g. 45°). | `NEEDS NEW SYSTEM` | no code: Motion Warping plugin not enabled in uproject and warp clamping bounds not implemented | **L** |
| **BOSS-HIT-010** | Direct/splash precedence | Direct weapon impact takes precedence over secondary shockwave / ground splash; simultaneous hit applies direct only. | `NEEDS DESIGN DECISION` | `Source/OneBossFight/Player/RPGDamageResolver.cpp:152` quote: `Result.Outcome = RPGDamageRules::Decide(bTargetAlive, bAtta`<br>resolver decide rule only takes alive, generation, duplicate, and invulnerable flags; no direct vs secondary splash precedence arbiter defined | **M** |
| **BOSS-HIT-011** | Swept annulus | Ground splash / shockwave sweeps outward in calibrated ring without invisible gaps or lingering ghost damage. | `NEEDS NEW SYSTEM` | `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:230` quote: `const FCollisionShape Shape=FCollisionShape::MakeCapsule(W.`<br>sweep only constructs linear swept capsules along weapon key poses; outward expanding ring/annulus component not implemented | **L** |
| **BOSS-HIT-012** | Grab fail-safe | Interrupted grab releases victim immediately to ground locomotion without animation lock or falling through floor. | `NEEDS NEW SYSTEM` | no code: grab state machine, victim attachment sync, and interrupt release fail-safe not implemented | **L** |
| **BOSS-MOV-002** | Combat positioning | Boss maintains center-arena bias when target is near walls, avoiding getting pinned in corners. | `NEEDS DESIGN DECISION` | `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:255` quote: `// Opt-in repositioning: nobody is eligible from here (the `<br>repositioning only walks straight toward target band without arena boundary or wall clearance scoring | **M** |
| **BOSS-MOV-003** | Movement commitment | Movement requests exhibit commitment hysteresis; boss does not flip direction every frame. | `ENGINE-ONLY` | `Source/OneBossFight/Player/RPGBossTrackRules.h:19` quote: `if (bCommitted||!FMath::IsFinite(DegPerSecond)||!FMath::IsFi`<br>nearest code, not the feature: turn tracking turns shortest-way each tick without movement direction latching or continuous locomotion hysteresis | **S** |
| **BOSS-MOV-004** | Wall-safe attacks | Forward charge attacks clamp movement trajectory when hitting arena boundary without clipping through. | `NEEDS ART` | no code: forward charge attack animations with root motion require level art perimeter collision geometry and collision preset authoring to prevent clipping | **M** |
| **BOSS-MOV-006** | Arena/attack fit | Arena geometry (L_SevarogArena) provides clear combat lane with zero player snag points. | `NEEDS ART` | `Source/OneBossFight/Tests/RPGAutomationTests.cpp:766` quote: `IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGArenaCollisionTest, "On`<br>collision tests only verify legacy ARPGGreyboxArena geometry; production level L_SevarogArena clearance and snag point audit requires level art verification | **M** |
| **BOSS-PAC-002** | Pressure variation | Combo sequences interleave high pressure with deliberate tempo pauses (e.g. after MC-04 slam). | `NEEDS DESIGN DECISION` | `Source/OneBossFight/Player/RPGBossComboRules.h:12` quote: `struct FComboEdge`<br>combo graph edges only specify target node, range, yaw, and outcome; no tempo pause delay or deliberate pacing duration field exists | **S** |
| **BOSS-PAC-003** | Guaranteed openings | Heavy finisher (MC-04) guarantees recovery window sufficient for player light or heavy punish counter-attack. | `PLAYER-SIDE` | `Source/OneBossFight/Player/RPGBossMoveCard.h:60` quote: `UPROPERTY(EditAnywhere) float RecoveryEndSeconds = 0.f;`<br>move card specifies static RecoveryEndSeconds; validation against player punish attack timings requires player moveset intake | **M** |
| **BOSS-PAC-004** | Conditional opening cues | Visual recovery cues (scythe lodged in ground, posture reset) clearly indicate boss vulnerable state. | `NEEDS ART` | no code: visual/audio recovery cues (e.g. scythe lodged in ground) require authored animation notify tracks and VFX | **L** |
| **BOSS-PAC-005** | Punish-margin calculation | Boss recovery duration exceeds player light attack startup + travel time by at least 0.3s. | `PLAYER-SIDE` | no code: punish margin formula (recovery > player startup + travel + 0.3s) requires player moveset startup data | **M** |
| **BOSS-DEF-004** | Windowed hyperarmor | Heavy moves (MC-04) possess hyperarmor during active swing; light attacks do not interrupt swing. | `ENGINE-ONLY` | `Source/OneBossFight/Player/RPGWeaponAttackTable.h:44` quote: `float HyperArmorStart = -1.f;`<br>nearest code, not the feature: hyperarmor window fields exist only for player attacks in RPGWeaponAttackTable; hyperarmor tags not implemented for boss move cards | **S** |
| **BOSS-DEF-005** | Fair boss defense | Boss defensive actions (backstep, block) adhere to fair player counterplay windows. | `NEEDS ART` | no code: defensive moves (backstep, block) not authored in boss profile moveset or animation cards | **M** |
| **BOSS-PHS-005** | Anti-cheese with counterplay | Extreme player kiting or hugging triggers anti-greed/gap-closer moves, preventing exploit loops. | `NEEDS DESIGN DECISION` | `Source/OneBossFight/Player/RPGBossMoveSelector.cpp:49` quote: `if (Out.ChosenIndex==INDEX_NONE || T.Score>Out.Score) { Out.`<br>candidate evaluation selects solely by highest score among eligible cards; no anti-cheese override or exploit loop detector exists | **M** |
| **BOSS-QA-006** | Camera/readability | Camera framing maintains boss visibility and readability across near and far distance bands. | `PLAYER-SIDE` | no code: camera framing and lock-on tracking evaluation requires player follow camera / lock-on system testing | **M** |
| **BOSS-QA-007** | Accessible feedback | Combat telegraphed cues remain readable under low VFX and audio-only/visual-only conditions. | `NEEDS ART` | no code: low VFX / audio-only / visual-only contrast testing harness not authored in project | **L** |

---

## 3. Census Distribution Breakdown

### By Dependency Class:
- **NEEDS ART:** 6 requirements (25.0%)
- **NEEDS NEW SYSTEM:** 5 requirements (20.8%)
- **PLAYER-SIDE:** 4 requirements (16.7%)
- **NEEDS DESIGN DECISION:** 4 requirements (16.7%)
- **ENGINE-ONLY:** 3 requirements (12.5%)

### By Engine Run Cost:
- **Cost M:** 11 requirements (45.8%)
- **Cost L:** 8 requirements (33.3%)
- **Cost S:** 3 requirements (12.5%)
