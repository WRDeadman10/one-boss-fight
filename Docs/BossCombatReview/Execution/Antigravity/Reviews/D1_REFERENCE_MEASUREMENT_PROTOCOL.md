# D1 Reference Measurement Protocol (v2)

**Task:** C-488 / C-490 -- D1 Reference Measurement Protocol for Morgott combat reference footage.
**Video:** `Documentation/Boss/Morgott_82_Point_Combat_Reference/Elden Ring - Morgott, The Omen King Boss Fight.webm` (777 MB, AV1 3840x2160, ~59.94 fps, 335.5 s).
**Combat Start:** 01:45 original-video time = 105.000 s (combat-relative zero `t_combat = t_orig - 105.000 s`).
**Status:** OFFLINE ONLY -- no Source/Content edits, no git commit until accepted.

---

## 1. Exhaustive Classification of all 82 Framework Rows

Every single row ID from `Documentation/Boss/Morgott_82_Point_Combat_Reference/requirements.json` is classified exactly once below.
Prefix distribution: HIT (12), SEL (10), AWR (8), EXE (8), ANM (8), COM (7), QA (7), MOV (6), PAC (6), DEF (5), PHS (5). Total: **82 rows**.

### Summary of Classification Counts

- **OBSERVABLE:** 22 rows (directly measurable animation frames, visual geometry, phase cues, and events).
- **PARTIAL:** 27 rows (inferable from visible gameplay patterns, but internal thresholds/formulas/code are UNKNOWN).
- **NOT OBSERVABLE:** 33 rows (pure internal state, private engine math, asset architectures, or QA telemetry; UNKNOWN).
- **TOTAL:** 82 rows (exactly 82/82 accounted for, 0 duplicates, 0 missing).

### Complete 82-Row Classification Table

