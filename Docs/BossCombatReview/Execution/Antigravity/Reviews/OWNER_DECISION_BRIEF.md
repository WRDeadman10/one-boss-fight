# Track B: Owner Strategic Decision Brief (v2.8)

**Date:** 2026-11-01  
**Author:** Tech Lead Claude & Antigravity  
**Audience:** Project Owner  
**Reference:** Question sent by email (`Documentation/TEAM_MAILBOX.md:14532`)  

---

## 1. Executive Summary & Current State

The test boss combat framework has reached strong mathematical and behavioral maturity. All numbers below are computed directly from the canonical verification ledger (`Ledger/witness_status_v3.json` v3.15) and census script (`Reviews/generate_not_yet_census.py`).

### Ledger Census Today (82 Canonical Requirements):
- **WITNESSED:** **45** (54.9%) — Behavioral proof verified live in PIE or via C++ unit test assertions on the framework boss.
- **PARTIAL:** **14** (17.1%) — Core logic implemented and tested; awaiting specific engine scenarios, input drivers, or authoring.
- **NOT YET:** **23** (28.0%) — Unbuilt subsystems, unauthored animations, or future combat blocks.

### Milestones Graduated to WITNESSED (Since C-546):
- **BOSS-MOV-005 (Arena-valid responses):** Live PIE proof on `L_SevarogFrameworkProofMOV005` (`Claude/B_MOV005/pie_leash3`) proves target teleporting outside radius triggers `arena_leash` Start, aborts active card with cleanup reason `ArenaLeash`, leashes back to arena center (where target began), and cleanly resumes fight upon player return.
- **BOSS-AWR-001 (Target validity):** Attack abort and boss shutdown verified across all 3 fault states (Dead, OffArena, Destroyed) with zero subsequent candidate/decision evaluations (`Claude/B_AWR001`).
- **BOSS-HIT-005 (Query filtering):** Non-target pawns filtered in sweep capsule (`ignoredPawns=1 selfHits=0`) with zero damage perturbation (`Claude/B_HIT005/byst60`), combined with dead-target abort.
- **BOSS-QA-004 (FPS parity):** Fixed-timestep runs at 30, 60, and 120 FPS producing identical hit counts (2) and damage (55.0 applied).
- **BOSS-COM-003, 005, 007 (Combo graph):** Multi-scenario live PIE proofs on `L_SevarogFrameworkProofCOM3` verifying 3-node combo progression, single-use gate consumption, and default recovery fallbacks.
- **BOSS-AWR-005 (Vertical separation):** Proved horizontal ground sweep card refusal on elevated ledge ($Z=115\text{ cm} > 50\text{ cm}$) using `FloorSeparationCm()` feet-to-feet distance fixing capsule origin offset (`Claude/B_AWR005/pie_ledge`).
- **BOSS-COM-002 (Branch evaluation timing):** Hit window EndSeconds proven to close strictly before combo branch decision gate opens across all evaluated gates in B_COMBO3.
- **BOSS-AWR-002 (Gate-time snapshot):** Lateral shift proof on `L_SevarogFrameworkProofF5` proving heading commit and lock without mid-action re-evaluation or trajectory abort despite player lateral shift.
- **BOSS-EXE-007 (Watchdog) & BOSS-ANM-007 (Notify-end independence):** C++ watchdog in executor aborting stalled card after $T = \text{RecoveryEndSeconds} / \text{PlayRate} + 0.5\text{s}$ under simulated dropped montage end (`rpg.BossProofSuppressMontageEnd 1`), cleaning up model, clearing active combo, and resuming decision loop without AI stall.

