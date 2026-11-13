# BM-46..50: residual KNOWN_ISSUES triage and lane BM closeout (lane BM, batch 10 of 10)

C (implementer), 2026-11-12, per the owner's 50-task instruction.

**Not done:** no source edits, and no Unreal, build, PIE, commit or push.

## BM-46/47: triage of every open KI (heuristic, labelled as such)

`KNOWN_ISSUES.md` has **185 KI rows**, of which **117 are open**: the final status cell contains `open` case-insensitively (115 contain capitalized `Open`; KI-147 and KI-183 use lowercase `open`). Each open row was classified with **keyword rules** applied to its status and description text, in this order, first match wins:

| Class | Meaning | Count |
|---|---|---|
| **E** | engine-gated: needs an Unreal, PIE, Editor, package or GPU run | 57 |
| **D** | owner-decision-gated | 8 |
| **L** | a recorded limit or note, with no action defined | 3 |
| **O** | possible owner-independent offline follow-up (heuristic; each must be confirmed by hand before scheduling) | 49 |

**This is a triage aid, not a verification.** The rules are coarse: an "O" row may still need an engine run, and an "L" row may hide actionable work. The rows this lane re-verified by hand are marked in the **BM** column (21 rows); their batch reports carry the exact status.

| KI | Area | Class | BM batch | Status (truncated) |
|---|---|---|---|---|
| KI-001 | Toolchain | O |  | Open |
| KI-003 | Performance | O |  | Open |
| KI-004 | Performance | O |  | Open |
| KI-005 | Input | O |  | Open |
| KI-002 | Build | O |  | Open |
| KI-009 | Animation | O |  | Open |
| KI-010 | Input | E |  | Open (implemented, untested in play) |
| KI-012 | Tooling | E |  | Open |
| KI-014 | Boss | E |  | Open |
| KI-015 | Boss | E |  | Open |
| KI-016 | Boss | O |  | Open |
| KI-020 | Input | O |  | Open |
| KI-022 | UI | O |  | Open |
| KI-024 | VFX | O |  | Open |
| KI-026 | Tooling | O |  | Open |
| KI-028 | Project | E |  | Open (stage 3) |
| KI-029 | Content | O |  | Open |
| KI-030 | Pack | O |  | Open |
| KI-033 | Pack edits | O |  | Open |
| KI-034 | Greystone [harmless] | E |  | Open |
| KI-035 | Greystone | O |  | Open |
| KI-036 | Pack edits | O |  | Open |
| KI-037 | Camera | E |  | Open |
| KI-039 | Sevarog | O |  | Open |
| KI-040 | Greystone | O |  | Open |
| KI-041 | Project | D |  | Open |
| KI-045 | Greystone | O |  | Open |
| KI-050 | Project | O |  | Open |
| KI-055 | Tooling | O |  | Open |
| KI-057 | Tests | O |  | Open |
| KI-058 | Tooling | E |  | Open |
| KI-059 | Player | O |  | Open |
| KI-051 | Performance | E |  | Open |
| KI-061 | Audio | E |  | Open |
| KI-062 | Art | E |  | Open |
| KI-063 | Boss | O |  | Open |
| KI-065 | Boss | O |  | Open |
| KI-066 | Camera | E |  | Open |
| KI-067 | Boss | O |  | Open |
| KI-068 | Boss | O |  | Open |
| KI-070 | Art | O |  | Open |
| KI-074 | Boss | O |  | Open |
| KI-078 | Presentation | O |  | Open |
| KI-079 | Repo | O |  | Open |
| KI-080 | Repo | O |  | Open |
| KI-081 | Test | E |  | Open (procedure) |
| KI-085 | Player | L |  | Open (limitation, untested by hand) |
| KI-087 | Presentation | O |  | Open (cosmetic) |
| KI-094 | Gate 3 | E |  | Open (note) |
| KI-099 | Balance | D |  | Open |
| KI-102 | Boss | D |  | Open (owner decision, option built). Evidence 2026-10-24 (tw |
| KI-103 | Test | O |  | Open (intermittent) |
| KI-104 | Art | E |  | Open (accepted for Gate 4 unless the owner asks for more) |
| KI-105 | Art | E |  | Open: look at it when screenshots work, then adjust sizes |
| KI-106 | Boss | O |  | Open, low priority |
| KI-107 | Art | E |  | Open: look at it when screenshots work |
| KI-108 | Performance | E |  | Open: experiments and the GPU profile (kit round 2) |
| KI-101 | Test | O |  | Open (test relaxed, real fights verified) |
| KI-093 | Environment | E |  | Open (environment) |
| KI-091 | Gate 3 | L |  | Open (note) |
| KI-092 | Gate 3 | O |  | Open |
| KI-109 | Test | E |  | Open |
| KI-110 | Boss | O |  | Open (capability limit decided by Codex X-245; native fix no |
| KI-111 | Test | E |  | Open (limits recorded, no failure observed) |
| KI-112 | Test | E |  | Open (limits recorded, no failure observed) |
| KI-113 | Test | E |  | Open (limits recorded, no failure observed) |
| KI-114 | Test | E |  | Open (limits recorded, no failure observed) |
| KI-115 | Test | E |  | Open (limits recorded, no failure observed) |
| KI-116 | Test | E |  | Open (limits and process exceptions recorded, no failure in  |
| KI-117 | Test | E |  | Open (limits recorded, no failure observed) |
| KI-118 | Test | E |  | Open (limits recorded, no failure observed) |
| KI-119 | Test | E |  | Open (limits recorded, no failure observed) |
| KI-120 | Test | E |  | Open (limits recorded, no failure observed) |
| KI-121 | Test | E |  | Open (limits recorded; one failed build attempt kept on reco |
| KI-122 | Test | E |  | Open (limits recorded; built and run clean on the first atte |
| KI-123 | Test | E |  | Open (documented limits) |
| KI-124 | DD19 verification limits | E |  | Open limits; Claude review pending |
| KI-125 | DD20 source-only limits | E |  | Open |
| KI-126 | Authoring | E |  | Open (offline qualification limits documented) |
| KI-127 | Authoring | E |  | Open (staged qualification limits documented) |
| KI-128 | Arithmetic residual, C266/C268 | O | BM-26..30 | Open residual; no lasting nonfinite threshold claimed |
| KI-129 | DD21 measured limits | E |  | Open; lead run acceptance pending |
| KI-130 | DD22 measured limits | E |  | Open; lead run acceptance pending |
| KI-131 | DD23 source-only limits | E |  | Open; lead source review pending |
| KI-132 | DD24 source-only limits | E |  | Open |
| KI-133 | DD25 source-only limits | E |  | Open; lead source review pending |
| KI-134 | DD26 source-only integration/authoring l | O |  | Open; source review pending |
| KI-135 | Authoring toolkit / engine API | E |  | Open; correction and in-editor authoring verification pendin |
| KI-136 | Death lifecycle / issue traceability | E | BM-36..40 | Open; dedicated reference recorded, source-comment dispositi |
| KI-137 | DD28 staged registration limits | E |  | Open; STAGED SOURCE REVIEW PENDING, no runtime verification |
| KI-138 | DD29 staged world composition limits | E |  | Open; STAGED SOURCE REVIEW PENDING, five tests UNRUN |
| KI-139 | Authoring toolkit / soft-class conversio | E |  | Open; DD27g measured / accepted C328; A218 correction and DD |
| KI-145 | Proposed card ranges exceed the measured | E |  | Open, design  Update 2026-10-31 (C-463): Antigravity's sampl |
| KI-147 | RESOLVED for baked windows (2026-10-30,  | O |  | Resolved for baked windows; open for unbaked ones |
| KI-154 | Boss | E | BM-36..40 | Open (no deterministic native repro; live contact evidence n |
| KI-155 | Framework proof profile | L | BM-36..40 | Open (proof-profile limitation, observed by Claude C-707) |
| KI-158 | Tooling (low) | D | BM-11..15 | Open |
| KI-159 | Tooling (low) | D | BM-11..15 | Open |
| KI-160 | Tooling (low) | D | BM-11..15 | Open |
| KI-161 | Tooling (low) | D | BM-11..15 | Open |
| KI-162 | Tooling (low) | D | BM-11..15 | Open |
| KI-163 | Tooling (low) | O | BM-01..05 | Open |
| KI-164 | Tooling (low) | O | BM-01..05 | Open |
| KI-165 | Tooling (low) | O | BM-16..20 | Open |
| KI-166 | Tooling (low) | O | BM-16..20 | Open |
| KI-167 | Tooling (low) | O | BM-01..05 | Open |
| KI-168 | Release (low) | E | BM-21..25 | Open (source disposition recorded; binary check pending) |
| KI-169 | Editor tooling (low) | E |  | Open (unverified; needs a reflected Editor check) |
| KI-170 | Tooling (low) | E | BM-06..10 | Open (unverified; needs a reflected Editor check) |
| KI-171 | Editor tooling (low) | E | BM-06..10 | Open (unverified; needs a reflected Editor check) |
| KI-174 | Boss combo pause / arena leash (low, opt | O | BM-36..40 | Open (low, opt-in leash; C-743) |
| KI-175 | Player parry lifecycle / respawn (low, u | E | BM-31..35 | Open (no deterministic native repro; needs live lifecycle ev |
| KI-176 | Player parry stamina refund / unreadable | O | BM-31..35 | Open (no deterministic native repro; needs actual-path fixtu |
| KI-177 | Boss parry recovery / stance-break order | E |  | Open (live proof needs an F5 framework-boss PIE fixture, una |
| KI-179 | Framework executor watchdog automation c | E |  | Open (no deterministic runtime defect repro; automation fixt |
| KI-181 | Selector subnormal score underflow (low, | O | BM-31..35 | Open (low, source-level boundary; C-760) |
| KI-183 | Shipping encounter selection API boundar | E |  | Policy decided; implementation/proof row remains open until  |

## BM-48: cumulative lane BM result (BM-01..50)

| Batch | Tasks | Deliverable | Checks actually run |
|---|---|---|---|
| 1 | BM-01..05 | ledger hygiene proposals (`BM_01_05_LEDGER_HYGIENE.md`) | `grep` re-reads; no tests |
| 2 | BM-06..10 | Python parse census (`test_python_parse_census.py`) | 990 files parsed; HEAD vs working-tree check; **2/2** |
| 3 | BM-11..15 | destructive-cleanup scope pins (`test_destructive_cleanup_scope.py`) | AST and line scans; **6/6**; the tools were not executed |
| 4 | BM-16..20 | KI-165/166 characterization (`test_ki165_166_characterization.py`) | real temp-folder subprocess runs; **5/5** |
| 5 | BM-21..25 | Shipping CVar guard census (`test_shipping_cvar_guards.py`) | static census of 52 declarations; **3/3** |
| 6 | BM-26..30 | KI-128 threshold-overflow native test (`RPGBleedThresholdOverflowTests.cpp`) | hand trace; **not compiled or run** (engine-gated) |
| 7 | BM-31..35 | parry and selector static pins (`test_parry_selector_static_pins.py`) | source reads; IEEE round-trip check; **5/5** |
| 8 | BM-36..40 | framework boss static pins (`test_framework_boss_static_pins.py`) | source reads; **5/5** |
| 9 | BM-41..45 | compile-risk lint (`test_bl_bm_compile_risk_lint.py`) | 51 files linted, 0 hits; detectors proven; **5/5** |
| 10 | BM-46..50 | this triage and closeout | KI table parse; heuristic rules |

**Totals:**
- **New Python test suites:** 7, 31 tests in all, every one passing on the final rerun (2026-11-12). The BL lane's `test_bl_lane_static_checks.py` was also rerun: 5/5. **New native test files:** 1, not compiled.
- **Production source changed by C:** none.
- **Commits by C:** none.

**Key findings:**
1. **KI-170/171** fail at HEAD and parse only because of uncommitted working-tree repairs. The KI-171 repair changes control flow and needs the lead's review.
2. **`MakeBenchKit.ps1:76`** also deletes an existing zip, which is not in KI-158.
3. **KI-166:** `profile_dump.py` exits 0 on a wrong-shaped input, and `card_table.py` leaves partial output before crashing.
4. **KI-168:** the 6 Shipping-visible controls match exactly, and there is no KI-185-pattern leak. KI-185's guarded-declaration count is now 46, not 35.
5. **KI-128:** the threshold-growth overflow is transient; the stored value is the finite cap.
6. **KI-181:** the underflow happens only at the double-to-float narrowing.
7. **KI-174:** off-arena time counts toward the combo pause; whether it should is the lead's decision.
8. **Moved citations** for KI-164, KI-165, KI-174, KI-175 and KI-176 are proposed in the batch reports.

**Review status:** AG accepted all BM-01..50 as clean (A-896, A-897, A-898). Codex static review of BM-26..50 found no discrepancies (X-2209, X-2211). No hotfixes are pending. Engine-gated acceptance remains open.

## BM-49: one-command run of every BM Python suite

From the repo root:

```
python -m unittest discover -s Scripts/Tools -p "test_python_parse_census.py" && python -m unittest discover -s Scripts/Tools -p "test_destructive_cleanup_scope.py" && python -m unittest discover -s Scripts/Tools -p "test_ki165_166_characterization.py" && python -m unittest discover -s Scripts/Tools -p "test_shipping_cvar_guards.py" && python -m unittest discover -s Scripts/Tools -p "test_parry_selector_static_pins.py" && python -m unittest discover -s Scripts/Tools -p "test_framework_boss_static_pins.py" && python -m unittest discover -s Scripts/Tools -p "test_bl_bm_compile_risk_lint.py" && python -m unittest discover -s Scripts/Tools -p "test_bl_lane_static_checks.py"
```

## BM-50: gated items handed back

| Gate | Items |
|---|---|
| **Engine-gated (lead)** | the BL plus BM native test build and automation run (50 BL tests plus `OneBossFight.Framework.Bleed.ThresholdGrowthOverflow`); the KI-168 binary check; the KI-169/171 reflected Editor checks; the live runs for KI-154/155/174/175/176/177/179 |
| **Owner-gated** | the KI-158..168 fix decisions; X-1991; the HIT-008 scope |
| **Lead decisions** | applying the BM-01..05 ledger proposals; the KI-174 pause intent; the KI-136 comment re-cite; committing and reviewing the KI-170/171 working-tree repairs |