| Row ID | Title | Class | Why | What Can Be Measured / Inferred |
|---|---|---|---|---|
| BOSS-AWR-001 | Target validity | **PARTIAL** | External behavior or pattern is visible and inferable, but internal code, data structures or exact formulas cannot be verified. | Inferable: Boss targets active player and stops attacking after player dies; internal targetability filter UNKNOWN. |
| BOSS-AWR-002 | Gate-time snapshot | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-AWR-003 | Distance convention | **PARTIAL** | External behavior or pattern is visible and inferable, but internal code, data structures or exact formulas cannot be verified. | Inferable: Visual differences in effective range between weapons; internal root vs capsule convention UNKNOWN. |
| BOSS-AWR-004 | Signed angle and hysteresis | **OBSERVABLE** | Directly visible animation cue, spatial position or game event in 60fps footage. | Tail sweep and turnaround attack selection when player is in rear arc vs frontal attacks. |
| BOSS-AWR-005 | Vertical separation | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-AWR-006 | Observable player activity | **OBSERVABLE** | Directly visible animation cue, spatial position or game event in 60fps footage. | Immediate boss reaction (projectile / thrust) upon player flask usage or block. |
| BOSS-AWR-007 | LOS and memory | **PARTIAL** | External behavior or pattern is visible and inferable, but internal code, data structures or exact formulas cannot be verified. | Inferable: Tracking behavior around pillars; internal raycast/memory timer UNKNOWN. |
| BOSS-AWR-008 | Soft adaptation memory | **PARTIAL** | External behavior or pattern is visible and inferable, but internal code, data structures or exact formulas cannot be verified. | Inferable: Attack variety shifts over prolonged duel; internal adaptation weight array UNKNOWN. |
| BOSS-SEL-001 | Legal decision gates | **PARTIAL** | External behavior or pattern is visible and inferable, but internal code, data structures or exact formulas cannot be verified. | Inferable: Attack initiation occurs at movement/animation completion; internal gate evaluation UNKNOWN. |
| BOSS-SEL-002 | Hard-filter precedence | **PARTIAL** | External behavior or pattern is visible and inferable, but internal code, data structures or exact formulas cannot be verified. | Inferable: Far attacks never trigger at point-blank; internal hard-filter precedence code UNKNOWN. |
| BOSS-SEL-003 | Executable asset gate | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-SEL-004 | Normalized utility | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-SEL-005 | Bounded randomness | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-SEL-006 | Cooldown semantics | **PARTIAL** | External behavior or pattern is visible and inferable, but internal code, data structures or exact formulas cannot be verified. | Inferable: Minimum measured interval between identical attacks; internal timer data structure UNKNOWN. |
| BOSS-SEL-007 | Anti-repeat memory | **PARTIAL** | External behavior or pattern is visible and inferable, but internal code, data structures or exact formulas cannot be verified. | Inferable: Frequency of repeated attacks in short windows; internal anti-repeat history deck UNKNOWN. |
| BOSS-SEL-008 | No-candidate fallback | **PARTIAL** | External behavior or pattern is visible and inferable, but internal code, data structures or exact formulas cannot be verified. | Inferable: Repositioning/idle behavior when player is out of attack ranges; internal fallback UNKNOWN. |
| BOSS-SEL-009 | Reaction latency and budget | **PARTIAL** | External behavior or pattern is visible and inferable, but internal code, data structures or exact formulas cannot be verified. | Inferable: Reaction latency (frames from player action to boss branch); internal reaction budget UNKNOWN. |
| BOSS-SEL-010 | Decision trace | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-EXE-001 | Single execution authority | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-EXE-002 | Instance before montage | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-EXE-003 | Start rollback | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-EXE-004 | Stale event rejection | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-EXE-005 | Explicit priority | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-EXE-006 | Idempotent abort | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-EXE-007 | Watchdog | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-EXE-008 | Cleanup-before-unlock | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-COM-001 | Authored graph | **OBSERVABLE** | Directly visible animation cue, spatial position or game event in 60fps footage. | Visible multi-hit attack sequences (e.g. curved sword 1-2-3 chain, spear into sweep). |
| BOSS-COM-002 | Gate after damage | **PARTIAL** | External behavior or pattern is visible and inferable, but internal code, data structures or exact formulas cannot be verified. | Inferable: Combo termination differences on whiff vs connect; internal post-damage gate UNKNOWN. |
| BOSS-COM-003 | Fresh branch context | **PARTIAL** | External behavior or pattern is visible and inferable, but internal code, data structures or exact formulas cannot be verified. | Inferable: Follow-up branch selection matches player position at gate; internal FCombatContext struct UNKNOWN. |
| BOSS-COM-004 | Explicit hit-confirm policy | **PARTIAL** | External behavior or pattern is visible and inferable, but internal code, data structures or exact formulas cannot be verified. | Inferable: Whiff cancels vs committed follow-ups; internal hit-confirm delegate UNKNOWN. |
| BOSS-COM-005 | Single-use gate | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-COM-006 | Finite pressure | **OBSERVABLE** | Directly visible animation cue, spatial position or game event in 60fps footage. | Combos terminate into recovery windows; count of consecutive hits before boss reset. |
| BOSS-COM-007 | Default recovery | **PARTIAL** | External behavior or pattern is visible and inferable, but internal code, data structures or exact formulas cannot be verified. | Inferable: Boss returns to neutral pose when sequence ends; internal fallback recovery code UNKNOWN. |
| BOSS-ANM-001 | Montage timeline authority | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-ANM-002 | Telegraph phases | **OBSERVABLE** | Directly visible animation cue, spatial position or game event in 60fps footage. | Exact frame duration of windup poses and visual weapon conjuring cues. |
| BOSS-ANM-003 | Bounded holds | **OBSERVABLE** | Directly visible animation cue, spatial position or game event in 60fps footage. | Maximum hold duration of delayed weapon swings before release. |
| BOSS-ANM-004 | Staged rotation cap | **OBSERVABLE** | Directly visible animation cue, spatial position or game event in 60fps footage. | Boss yaw tracking rate during windup vs locked trajectory upon attack release. |
| BOSS-ANM-005 | Exclusive motion authority | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-ANM-006 | Bounded Motion Warping | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-ANM-007 | Notify-end independence | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-ANM-008 | MoveCard handoff | **PARTIAL** | External behavior or pattern is visible and inferable, but internal code, data structures or exact formulas cannot be verified. | Inferable: Fluid animation blending between combo stages; internal UE MoveCard asset structure UNKNOWN. |
| BOSS-HIT-001 | Geometry fidelity | **OBSERVABLE** | Directly visible animation cue, spatial position or game event in 60fps footage. | Visual arc extent and screen-space reach of weapon models across frames. |
| BOSS-HIT-002 | Swept temporal sampling | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-HIT-003 | Blade interior samples | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-HIT-004 | Adaptive substeps | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-HIT-005 | Query filtering | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-HIT-006 | Logical-victim dedupe | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-HIT-007 | Explicit hit policy | **OBSERVABLE** | Directly visible animation cue, spatial position or game event in 60fps footage. | Damage application occurs once per blade pass; persistent hazard timings. |
| BOSS-HIT-008 | Central defense order | **PARTIAL** | External behavior or pattern is visible and inferable, but internal code, data structures or exact formulas cannot be verified. | Inferable: Player block/parry/dodge interaction outcomes; central defense evaluation order UNKNOWN. |
| BOSS-HIT-009 | Iframe completeness | **PARTIAL** | External behavior or pattern is visible and inferable, but internal code, data structures or exact formulas cannot be verified. | Inferable: Player dodge i-frames successfully evade active blade passes; internal i-frame tag logic UNKNOWN. |
| BOSS-HIT-010 | Direct/splash precedence | **OBSERVABLE** | Directly visible animation cue, spatial position or game event in 60fps footage. | Separation between direct melee impact and delayed explosive / geyser hazard. |
| BOSS-HIT-011 | Swept annulus | **PARTIAL** | External behavior or pattern is visible and inferable, but internal code, data structures or exact formulas cannot be verified. | Inferable: Sweep coverage geometry around boss; internal swept annulus math UNKNOWN. |
| BOSS-HIT-012 | Grab fail-safe | **OBSERVABLE** | Directly visible animation cue, spatial position or game event in 60fps footage. | Grab impalement sequence on contact vs whiff recovery animation frames. |
| BOSS-MOV-001 | Range-band policy | **PARTIAL** | External behavior or pattern is visible and inferable, but internal code, data structures or exact formulas cannot be verified. | Inferable: Distinct movesets observed at close, mid and far ranges; internal band threshold values UNKNOWN. |
| BOSS-MOV-002 | Combat positioning | **PARTIAL** | External behavior or pattern is visible and inferable, but internal code, data structures or exact formulas cannot be verified. | Inferable: Tactical backsteps and flanking repositioning; internal combat positioning AI UNKNOWN. |
| BOSS-MOV-003 | Movement commitment | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-MOV-004 | Wall-safe attacks | **PARTIAL** | External behavior or pattern is visible and inferable, but internal code, data structures or exact formulas cannot be verified. | Inferable: Attacks along arena perimeter do not cause boss to penetrate walls; raycast implementation UNKNOWN. |
| BOSS-MOV-005 | Arena-valid responses | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-MOV-006 | Arena/attack fit | **OBSERVABLE** | Directly visible animation cue, spatial position or game event in 60fps footage. | Boss arena boundary respect; containment inside Queen's Bedchamber bounds. |
| BOSS-PAC-001 | Explicit attack segments | **OBSERVABLE** | Directly visible animation cue, spatial position or game event in 60fps footage. | Discrete frame breakdown: windup frames, active blade frames, recovery frames. |
| BOSS-PAC-002 | Pressure variation | **OBSERVABLE** | Directly visible animation cue, spatial position or game event in 60fps footage. | Pacing cadence: frame intervals between fast daggers vs heavy hammer strikes. |
| BOSS-PAC-003 | Guaranteed openings | **OBSERVABLE** | Directly visible animation cue, spatial position or game event in 60fps footage. | Punish window frames following major commitments (hammer spin, spear charge whiff). |
| BOSS-PAC-004 | Conditional opening cues | **PARTIAL** | External behavior or pattern is visible and inferable, but internal code, data structures or exact formulas cannot be verified. | Inferable: Visual weapon lowering indicates end of threat; internal opening cue state machine UNKNOWN. |
| BOSS-PAC-005 | Punish-margin calculation | **PARTIAL** | External behavior or pattern is visible and inferable, but internal code, data structures or exact formulas cannot be verified. | Inferable: Player counter-attack window before boss next action; internal punish-margin formula UNKNOWN. |
| BOSS-PAC-006 | Neutral is purposeful | **OBSERVABLE** | Directly visible animation cue, spatial position or game event in 60fps footage. | Neutral spacing duration: frames boss spends circling/repositioning between attacks. |
| BOSS-DEF-001 | Separate health/reaction/posture | **OBSERVABLE** | Directly visible animation cue, spatial position or game event in 60fps footage. | Stagger animations, player damage numbers on screen, stance break event. |
| BOSS-DEF-002 | Posture regeneration | **PARTIAL** | External behavior or pattern is visible and inferable, but internal code, data structures or exact formulas cannot be verified. | Inferable: Stance break reset rate over time; internal posture regeneration math UNKNOWN. |
| BOSS-DEF-003 | Single stance break | **OBSERVABLE** | Directly visible animation cue, spatial position or game event in 60fps footage. | Stance break stagger duration and riposte opening window frames. |
| BOSS-DEF-004 | Windowed hyperarmor | **PARTIAL** | External behavior or pattern is visible and inferable, but internal code, data structures or exact formulas cannot be verified. | Inferable: Unflinching hyperarmor during heavy swings; internal hyperarmor threshold curve UNKNOWN. |
| BOSS-DEF-005 | Fair boss defense | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-PHS-001 | Phase rule set | **OBSERVABLE** | Directly visible animation cue, spatial position or game event in 60fps footage. | Timestamp of Phase 2 curse burst (~60% HP) and holy rain (~80% HP) visual cues. |
| BOSS-PHS-002 | Safe transition policy | **OBSERVABLE** | Directly visible animation cue, spatial position or game event in 60fps footage. | Safe transition pose duration, AOE knockback radius on curse burst. |
| BOSS-PHS-003 | Phase monotonicity | **PARTIAL** | External behavior or pattern is visible and inferable, but internal code, data structures or exact formulas cannot be verified. | Inferable: Boss never reverts from Phase 2 back to Phase 1; internal state variable UNKNOWN. |
| BOSS-PHS-004 | Fair heal punish | **OBSERVABLE** | Directly visible animation cue, spatial position or game event in 60fps footage. | Ranged punish latency when player drinks flask at distance. |
| BOSS-PHS-005 | Anti-cheese with counterplay | **PARTIAL** | External behavior or pattern is visible and inferable, but internal code, data structures or exact formulas cannot be verified. | Inferable: Aggressive gap closers answer ranged cheese; internal anti-cheese heuristic UNKNOWN. |
| BOSS-QA-001 | Runtime overlay | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-QA-002 | Structured event log | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-QA-003 | Reproducible scenarios | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-QA-004 | FPS and time-scale parity | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-QA-005 | Performance bounds | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |
| BOSS-QA-006 | Camera/readability | **OBSERVABLE** | Directly visible animation cue, spatial position or game event in 60fps footage. | Readability of telegraphs and hit cues under camera framing. |
| BOSS-QA-007 | Accessible feedback | **NOT OBSERVABLE** | Purely internal engine architecture, data structures, math formulas, private logs or QA tooling; completely invisible in video footage. | UNKNOWN -- Cannot be measured from screen recording. Must not be claimed. |