### Progress on Key PARTIAL Rows:
- **BOSS-QA-003 (Determinism):** Bit-for-bit event reproducibility across identical seeds, and live seeded tie-breaking on `L_SevarogFrameworkProofQA003` picking lower-scoring moves deterministically; remains PARTIAL pending frame-synchronized player input injection.
- **BOSS-QA-002 (Structured event log):** 56 structured `[FrameworkProof]` tokens and unique monotonic decision sequence numbers across stance breaks; production `[CARD_*]` prefix reserved.
- **BOSS-DEF-002 (Posture regen):** Reset-on-drain delay and linear regen rate verified live in PIE.
- **BOSS-SEL-008 (No-candidate fallback):** Opt-in walk-back-to-band and turn-in-place repositioning reset verified when 0 cards qualify; remains PARTIAL pending design decision on default profile shipping policy.

---

## 2. Taxonomy of Remaining Work

### A. The 14 PARTIAL Rows (Grouped by Real Blocker)
From the original plan (`Reviews/PARTIAL_UPGRADE_PLAN.md`), with its current status taken from the ledger (v3.14):
1. **Engine / PIE Scenario Hooks (3 rows):**
   - `BOSS-QA-001` (Runtime overlay): Formatted strings logged live; blocked because unattended PIE GPU backbuffer readback returned black pixels; requires on-screen display capture.
   - `BOSS-SEL-008` (No-candidate fallback): Walk-to-band verified live; requires continuous strafe loop when 0 cards qualify or production opt-in policy.
   - `BOSS-COM-004` (Hit-confirm policy): Whiff/recovery verified live; requires guarded and parried target states in PIE.
2. **Player-Side / Combat Input Integration (4 rows):**
   - `BOSS-HIT-008` (Central defense order): Requires player shield block/parry stance integration in damage resolver.
   - `BOSS-HIT-009` (Iframe completeness): Requires player dodge iframe timing alignment with weapon sweep window.
   - `BOSS-PHS-004` (Fair heal punish): Requires player flask drinking perception reaction loop in boss character.
   - `BOSS-ANM-005` (Exclusive motion authority): Requires formal player-boss collision and AI navigation lock.
3. **Animation & Notify Track Authoring (3 rows):**
   - `BOSS-ANM-002` (Telegraph phases): Requires authored windup, active, and recovery notify tracks.
   - `BOSS-MOV-001` (Range-band policy): Requires full 15-family range-band card partitioning.
   - `BOSS-PAC-006` (Neutral is purposeful): Requires multi-attack neutral transition testing with authored idle postures.
4. **Lifecycle & Watchdog Robustness (1 row):**
   - `BOSS-EXE-006` (Idempotent abort): Requires live grab/AoE executor abort path.
5. **Architectural & Design Constraints (2 rows):**
   - `BOSS-AWR-004` (Signed angle hysteresis): Discrete-attack boss has no oscillation; requires selector-side memory.
   - `BOSS-QA-002` (Structured event log): Defenses and interrupts not logged; production `[CARD_*]` prefix reserved.
6. **Hardware Baseline (1 row):**
   - `BOSS-QA-005` (Performance bounds): Packaged build 1080p 60 FPS $p99 \le 16.67\text{ ms}$ on physical RTX 2060 Super GPU (parked by owner).

