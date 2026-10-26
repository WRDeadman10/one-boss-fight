# Task board: Codex, Antigravity, Claude (created 2026-10-26 by Claude at the owner's request)

Owner directive (chat, 2026-10-26): Codex and Antigravity are free; Claude concentrates on REVIEW, VALIDATION and TESTING; lay out the work for both; keep a watch on the mailbox and make Codex and Antigravity watch it too, so the three talk to each other and nobody sits waiting for somebody.

## 0. Rules of engagement (read once, then work)

1. **Run your own mailbox watch.** Codex: `powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\MailboxNext.ps1 -Me X -SeenCount <n> -Seconds 570`; Antigravity: the same with `-Me A`; first call without `-SeenCount` prints your count. Exit 0 = new messages, exit 2 = nothing yet: take your NEXT TASK from your queue, never wait on a timeout. Re-run the watch after every package report.
2. **Talk directly.** Content question for the other agent? Post an X-n / A-n addressed to them ("Codex ->" or "Antigravity ->") with Claude in copy. Do not route routine questions through Claude; Claude only decides disputes, reviews, builds and runs.
3. **Never idle.** After each package: post the report, start the next task of your queue. A real blocker is only an owner decision or a fact only the editor can give: post it once (DECISION NEEDED / EDITOR NEEDED) and continue with the next task.
4. **Evidence discipline:** every number cites a file and hash or an evidence id; a claim from a mailbox post is not evidence; DONE needs a reproducible check; say NOT BUILT / NOT RUN where true. Peer reviews: at least five concrete findings with file:line, or the list of clean checks.
5. **Boundaries unchanged:** no pack asset edits, no live `Source/` edit except where a task says so, no commit or push, G-4 and G-5 denied, all 83 requirements required, DD-1 changes no behaviour of the three shipped builds, one editor owner (Claude).
6. **Reports:** one mailbox post per package, usual format (TASK, STATUS, FINDINGS, DECISION NEEDED, NEXT ACTION, VALIDATION). Claude posts a PROGRESS block (done / in progress / next / blocked, counts) into `PHASE_STATUS.md` and the mailbox after every review cycle.

## 1. State today (2026-10-26)

DD-1 step 0 closed. DD-1 step 1 built, 41/41 automation, full gate 40/40 (data epoch), catalog assets exist, scratch route (a) proven (E-010), pack reuse exports E-009. NOT done: Codex acceptance of step 1, owner acceptance, cold packaged load of the catalog folder, steps 2 and 3 (drafts only, in `Codex/Drafts/`, not promoted), P0 report, P1 to P8.

## 2. CODEX queue (X-T1 to X-T9, in this order)

| ID | Task | Deliverable | Done when |
|---|---|---|---|
| X-T1 | WP-14: independent review of Claude's fixes (`RPGBossDormantWake.cpp` WakeClip stop, Publish braces) and the WP-15 diff (`Describe`, `GetBuildName`, removed `Chosen`, `Catalog.Resolution` test) | findings with file:line or "clean" | posted |
| X-T2 | Formal acceptance review of step 1 against spec v2 + v3 amendments, F5/F6/F7 against `Claude/DD1/preimages/` | `Codex/STEP1_ACCEPTANCE_REVIEW.md`: a verdict per spec line, overall ACCEPT / ACCEPT WITH CONDITIONS / REJECT | file + X-n |
| X-T3 | Review `Source/OneBossFight/Scratch/RPGScratchRouteA.*` and `Claude/Evidence/E-010_scratch_route_a.md`: what the evidence supports and does not, compile and design risk | findings | posted |
| X-T4 | WP-13: complete Boss01 field-source manifest (every constant/tunable the boss reads, source file:line, value kind, owning definition field, consumer, parity check; class HYDRATABLE_NOW / NEEDS_SEAM / NEEDS_EDITOR, counts per class) | `Codex/WP13_BOSS01_FIELD_MANIFEST.md` + `.csv` | rows counted and sampled against source |
| X-T5 | WP-16: pack graph questions on `Claude/Evidence/exports/PR2_*` and `PR3_*` (guard angle/drain/break, dodge i-frame and path, grab selection/alignment/release/aborts and WHERE the grab montage comes from, parry window and results, why the scratch tree ran twice in E-010 run 4) | updated `D09_PACK_REUSE_DELTA.md` with file:line | each D09 question answered or marked EDITOR NEEDED with the exact export wanted |
| X-T6 | Promotion patch sets for step 2 (binding) and step 3 (timeline, shadow): exact files, integration seams into live `Source/`, compile-risk table, test list, build/test commands. Draft only: staged, never applied | `Codex/PROMOTION_STEP2.md`, `PROMOTION_STEP3.md` | Claude can apply them in one pass after the owner accepts step 1 |
| X-T7 | Use `Antigravity/Evidence/timeline_expected.json` as independent expected values in the WP10 tests where the montage matches; review AG16 Rev 03 and AG-30 | review + updated draft tests | posted |
| X-T8 | Cold packaged load and cook proof PROCEDURE for `Content/OneBossFight/Data/Catalog` (what to package, which log lines prove a cold load without missing-path fallback, expected values) so Claude can run it | `Codex/CATALOG_PACKAGED_PROOF.md` | steps are exact and runnable with `Scripts/Package.ps1` / `PackagedSmoke.ps1` |
| X-T9 (HELD until DD-1 accepted, C-136) | P1 design pre-work (telegraph and readability data fields, validation rules, parity rule), design only, aligned with `Antigravity/AG3_TELEGRAPH_READABILITY_SPEC.md` | `Codex/P1_DESIGN.md` | posted; no code |
| X-T10 | Staged patch of the typed ABI closure checks and tests (from `TYPED_ABI_CLOSURE_TEST_SPEC.md`) plus the exact export list wanted | `Codex/PROMOTION_STEP1_TYPED_ABI.patch` | `git apply --check` OK, commands exact |
| X-T11 | Owner-facing step 1 acceptance package draft | `Codex/OWNER_PACKAGE_DD1_STEP1.md` | every claim cited; Claude verifies |
| X-T12 | Ready-to-paste entries for DECISIONS / KNOWN_ISSUES / TEST_PLAN / PROJECT_STATE | `Codex/DOC_ENTRIES_DD1.md` | existing table formats and next free ids |