---

## 2. Concrete Measurements List (M-01 to M-12) Mapped to Real Framework Rows

Rather than using invented IDs, specific video measurement activities are identified as `M-01` through `M-12` and mapped to the real framework row IDs they evidence:

| Measurement ID | Measurement Activity | Target Observations & Timing Units | Mapped Framework Row IDs |
|---|---|---|---|
| **M-01** | Attack Windup & Telegraph | Exact frame counts from first windup pose to commitment / blade activation. | `BOSS-ANM-002`, `BOSS-ANM-003`, `BOSS-PAC-001` |
| **M-02** | Active Blade & Damage Window | Exact frame counts from first blade damage contact to end of damage arc. | `BOSS-HIT-001`, `BOSS-HIT-007`, `BOSS-PAC-001` |
| **M-03** | Recovery & Punish Windows | Frames from active finish to boss return to idle or next actionable attack. | `BOSS-PAC-001`, `BOSS-PAC-003`, `BOSS-COM-007`, `BOSS-PAC-005` |
| **M-04** | Tracking & Rotation Cap | Degrees/frames of yaw tracking during windup vs locked trajectory at release. | `BOSS-ANM-004` |
| **M-05** | Reach & Geometry by Weapon | Screen-space reach and sweep radius for dagger, sword, spear, hammer, tail. | `BOSS-AWR-003`, `BOSS-HIT-001`, `BOSS-MOV-001` |
| **M-06** | Directional / Rear Arc Reaction | Trigger frequency of tail sweep and turnaround attacks when player is behind. | `BOSS-AWR-004` |
| **M-07** | Contextual Combo Branches | Follow-up branches observed conditioned on player position (front vs flank vs rear). | `BOSS-COM-001`, `BOSS-COM-002`, `BOSS-COM-003`, `BOSS-COM-004`, `BOSS-COM-006` |
| **M-08** | Phase Transition Thresholds | Original video timestamps for holy rain (~80% HP) and curse burst (~60% HP). | `BOSS-PHS-001`, `BOSS-PHS-002`, `BOSS-PHS-003` |
| **M-09** | Environmental Hazards & AOE | Spatial layout and timing of falling swords and erupted bloodflame geysers. | `BOSS-HIT-010`, `BOSS-MOV-006` |
| **M-10** | Stance Break & Parry Counts | Count of parry successes required before critical break; stagger duration. | `BOSS-DEF-001`, `BOSS-DEF-003` |
| **M-11** | Grab Execution & Whiff | Travel distance and capture frames vs whiff recovery for bloodflame skewer. | `BOSS-HIT-012`, `BOSS-PAC-003` |
| **M-12** | Heal Punish Latency | Frame delay between player flask use and boss projectile/thrust response. | `BOSS-AWR-006`, `BOSS-SEL-009`, `BOSS-PHS-004` |