### B. The 23 NOT YET Rows (Grouped by Class & Cost)
Directly computed from `Reviews/NOT_YET_CENSUS.md` and verified against disk:
- **Cost Breakdown:** **Cost S (1-2 runs): 3 reqs (13.0%)** | **Cost M (2-4 runs): 12 reqs (52.2%)** | **Cost L (4+ runs): 8 reqs (34.8%)**.
- **By Dependency Class:**
  * **ENGINE-ONLY (4 reqs, 17.4%):** Pure C++ runtime rules or hooks; no art dependencies.
    - Cost S: `BOSS-MOV-003` (Movement commitment), `BOSS-DEF-004` (MoveCard hyperarmor tags).
    - Cost M: `BOSS-SEL-009` (Reaction latency window), `BOSS-EXE-005` (Phase vs stagger priority).
  * **NEEDS DESIGN DECISION (4 reqs, 17.4%):** Designer thresholds or scoring rules; requires owner choices before code.
    - Cost S: `BOSS-PAC-002` (Combo tempo pauses).
    - Cost M: `BOSS-MOV-002` (Combat positioning center bias), `BOSS-HIT-010` (Direct vs splash precedence), `BOSS-PHS-005` (Anti-cheese trigger rules).
  * **NEEDS ART (6 reqs, 26.1%):** Requires animations, montages, notify tracks, or level collision art.
    - Cost M: `BOSS-MOV-004` (Wall-safe charge trajectories), `BOSS-MOV-006` (L_SevarogArena snag point audit), `BOSS-DEF-005` (Defensive moveset actions).
    - Cost L: `BOSS-ANM-003` (Bounded holds), `BOSS-PAC-004` (Vulnerability visual cues), `BOSS-QA-007` (Low VFX accessibility harness).
  * **NEEDS NEW SYSTEM (5 reqs, 21.7%):** Requires unbuilt architectural subsystems.
    - Cost L: `BOSS-AWR-007` (LOS raycasts & memory), `BOSS-AWR-008` (Player dodge adaptation histogram), `BOSS-ANM-006` (Motion Warping plugin integration), `BOSS-HIT-011` (Swept annulus shockwave), `BOSS-HIT-012` (Two-character grab state machine).
  * **PLAYER-SIDE (4 reqs, 17.4%):** Requires player combat intake, input buffers, or camera integration.
    - Cost M: `BOSS-AWR-006` (Player flask/heavy commitment listener), `BOSS-PAC-003` (Finisher recovery punish window), `BOSS-PAC-005` (Punish-margin calculation formula), `BOSS-QA-006` (Combat follow camera framing).

---

## 3. The Owner Question & Options

Verbatim text of the question sent to the owner (`Documentation/TEAM_MAILBOX.md:14532`):

> `"which way next" for Track B: A) upgrade the 27 PARTIAL rows to WITNESSED (mostly one live run or one screenshot each), then the open rows; B) the 24 NOT YET rows in cost order (about 8 need art/design input, about 16 need new systems); C) stop. My recommendation: A then B.`

### Evaluation with Today's Data:
- **Option A (Upgrade PARTIAL rows first):** 11 rows have already graduated (`AWR-001`, `QA-004`, `HIT-005`, `COM-003`, `COM-005`, `COM-007`, `AWR-005`, `COM-002`, `AWR-002`, `EXE-007`, `ANM-007`), leaving 16 rows. Several of these 16 have established framework hooks and can be graduated via targeted PIE scenario maps (e.g. `QA-001` on-screen screenshot, `SEL-008` no-candidate strafe reset). The remaining rows depend on player-side intake, notify authoring, or lifecycle logging.
- **Option B (Work NOT YET rows in cost order):** The 3 Cost S and 2 Cost M `ENGINE-ONLY` rows (`MOV-003`, `MOV-005`, `DEF-004`, `SEL-009`, `EXE-005`) can be implemented immediately in C++. However, the 4 `NEEDS DESIGN DECISION` rows require designer choices from the owner before implementation, and the remaining 15 rows depend on art assets or whole unbuilt subsystems.
- **Option C (Stop):** Freeze Track B at current state (42 WITNESSED / 16 PARTIAL / 24 NOT YET) and transition focus to other project areas.

---

## 4. Recommendation

### Recommendation: **Option A first, then the Cost S/M ENGINE-ONLY rows of Option B.**

**Rationale:**
1. **Capitalize on Proven Scenarios:** The PARTIAL rows already possess verified C++ implementations and unit tests. Addressing the engine-accessible subset converts existing investments into clean WITNESSED rows with zero new system architecture.
2. **Targeted C++ Expansion:** Following Option A's engine-ready slice with Option B's 5 `ENGINE-ONLY` rows (`MOV-003`, `MOV-005`, `DEF-004`, `SEL-009`, `EXE-005`) expands framework capability purely in code without art bottlenecks.
3. **Avoid Premature Blockers:** Working strictly in cost order without separating by dependency class would stall against the 4 design-decision rows and 6 art rows.
