# W-A023: Historical Docs Archiving Deferral Record

**Date:** 2026-11-06  
**Author:** Antigravity (Lane A)  
**Status:** WAITING ON LEAD (Deferred to Post-RC)  
**Scope:** Formal record of Lead Claude's directive `[C-934]` deferring the physical migration (`git mv`) of the 694 superseded documentation files cataloged in `V-A082`.  
**Sources:** Documentation/TEAM_MAILBOX.md:24074, Documentation/Boss/V_A082_SUPERSEDED_DOCS_ARCHIVE_LIST.md:1-72, Documentation/PROJECT_STATE.md:1-470

---

## 1. Directive & Rationale

In directive [`[C-934]`](file:///c:/UnrealProject/OneBossFight/Documentation/TEAM_MAILBOX.md#L24074), Lead Claude evaluated the archiving proposal submitted in `V-A082` and issued the binding decision:

> *"DECISION on V-A082 / W-A023 (archive 694 superseded Boss docs): DEFERRED. Reason: C-820 no churn and C-883 file safety: moving 694 files breaks every link/line citation that points at them (CheckDocLineCounts and the link checker would need a full re-run and fixes), for no gameplay gain. Revisit after the release candidate tag; if done then: one tranche per commit, git mv only, link checker 0 broken before and after, and the list stays approved by me per tranche. Antigravity: mark W-A023 WAITING ON LEAD (deferred), take the next unblocked task."*

---

## 2. Risk Mitigation

Executing mass file moves (`git mv 694 files`) during active release stabilization introduces severe risks:
1. **Broken Link Churn:** Hundreds of historical audit files cross-reference exact paths under `Documentation/Boss/`; moving them would immediately fail `check_doc_links.py`.
2. **Git Diff Clutter:** Staging 694 file moves bloats commit histories and obscures critical code/test reviews.
3. **Zero Runtime Gain:** Markdown files are not cooked into packaged game builds; archiving yields 0 ms and 0 byte benefit in Shipping.

---

## 3. Post-RC Execution Plan

When authorized post-release candidate tag:
- The migration will proceed strictly in the 5 tranches defined in `V_A082:20-58`.
- Executed using `git mv` only (one commit per tranche).
- Verified with `python Scripts/Tools/check_doc_links.py` (`broken_links=0`) before and after each tranche.

---

## 4. Status

- **Task Status:** **WAITING ON LEAD (DEFERRED)**
- **Next Task:** Re-verify living `PROJECT_STATE.md` structure against recovery copies (`W-A024`).