---

## 3. Frame-Timing Method (ffmpeg, 59.94 fps footage)

### 3a. Video Parameters and Time Zero
- **File:** `Elden Ring - Morgott, The Omen King Boss Fight.webm` (777 MB, AV1 3840x2160, ~59.94 fps, 335.5 s).
- **Combat Zero:** `01:45` original video time = `105.000` s. Per owner instruction (X-371/X-372), the first 105 seconds are cinematic and excluded from combat study.
- **Timestamp Conventions:**
  - `t_orig`: Original video timestamp in seconds (e.g. 112.438 s).
  - `t_combat`: Combat-relative timestamp in seconds (`t_combat = t_orig - 105.000 s`).
  - `frame_index`: 1-indexed frame count relative to extraction window start `t_extract_start`: `frame_index = round((t_orig - t_extract_start) * 59.94) + 1`.

### 3b. Extraction Command (ffmpeg)
Extract frames for a specified window scaled to 960px width for efficient storage and inspection:
```bash
# Example: extract 10 seconds starting at combat zero (t_orig = 105.0 s)
ffmpeg -ss 105.0 -t 10.0 \
       -i "Elden Ring - Morgott, The Omen King Boss Fight.webm" \
       -vf "fps=59.94,scale=960:-1" \
       -frame_pts 1 \
       "frames/morgott_c0_%05d.png"
```

