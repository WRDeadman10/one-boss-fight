# AG-8: Adversarial Review of Claude's Technical Evidence and Baseline Specifications

**Document ID:** `AG8_ADVERSARIAL_REVIEW` (Rev 01)  
**Date:** 2026-10-25  
**Author:** Antigravity (Accountable Visual & Technical Animation Investigator)  
**Target Author / Subject:** Claude (Technical Lead & Author of E-001 through E-008, STEP0, and STEP1 Specs)  
**Addressed to:** Claude, Codex GPT-6 Astra, Project Owner  
**Authority & Mandate:** Task AG-8 of Work Order 02 (`ANTIGRAVITY_WORK_ORDER_02.md`). Strict adversarial audit: finding at least five concrete defects, wrong numbers, unsupported claims, or instances where text exceeds underlying data.

---

## 1. Executive Summary

This adversarial audit inspected Claude's evidence files (`E-002` through `E-008`), `STEP0_BASELINE.md`, and `STEP1_SPEC_v3_AMENDMENTS.md`, cross-referencing them against raw exports in `Docs/BossCombatReview/Execution/Claude/Evidence/exports/` and engine source code.

Six verified defects have been identified where Claude's text:
1. Retains contradictory statements in document bodies that directly dispute Revision 2 correction headers.
2. Asserts mathematically false frame calculations.
3. Grossly misrepresents parser failure rates by retaining obsolete fractions.
4. Leaves obsolete behavior invariants in governing baseline tables.
5. Incompletely documents harness contamination variables.

---

## 2. Adversarial Findings Register

```
+--------+---------------------------------------+--------------------+----------------------------------------+
| Item   | File & Line Reference                 | Category           | Summary of Defect / Inconsistency      |
+--------+---------------------------------------+--------------------+----------------------------------------+
| **D1** | `E-002` Line 67 vs Line 3             | Contradiction      | Sprint attack phase 2 trigger error    |
| **D2** | `E-008` Line 11 vs Line 3             | Retained Error     | Withdrawn +194 deg angle retained      |
| **D3** | `E-007` Line 7 vs Line 3              | Math Error         | 0.07s asserted as < 1 frame at 20 fps  |
| **D4** | `STEP0_BASELINE` Line 16 vs Line 36   | Policy Conflict    | Obsolete "10 of 11 reproduce" mandate  |
| **D5** | `E-006` Line 11 vs Line 3             | Data Distortion    | 48.6% unresolved called "about a 1/4"  |
| **D6** | `STEP0_BASELINE` Line 34 vs E-007/008 | Incomplete Record  | Omission of WakeClip in contamination  |
+--------+---------------------------------------+--------------------+----------------------------------------+
```

---

### DEFECT 1: Uncorrected Contradiction on Sprint Attack Eligibility in Phase Two

- **File & Line Anchors:** `Docs/BossCombatReview/Execution/Claude/Evidence/E-002_live_route_and_attack_inventory.md`, Line 67 vs Line 3 (item 5).
- **The Defect:** In Revision 2 of `E-002` (Line 3), Claude explicitly acknowledges:
  > `(5) "Sprint runs only while Leap is on cooldown" is wrong in two ways: Leap can also be rejected by the ability-system block tag (phase one) or by any Can Activate Ability? predicate, and in phase two Sprint can follow any Leap rejection;`
  However, in the body of `E-002` at **Line 67** (Addendum E-002-08), Claude still writes:
  > `in phase two Leap is tried first and Sprint only runs while Leap is on its 15 s cooldown.`
- **Check Performed:** Read and diffed `E-002` line 3 against line 67. Cross-referenced with raw graph export `graph_ASC_GetAbilitiesByAllTags_and_TryActivate.txt` and `graph_GA_EnemyMeleeAttack_CanActivate.txt`.
- **Consequence:** The body text was never patched when Revision 2 was drafted. A reader or automated parser reading Addendum 8 receives an incorrect gating rule: Sprint can trigger in Phase 2 whenever Leap fails *any* predicate (combat target invalid, distance out of range, tag blocked, or cooldown), NOT solely when Leap is on its 15s cooldown.

---

### DEFECT 2: Retained Withdrawn Angular Discrepancy Figure (+194°) in Body

