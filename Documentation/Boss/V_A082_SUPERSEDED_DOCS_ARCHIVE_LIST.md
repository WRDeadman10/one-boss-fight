# V-A082: Superseded Boss Docs Archive Proposal & Manifest

**Date:** 2026-11-06  
**Author:** Antigravity (Lane A)  
**Status:** Proposal (Awaiting Lead Claude Approval per `QUEUE_V.md:211`)  
**Scope:** Inventory and structured migration plan for superseded historical documents currently residing in [`Documentation/Boss/`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/).
**Sources:** Documentation/Boss/ [Disk inventory scan of 826 files]

---

## 1. Context & Motivation

The [`Documentation/Boss/`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/) directory currently houses 826 markdown documents and CSV artifacts. Over 690 of these files represent completed historical audit records and verification notes from concluded queues (Queue D, Queue E, Queue R, Queue S). While these documents preserve crucial development audit trails, their presence at the top level creates directory clutter, increases IDE index overhead, and complicates navigation for active work in Queues V and W.

Per task definition `V-A082` and subsequent execution gate `W-A023`, **no files are moved during this task**. This document provides the formal index, categorization, target structure, and link verification plan for Lead review and sign-off.

---

## 2. Inventory & Classification

Analysis of the 826 files in `Documentation/Boss/` yields five primary superseded candidate tranches:

| Tranche | Pattern / Namespace | File Count | Purpose / Content Description | Proposed Archive Destination |
|---|---|---|---|---|
| **Tranche 1: Queue D** | `*_D[0-9]*.md` (excluding `D1`, `D2`, `D5`) | 277 files | Phase 1 Boss combat and framework audits (D001–D200) | `Documentation/Boss/Archive/Queue_D/` |
| **Tranche 2: Queue S** | `*_S[0-9]*.md`, `S[0-9]*_*.md` | 198 files | Shipping configuration, gate reviews, and platform tests | `Documentation/Boss/Archive/Queue_S/` |
| **Tranche 3: Queue R** | `*_R[0-9]*.md`, `R[0-9]*_*.md` | 185 files | Refactoring audits, test mutations, and timing profiles | `Documentation/Boss/Archive/Queue_R/` |
| **Tranche 4: Queue E** | `E1[0-9][0-9]_*.md`, `E2[0-9][0-9]_*.md` | 30 files | Early encounter opt-in and decision records (E126–E200) | `Documentation/Boss/Archive/Queue_E/` |
| **Tranche 5: Early HowTos** | `C1_*.md` .. `C4_*.md` | 4 files | Superseded early tutorials (replaced by newcomer guide) | `Documentation/Boss/Archive/EarlyGuides/` |
| **Active Retained** | `U_*`, `V_*`, `W_*`, `QUEUE_*`, `D5_*` | 132 files | Active queue tasks, current benchmarks, and living D5 tracks | *Retained at top-level `Documentation/Boss/`* |
| **Total** | | **826 files** | | **694 proposed for archive / 132 retained** |

*(Source: Disk scan of `Documentation/Boss/*.md`, 2026-11-06).*

---

## 3. Migration Plan & Safety Safeguards

### 3.1 Strict Tracked `git mv` Only
To avoid the untracked loss issue documented in [`Documentation/KNOWN_ISSUES.md:301`](file:///c:/UnrealProject/OneBossFight/Documentation/KNOWN_ISSUES.md#L301) (`KI-188`), all file moves must:
1. Use explicit `git mv <source> <target>`.
2. Ensure destination folders under `Documentation/Boss/Archive/` are **not** matched by `.gitignore`.
3. Never invoke raw shell `Remove-Item` or delete untracked files.

### 3.2 Link Safety Guard (`check_doc_links.py`)
Moving 694 files risks breaking relative markdown references in `Documentation/DECISIONS.md`, `Documentation/TASKS.md`, and `Documentation/TEST_PLAN.md`.
- Before executing `git mv` in `W-A023`, a path rewrite mapping script will run over living documents to update links from `Documentation/Boss/<File>` to `Documentation/Boss/Archive/<Tranche>/<File>`.
- The migration will be gated on `python Scripts/Tools/check_doc_links.py` returning `broken_links=0`.

---

## 4. Sample Proposed Migration Manifest

A representative sample of the migration mapping:

```
Documentation/Boss/ADAPTIVE_AGGRESSION_EXPECTED_D173.md  -> Documentation/Boss/Archive/Queue_D/ADAPTIVE_AGGRESSION_EXPECTED_D173.md
Documentation/Boss/ARENA_LEASH_BOUNDARY_PROOF_AUDIT_D40.md -> Documentation/Boss/Archive/Queue_D/ARENA_LEASH_BOUNDARY_PROOF_AUDIT_D40.md
Documentation/Boss/AUTOMATION_DETERMINISM_AUDIT_D83.md   -> Documentation/Boss/Archive/Queue_D/AUTOMATION_DETERMINISM_AUDIT_D83.md
Documentation/Boss/ANTICHEESE_PROOF_EXPECTED_S119.md    -> Documentation/Boss/Archive/Queue_S/ANTICHEESE_PROOF_EXPECTED_S119.md
Documentation/Boss/CLI_INPUT_VALIDATION_AUDIT_S173.md   -> Documentation/Boss/Archive/Queue_S/CLI_INPUT_VALIDATION_AUDIT_S173.md
Documentation/Boss/TEST_MUTATION_AUDIT_R66_70.md        -> Documentation/Boss/Archive/Queue_R/TEST_MUTATION_AUDIT_R66_70.md
Documentation/Boss/E126_DECISION_AUDIT.md               -> Documentation/Boss/Archive/Queue_E/E126_DECISION_AUDIT.md
Documentation/Boss/C1_NEW_BOSS_HOWTO.md                 -> Documentation/Boss/Archive/EarlyGuides/C1_NEW_BOSS_HOWTO.md
```

---

## 5. Disposition & Recommendation

- **Recommendation:** Maintain the 132 active files (`U_*`, `V_*`, `W_*`, living specifications) in root `Documentation/Boss/`.
- **Action Required:** Await explicit Lead Claude review and approval in mailbox before executing the `git mv` tranche in Queue W (`W-A023`).