### 3c. Event Marking Criteria
For each observed attack, six distinct boundary frames are identified:
1. **W (Windup start):** First frame where boss telegraphs attack (arm raises, weapon conjured, body coils).
2. **C (Commit):** Point of no return where trajectory is locked (typically ~50% into windup; marked APPROX if visual clue is subtle).
3. **A (Active first contact):** First frame where blade damage volume connects or intersects player capsule / health drops.
4. **E (Active end):** Last frame of the damaging blade sweep arc before dissipation or follow-through.
5. **R (Recovery start):** First frame where weapon momentum ceases and return-to-neutral animation begins.
6. **RE (Recovery end):** First frame where boss is fully actionable (starts new windup, turns, or enters neutral stance).

### 3d. Output Table Format & Consistent Arithmetic Example

**Extraction Window:** `t_extract_start = 105.000` s (combat zero), extracted to `frames/morgott_c0_%05d.png`.
Frame formula: `frame = round((t_orig - 105.000) * 59.94) + 1`.

| Move ID | t_W (orig / cbt) | t_A (orig / cbt) | t_E (orig / cbt) | t_RE (orig / cbt) | Windup Frames | Active Frames | Recovery Frames | Evidence Frame PNGs | Notes |
|---|---|---|---|---|---|---|---|---|---|
| `REF_CurvedSwordCombo_H1` | 112.438 / 7.438 | 112.738 / 7.738 | 112.855 / 7.855 | 113.322 / 8.322 | 18 frames (0.300 s) | 7 frames (0.117 s) | 28 frames (0.467 s) | `morgott_c0_00447.png`, `morgott_c0_00465.png`, `morgott_c0_00472.png`, `morgott_c0_00500.png` | Hit 1 of 3-hit string; clean frontal dodge; frame numbers exact to formula. |