- **File & Line Anchors:** `Docs/BossCombatReview/Execution/Claude/Evidence/E-008_CAP02_A4_query_vs_visible_blade.md`, Line 11 vs Line 3 (item 3).
- **The Defect:** In Revision 2 of `E-008` (Line 3), Claude notes:
  > `(3) With shortest circular deltas the sampled angular differences are about -51, -51, -69, -88, -105, -114, +170, +146, -166, +174, +125, +83 degrees: absolute shortest error about 51 to 174 degrees (the earlier "194" is withdrawn);`
  Yet in the body of `E-008` at **Line 11**, Claude's text still asserts:
  > `the difference to the query angle is -51 to -114 degrees at the start and +83 to +194 degrees later`
- **Check Performed:** Evaluated shortest signed angular deltas across the 12 active ticks in `exports/a4_geometry_probe_v2_2026-10-25.txt`. The maximum shortest circular delta is indeed $+174.0^\circ$ (at tick 0.831s: query angle $-41.8^\circ$, blade angle $+132.2^\circ$, delta $174.0^\circ$). The $+194^\circ$ was an artifact of unsigned linear subtraction without modulo $360^\circ$ wrapping.
- **Consequence:** Claude formally withdrew "194" in his header notes, but left the uncorrected $+194^\circ$ number inside the body findings, presenting contradictory data within the same document.

---

### DEFECT 3: Mathematical Contradiction on Sub-Frame Durations at 20 FPS

- **File & Line Anchors:** `Docs/BossCombatReview/Execution/Claude/Evidence/E-007_CAP01_A5_release_timing.md`, Line 7 vs Line 3.
- **The Defect:** In the Revision 2 header note (Line 3), Claude writes:
  > `At 20 fps one frame is 0.05 s, so 0.05 to 0.07 s is 1 to 1.4 frames, NOT "smaller than one frame".`
  However, in the body of `E-007` at **Line 7 (item 4)**, the uncorrected text remains:
  > `(4) the 0.05 to 0.07 s is smaller than one frame at 20 fps, so readability impact is a feel question for the owner, not a measured defect.`
- **Check Performed:** Basic arithmetic: At $20\text{ fps}$, frame duration is $\Delta t = 1.0 / 20.0 = 0.050\text{ s}$ ($50\text{ ms}$). An observed duration of $0.070\text{ s}$ equals $0.070 / 0.050 = 1.40\text{ frames}$.
- **Consequence:** Line 7 literally asserts that $0.07\text{ s}$ is "smaller than one frame at 20 fps", which is mathematically false. The header corrected it, but failed to remove the false claim from the body, leaving the document internally self-contradictory.

---

### DEFECT 4: Obsolete Early-Stop Invariant Mandate Retained in Behavior Table

- **File & Line Anchors:** `Docs/BossCombatReview/Execution/Claude/DD1/STEP0_BASELINE.md`, Line 16 vs Line 36.
- **The Defect:** In Section 2 ("Behaviours DD-1 must reproduce", Line 16), the governing table specifies:
  > `A2 slam stopped early (10 of 11 instances; first slam at 0.03 to 0.06 s in 5 of 6 fights), ability left active over 1.4 s | E-005 | reproduce; shadow comparison must show the same stops`
  However, in Supplement 1 at **Line 36** of the same file, Claude states:
  > `Corrections to the behaviour table above (Codex D06B): A2: nine Windup stops, one Active stop (1.99 s, window 1.93 to 2.11), one Recovery replacement (2.80 s): mechanism and sampled outcomes are preserved, NOT a statistical 10 of 11 invariant... DD-1 observes these symptoms through the shadow comparison and never reproduces them by implementing cancellation.`
- **Check Performed:** Read and compared Section 2 table (line 16) with Supplement 1 (line 36).
- **Consequence:** The primary governing table of `STEP0_BASELINE.md` still commands that DD-1 must "reproduce" a "10 of 11" early stop count. Leaving this obsolete directive in the primary table creates a direct conflict with Supplement 1, which states that DD-1 merely observes symptoms via shadow comparisons and must never implement cancellation to force parity.

---

### DEFECT 5: Unresolved Edge Percentage Understated by Half (48.6% called "about a quarter")

- **File & Line Anchors:** `Docs/BossCombatReview/Execution/Claude/Evidence/E-006_graph_edges_and_pack_adapter.md`, Line 11 vs Line 3 (item 1).
- **The Defect:** In Revision 2 (Line 3, item 1), Claude states:
  > `(1) Unresolved edge endpoints are 34 of 70 printed edges (13 of 19, 10 of 25, 11 of 26), not "about a quarter".`
  Yet in the body of `E-006` at **Line 11**, the text still asserts:
  > `so about a quarter of the edges end in ?.<pin id> (target node not resolved)`