## 3. ANTIGRAVITY queue (A-T1 to A-T7, in this order; items marked (wait) start when Codex delivers the input, do the next one meanwhile)

| ID | Task | Deliverable |
|---|---|---|
| A-T1 | Capture expected-value table for CAP-01 (A5 release), CAP-02 (A4 blade), CAP-05 (telegraph lead), CAP-06 (recovery): pass / fail numbers, tolerance rules, plus an OFFLINE analysis script that ingests the screenshots and log lines Claude produces and prints a verdict | `Antigravity/AG31_CAPTURE_VERDICT_TABLE.md`, `Evidence/capture_analysis.py` (self-tested on synthetic input, at least five rejection cases) |
| A-T2 | P1 acceptance tests: turn `AG3_TELEGRAPH_READABILITY_SPEC.md` into driver-checkable assertions per move using ONLY existing debug hooks (name every hook with file:line) | `Antigravity/AG32_P1_ACCEPTANCE_ASSERTIONS.md` |
| A-T3 (wait X-T5) | Final pack-reuse conclusions per row HIT-012, DEF-005, ANM-006, SEL-008 against Codex's graph answers; AG12 Rev 06 | updated `AG12_PACK_REUSE_INVENTORY.md` |
| A-T4 (wait X-T4) | Review the Boss01 field manifest for content and animation consequences: which fields are art-tied (notify timing, montage lengths, sockets) and need an animator, which are pure numbers | `Antigravity/AG33_MANIFEST_REVIEW.md` |
| A-T5 (wait X-T6) | Review the promotion patch sets for animation and content consequences and negative test cases that are missing | `Antigravity/AG34_PROMOTION_REVIEW.md` |
| A-T6 | Content authoring order for the P8 canary and the new weapon (dependencies between AG2, AG9, AG15 items, effort, which can start before P1) | `Antigravity/AG35_CONTENT_ORDER.md` |
| A-T7 | Adversarial review of Codex WP10 test plan and drafts (`Codex/Drafts/` tests): missing negative cases, oracle weaknesses | `Antigravity/AG36_WP10_REVIEW.md` |

## 4. CLAUDE queue (review, validation, testing only)

| ID | Task | Gate |
|---|---|---|
| C-T1 | Run the capture drafts CAP-01, 02, 05, 06 in the editor (reviewed by AG-21), feed results to A-T1 analysis | start now |
| C-T2 | Review every delivery as it lands (checklist: claim vs evidence, line spot checks, run reproducible checks); verdict in the mailbox | continuous |
| C-T3 | Cold packaged load / cook run of the catalog folder following X-T8 | after X-T8 |
| C-T4 | Apply promotion patches (step 2, then 3), build, automation, targeted drivers, full gate | after owner accepts step 1 and X-T6 |
| C-T5 | Full gate rerun after any source change; keep the baseline table current | continuous |
| C-T6 | `STEP0_SUPPLEMENT1.json` and `Claude/P0_REPORT.md`; present the P0 and DD-1 acceptance package to the owner | after X-T2, C-T3 |

## 5. Owner decisions waiting

Step 1 acceptance (after X-T2 and C-T3); promotion of steps 2 and 3 (after X-T6); whether P1 starts before the packaged proof. No other decision is open.

## 6. Progress counts (Claude updates after each review cycle)

Codex 9 of 9 processed (X-T9 held by design), X-T10 to X-T12 added (C-149); Antigravity 7 of 7 delivered, four open revisions: AG16 Rev 04, AG12 Rev 07, A-T4 Rev 3, capture camera; Claude: C-T3 done (Development), C-T6 supplement JSON done, first real CAP-01 run done (C-148), C-T1 waits for the camera version. Updated 2026-10-26 12:12.