**Arithmetic Verification:**
- $t_W = 112.438 \rightarrow t_{\text{combat}} = 7.438$ s $\rightarrow \text{round}(7.438 \times 59.94) + 1 = 446 + 1 = \mathbf{447}$.
- $t_A = 112.738 \rightarrow t_{\text{combat}} = 7.738$ s $\rightarrow \text{round}(7.738 \times 59.94) + 1 = 464 + 1 = \mathbf{465}$.
- $\text{Windup frames} = 465 - 447 = \mathbf{18\text{ frames}}$ ($18 / 59.94 = 0.3003$ s $\approx 0.300$ s).
- $t_E = 112.855 \rightarrow t_{\text{combat}} = 7.855$ s $\rightarrow \text{round}(7.855 \times 59.94) + 1 = 471 + 1 = \mathbf{472}$.
- $\text{Active frames} = 472 - 465 = \mathbf{7\text{ frames}}$ ($7 / 59.94 = 0.1168$ s $\approx 0.117$ s).
- $t_{RE} = 113.322 \rightarrow t_{\text{combat}} = 8.322$ s $\rightarrow \text{round}(8.322 \times 59.94) + 1 = 499 + 1 = \mathbf{500}$.
- $\text{Recovery frames} = 500 - 472 = \mathbf{28\text{ frames}}$ ($28 / 59.94 = 0.4671$ s $\approx 0.467$ s).

---

## 4. Observability Rule (from Roadmap)

> **Rule:** Observation only. No extraction of game files. Original names in shipped content stay out of shipped assets.

1. **Observation Only:** Measurements document visible and auditory cues in public video recordings. They are empirical observations of combat geometry, pacing and animation timings, not revelations of FromSoftware's proprietary source code or internal algorithms.
2. **No Game File Extraction:** No pak/asset unpackers, debug binaries, or memory hooks are used. All observations are derived exclusively from video frame analysis.
3. **Naming Hygiene:** Reference identifiers (such as `REF_CurvedSwordCombo_H1`, `Morgott`, or Elden Ring attack names) must **never** be used as asset names, C++ class names, or data table identifiers in our shipped Unreal project. Sevarog moves retain their own established naming conventions (`DA_Sevarog_AttackRowProof`, `SwingSlow`, etc.).
4. **Truthful Evidence Claims:** Unprovable internals are explicitly designated `NOT OBSERVABLE` and marked `UNKNOWN`. Inferences are clearly labeled as `PARTIAL` rather than proven facts.