- **Check Performed:** Arithmetic verification of edge counts from `exports/edges_*.txt`:
  * `edges_T_TryActivate_ActivateAbilities.txt`: 13 unresolved of 19 total edges ($68.4\%$).
  * `edges_GA_EnemyMeleeAttack_CanActivate.txt`: 10 unresolved of 25 total edges ($40.0\%$).
  * `edges_GA_MeleeBase_CanActivate.txt`: 11 unresolved of 26 total edges ($42.3\%$).
  * Total: $13 + 10 + 11 = 34$ unresolved out of $19 + 25 + 26 = 70$ total edges.
  * Ratio: $34 / 70 = \mathbf{48.57\%}$.
- **Consequence:** Line 11 understates the failure rate of the edge parser by almost a factor of two ($25\%$ vs actual $48.6\%$). Calling half the graph "about a quarter" distorts the reliability of the recovered Blueprint logic.

---

### DEFECT 6: Incomplete Documentation of Harness Contamination Variables

- **File & Line Anchors:** `Docs/BossCombatReview/Execution/Claude/DD1/STEP0_BASELINE.md`, Line 34 vs `E-007:5` & `E-008:5`.
- **The Defect:** In explaining why the first baseline gate run failed (`STEP0_BASELINE.md:34`), Claude writes:
  > `Before the run I left two process-wide settings changed in the editor: rpg.CloseTelegraph 0 (the A5 and A4 probe runs set it; pie_telegraph T0 expects the default 0.4) and the log verbosity Log LogAnimMontage VeryVerbose...`
  This statement asserts that *two* process-wide settings were left changed. However, cross-referencing `E-007` line 5 and `E-008` line 5:
  > `config: wake 0, telegraph 0, legend 0 as in E-007; window restored.`
  The probe `probes/p0_set_cvars.py` explicitly sets **three** console variables: `rpg.WakeClip 0`, `rpg.CloseTelegraph 0`, and `rpg.Legend 0`.
- **Check Performed:** Read `probes/p0_set_cvars.py` source code. Lines 15–18 execute:
  `unreal.SystemLibrary.execute_console_command(None, "rpg.WakeClip 0")`
  `unreal.SystemLibrary.execute_console_command(None, "rpg.CloseTelegraph 0")`
  `unreal.SystemLibrary.execute_console_command(None, "rpg.Legend 0")`
- **Consequence:** Claude omitted `rpg.WakeClip 0` from his contamination confession. `rpg.WakeClip` defaults to `1` in standard runs (e.g. `A2 defaults` in `E-004:13`). Leaving `rpg.WakeClip 0` active alters trial initialization poses, which may have contributed directly to the reset-state failures in `pie_soak` and `pie_player_death_reset`.

---

## 3. Evidence and Limits

| Claim / Field | Source File / Anchor | Kind | Status / Limit |
| :--- | :--- | :--- | :--- |
| Defect 1: Sprint Gating | `E-002.md:3` vs `E-002.md:67` | Textual Analysis | Direct textual contradiction verified |
| Defect 2: Angular Discrepancy | `E-008.md:3` vs `E-008.md:11` | Math / Textual Analysis | Verified against raw probe export |
| Defect 3: Frame Calculation | `E-007.md:3` vs `E-007.md:7` | Arithmetic Proof | $0.07\text{ s} / 0.05\text{ s} = 1.4\text{ frames} > 1$ frame |
| Defect 4: Baseline Table Mandate | `STEP0_BASELINE.md:16` vs `:36` | Textual Analysis | Contradictory mandate verified |
| Defect 5: Unresolved Edge Ratio | `E-006.md:3` vs `E-006.md:11` | Statistical Calculation | $34 / 70 = 48.57\% \approx 49\%$ |
| Defect 6: Cvar Contamination | `STEP0_BASELINE.md:34` vs `p0_set_cvars.py` | Source Inspection | Omission of `rpg.WakeClip 0` confirmed |

### What Could NOT Be Verified Offline:
1. Whether `rpg.WakeClip 0` was specifically the mechanical cause of the `pie_soak` failures cannot be proven without running the test in the editor with WakeClip toggled.
2. Exact runtime state machine transitions for the remaining 34 unresolved Blueprint edges cannot be evaluated without interactive Blueprint debugger execution.
