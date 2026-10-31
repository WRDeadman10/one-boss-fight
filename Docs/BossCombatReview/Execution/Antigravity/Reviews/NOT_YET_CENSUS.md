# Track B Remaining Requirements Census: 24 NOT YET Rows

**Document Reference:** `Reviews/NOT_YET_CENSUS.md`  
**Task Reference:** `[C-565]` (Track B Direction Selection Census)  
**Source Authority:** `witness_status_v3.json` (exact titles and observables)  
**Total Census:** 24 requirements currently classified as `NOT YET`  

---

## 1. Executive Summary & Classification Matrix

This document classifies all 24 remaining `NOT YET` combat requirements to inform the Owner's strategic roadmap choice across **Direction A** (Framework completion to full duel), **Direction B** (Track B soulslike boss framework polish), and **Direction C** (Pack-level authoring & Greystone integration).

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

## 2. Complete 24-Row NOT YET Census Table

| ID | Exact Title | Exact Observable | Dependency Class | Code Reference & Reason | Cost |
|:---|:---|:---|:---:|:---|:---:|
| **BOSS-AWR-006** | Observable player activity | Player flask drinking or heavy attack commitment raises priority of fast anti-greed card (MC-03). | `PLAYER-SIDE` | Player flask/heavy commitment state listener not exposed to boss perception (Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:180) | **M** |
| **BOSS-AWR-007** | LOS and memory | Occlusion by arena pillars triggers search / repositioning behavior instead of blind wall-striking. | `NEEDS NEW SYSTEM` | Line-of-sight raycast filter and obstacle memory search state missing in candidate selection (Source/OneBossFight/Player/RPGBossMoveSelector.cpp:45) | **L** |
| **BOSS-AWR-008** | Soft adaptation memory | Histogram of repeated backward player dodges triggers forward roll-catch gap-closer (MC-05) weighting boost. | `NEEDS NEW SYSTEM` | Recent player movement buffer and roll-catch adaptation weights not tracked in context (Source/OneBossFight/Player/RPGBossMoveSelector.cpp:30) | **L** |
| **BOSS-SEL-009** | Reaction latency and budget | AI reaction latency to player flask action is bounded by reaction delay window [0.2s - 0.4s]. | `ENGINE-ONLY` | AI reaction delay window [0.2-0.4s] before responding to player actions not wired in selector tick (Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:165) | **M** |
| **BOSS-EXE-005** | Explicit priority | Phase threshold crossing supersedes normal stagger and triggers phase transition animation. | `ENGINE-ONLY` | Phase threshold crossing priority over active stagger only exists in unit tests (Source/OneBossFight/Tests/RPGBossTransitionTests.cpp:25) | **M** |
| **BOSS-ANM-003** | Bounded holds | Variable windup holds are bounded between min and max duration with distinct visual audio cue at release. | `NEEDS ART` | Dynamic hold duration limits and release audio/visual notifies require authored animation notify tracks (Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:120) | **L** |
| **BOSS-ANM-006** | Bounded Motion Warping | Motion Warping translation and rotation strictly clamped to max warp distance (e.g. 150cm) and angle (e.g. 45°). | `NEEDS NEW SYSTEM` | Motion Warping plugin integration and translation/rotation clamping not enabled in runtime (Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:140) | **L** |
| **BOSS-HIT-010** | Direct/splash precedence | Direct weapon impact takes precedence over secondary shockwave / ground splash; simultaneous hit applies direct only. | `NEEDS DESIGN DECISION` | Simultaneous direct weapon and secondary splash precedence arbiter not defined in damage resolver (Source/OneBossFight/Damage/RPGDamageResolver.cpp:130) | **M** |
| **BOSS-HIT-011** | Swept annulus | Ground splash / shockwave sweeps outward in calibrated ring without invisible gaps or lingering ghost damage. | `NEEDS NEW SYSTEM` | Outward expanding ring/annulus sweep shape component not implemented in move executor (Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:190) | **L** |
| **BOSS-HIT-012** | Grab fail-safe | Interrupted grab releases victim immediately to ground locomotion without animation lock or falling through floor. | `NEEDS NEW SYSTEM` | Two-character grab state machine and interrupt victim release handler not implemented (Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:220) | **L** |
| **BOSS-MOV-002** | Combat positioning | Boss maintains center-arena bias when target is near walls, avoiding getting pinned in corners. | `NEEDS DESIGN DECISION` | Center-arena bias wall-clearance scoring when player hugs perimeter not implemented (Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:200) | **M** |
| **BOSS-MOV-003** | Movement commitment | Movement requests exhibit commitment hysteresis; boss does not flip direction every frame. | `ENGINE-ONLY` | Continuous movement commitment hysteresis / direction latching across frames not implemented (Source/OneBossFight/Player/RPGBossTrackRules.h:35) | **S** |
| **BOSS-MOV-004** | Wall-safe attacks | Forward charge attacks clamp movement trajectory when hitting arena boundary without clipping through. | `NEEDS ART` | Attack trajectory clamping against arena geometry bounds requires collision channel authoring (Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:150) | **M** |
| **BOSS-MOV-005** | Arena-valid responses | If player teleports outside arena bounds, boss leashes to arena center and resets to neutral. | `ENGINE-ONLY` | Leashing to arena center when player exits arena bounds not wired (Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:185) | **S** |
| **BOSS-MOV-006** | Arena/attack fit | Arena geometry (L_SevarogArena) provides clear combat lane with zero player snag points. | `NEEDS ART` | Production level L_SevarogArena geometry clearance and snag point audit requires level art verification (Source/OneBossFight/Tests/RPGAutomationTests.cpp:210) | **M** |
| **BOSS-PAC-002** | Pressure variation | Combo sequences interleave high pressure with deliberate tempo pauses (e.g. after MC-04 slam). | `NEEDS DESIGN DECISION` | Deliberate tempo pause nodes in combo sequences not authored in profile combo graph (Source/OneBossFight/Player/RPGBossComboRules.h:45) | **S** |
| **BOSS-PAC-003** | Guaranteed openings | Heavy finisher (MC-04) guarantees recovery window sufficient for player light or heavy punish counter-attack. | `PLAYER-SIDE` | Finisher recovery opening window validation against player counter-attack loop requires player attack intake (Source/OneBossFight/Player/RPGBossRules.h:60) | **M** |
| **BOSS-PAC-004** | Conditional opening cues | Visual recovery cues (scythe lodged in ground, posture reset) clearly indicate boss vulnerable state. | `NEEDS ART` | Vulnerability visual/audio cues (e.g. weapon lodged in ground) require animation assets and notifies (Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:135) | **L** |
| **BOSS-PAC-005** | Punish-margin calculation | Boss recovery duration exceeds player light attack startup + travel time by at least 0.3s. | `PLAYER-SIDE` | Mathematical verification that recovery duration exceeds player startup + travel time by >= 0.3s requires player moveset timings (Source/OneBossFight/Player/RPGBossRules.h:80) | **M** |
| **BOSS-DEF-004** | Windowed hyperarmor | Heavy moves (MC-04) possess hyperarmor during active swing; light attacks do not interrupt swing. | `ENGINE-ONLY` | Move card hyperarmor tag checking during active hit windows not wired into damage receiver (Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:330) | **S** |
| **BOSS-DEF-005** | Fair boss defense | Boss defensive actions (backstep, block) adhere to fair player counterplay windows. | `NEEDS ART` | Boss defensive actions (backstep, block animations) not authored in boss profile moveset (Source/OneBossFight/Player/RPGBossFrameworkProfile.h:40) | **M** |
| **BOSS-PHS-005** | Anti-cheese with counterplay | Extreme player kiting or hugging triggers anti-greed/gap-closer moves, preventing exploit loops. | `NEEDS DESIGN DECISION` | Player extreme kiting/hugging distance thresholds and anti-cheese trigger rules not defined (Source/OneBossFight/Player/RPGBossMoveSelector.cpp:55) | **M** |
| **BOSS-QA-006** | Camera/readability | Camera framing maintains boss visibility and readability across near and far distance bands. | `PLAYER-SIDE` | Combat camera framing evaluation requires player follow camera / lock-on system testing (Source/OneBossFight/Player/RPGFrameworkCharacter.cpp:50) | **M** |
| **BOSS-QA-007** | Accessible feedback | Combat telegraphed cues remain readable under low VFX and audio-only/visual-only conditions. | `NEEDS ART` | Low VFX and audio-only/visual-only accessibility contrast test harness requires multi-channel asset audit (Source/OneBossFight/Tests/RPGAutomationTests.cpp:240) | **L** |

---

## 3. Census Distribution Breakdown

### By Dependency Class:
- **NEEDS ART:** 6 requirements (25.0%)
- **NEEDS NEW SYSTEM:** 5 requirements (20.8%)
- **ENGINE-ONLY:** 5 requirements (20.8%)
- **PLAYER-SIDE:** 4 requirements (16.7%)
- **NEEDS DESIGN DECISION:** 4 requirements (16.7%)

### By Engine Run Cost:
- **Cost M:** 12 requirements (50.0%)
- **Cost L:** 8 requirements (33.3%)
- **Cost S:** 4 requirements (16.7%)