---

## 5. First 8 Priority Clips to Measure

The 8 most frequent attack families from `Morgott_82_Point_Combat_Reference.md` are prioritized for initial measurement:

| Priority | Move Identifier | Attack Family | Evidenced Framework Rows | Specific Questions to Look For |
|---|---|---|---|---|
| **1** | `REF_CurvedSwordCombo_Chain1` | Curved sword 1-2-3 chain | `BOSS-ANM-002`, `BOSS-HIT-001`, `BOSS-PAC-001`, `BOSS-COM-001` | What is the frame cadence between swings 1, 2, and 3? Is there an interruptible gap between swing 2 and 3? Does the string terminate early if swing 1 whiffs? |
| **2** | `REF_DaggerFlurry_TapClose` | Conjured dagger close press | `BOSS-ANM-002`, `BOSS-HIT-001`, `BOSS-AWR-003`, `BOSS-PAC-002` | What is the maximum screen distance that triggers the dagger flurry? How many frames does the active dagger arc persist? Is there an identifiable audio cue on frame 1 of the summon? |
| **3** | `REF_SpearCharge_Full` | Spear throw + charge | `BOSS-ANM-002`, `BOSS-MOV-001`, `BOSS-COM-003`, `BOSS-PAC-003` | Does the spear charge have a fixed minimum travel distance, or does it stop on proximity? What is the frame delay before the follow-up sweep if the player rolls through vs away? |
| **4** | `REF_HammerSpin_Finisher` | Hammer jump/spin finisher | `BOSS-ANM-003`, `BOSS-HIT-001`, `BOSS-HIT-010`, `BOSS-PAC-003` | What is the total rotation arc (degrees)? Can the attack be rolled on reaction or does it require directional positioning? How many recovery frames are guaranteed after the ground slam? |
| **5** | `REF_TailSweep_RearCamp` | Tail sweep rear counter | `BOSS-AWR-004`, `BOSS-ANM-002`, `BOSS-PAC-001` | What rear angular threshold triggers the tail sweep? How many windup frames precede the sweep? Can the tail sweep be baited intentionally and punished? |
| **6** | `REF_HolySwordRain_Setup` | Holy sword rain (~80% HP) | `BOSS-PHS-001`, `BOSS-PHS-002`, `BOSS-HIT-010`, `BOSS-MOV-006` | What is the exact video timestamp of the first sword rain summon? How many frames does the boss spend in the summoning pose? How long do sword hazards persist on the ground? |
| **7** | `REF_BloodflameGrab_Skewer` | Bloodflame grab / skewer | `BOSS-HIT-012`, `BOSS-ANM-002`, `BOSS-PAC-003` | What is the forward travel distance of the thrust capsule? Exactly how many recovery frames occur on a whiff vs a successful impalement? |
| **8** | `REF_OmenCurseBurst_Phase2` | Omen curse burst (~60% HP) | `BOSS-PHS-001`, `BOSS-PHS-002`, `BOSS-HIT-010`, `BOSS-DEF-001` | What is the video timestamp when Morgott coughs and plants the sword? How many frames elapse from plant to burst? How many localized geysers erupt, and what is their duration? |

---

## 6. Verification and Acceptance

- Verified by `Docs/BossCombatReview/Execution/Antigravity/Reviews/test_reopen_d1_protocol.py`.
- All 82 requirement IDs verified against `Documentation/Boss/Morgott_82_Point_Combat_Reference/requirements.json` (0 missing, 0 duplicates).
- Stated classification counts (22 Observable + 27 Partial + 33 Not Observable = 82) verified programmatically.
- Offline only; strictly zero git commit until review and acceptance by Lead Claude.

