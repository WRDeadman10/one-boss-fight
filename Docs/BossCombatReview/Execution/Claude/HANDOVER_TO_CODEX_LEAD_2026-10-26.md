# Handover: Claude (outgoing technical lead) to Codex (incoming technical lead), 2026-10-26 19:xx

The owner swapped the roles in chat on 2026-10-26: "Now the Codex will lead this from here yours and codex's roles are exchanged ... this role switch will happen often so keep in mind that". From now: **Codex leads** (plans, assigns work orders, accepts or rejects deliveries, owns the control documents). **Claude** is the implementer, integration and runtime owner and the only person who runs the Unreal Editor, builds and packages, and still reviews independently. **Antigravity** keeps content, capture, analysis and (by owner permission) commits and pushes. Roles will switch again: read the latest mailbox lead announcement before assuming who leads.

## 1. Owner decisions (verbatim, chat 2026-10-26 evening)
1. Accept step 1 or not yet: "Do what is best" (delegated). Claude's recorded decision as outgoing lead: **ACCEPT step 1 BOUNDED**: accepted for what is proven (three-build parity from the data catalog, typed reference closure live for the three shipped weapons, cold packaged load in Development, epoch survives a world travel). Conditions that stay OPEN and tracked as gates (not forgotten): distinct fourth weapon, same-leaf decoy and uncooked-item negatives (fixtures approved, being built), concurrent teardown/equip and choice-across-travel, constrained viewport and once-only diagnostics, Shipping provenance, a clean packaged log (KI-080 materials, CommonUI error). Codex as the new lead may tighten or revise this.
2. Test assets for the typed checks: "Yes" (the three developer-only fixtures of `Codex/C155_A100_REVIEW.md`).
3. A5 javelin release visual: "Park it" (UNVERIFIED; telemetry numbers stay).
4. Commit and push: "Antigravity can push".
5. P1 design work: "Do what is necessary" (release P1 DESIGN; design first, code only through the normal gates).

## 2. State in one page
- DD-1 step 0 closed; step 1 built; automation 41/41; full gate on the typed-ABI state 39/40 (`pie_close_attacks` C7 = known KI-106 timing check, rerun 55/55); cold packaged Development load `source=data` twice; travel: two `LoadMap`, one epoch (`STEP0_BASELINE.md` supplements 4 to 9, hashes inside).
- 83 requirements: 66 PARTIAL, 16 UNVERIFIED, 1 MISSING, 0 IMPLEMENTED (D10 matrix). P1 to P8 not started in code.
- Steps 2 and 3: staged scaffold patches `Codex/PROMOTION_STEP2_SCAFFOLD.patch` and `PROMOTION_STEP3_SCAFFOLD.patch` (apply-check OK, never applied), product-ready conditions listed in your `PROMOTION_STEP2.md`/`STEP3.md`.
- Pack facts (E-009, E-011): style grants 11 abilities, no guard/dodge/grab/heal; turn-in-place is live on the boss; no motion warping; grab montage source unknown.
- Route (a) scratch proof E-010 (feasible, not P2). Capture: external `CaptureLoop.ps1` + `run_in_editor.py`; CAP-02/05/06 have real frames; CAP-01 parked.

## 3. Control documents you take over (Claude wrote them): `MASTER_EXECUTION_PLAN.md`, `PHASE_STATUS.md`, `TASK_BOARD.md`, `DELEGATION_REGISTER.md`, `DESIGN_DECISIONS_PENDING.md`, `CODE_REVIEW_FINDINGS.md`, `MAILBOX_WATCH_STATE.md`. Update them as lead; Claude keeps the evidence files under `Claude/`.

## 4. Rules and lessons that cost time (keep them)
- No commits/pushes except Antigravity (owner permission); never rewrite history; no pack asset edits; G-4 and G-5 still denied; all 83 requirements stay required; the editor is Claude's alone.
- Stale Python runners in the standing editor: bridge-run drivers can leave a registered Slate callback; restart the editor between driver versions or the old code answers first.
- After any packaged run check `Get-Process OneBossFight` and stop with `taskkill /F /T`: a stray game process at full CPU made every PIE timing driver fail for hours.
- `hasattr`/`getattr(...,default)` readbacks fabricate values: a missing hook must raise. A RESULT line printed by a driver is not evidence; the analyzer/gate is.
- `CookCoverage` reads every `/Game/...` literal in `Source/` (tests included): new paths need always-cook directories or a split literal.
- Read long log lines in full (I misread a truncated line once); slice logs by line count taken before the run.
- Gate = `Scripts/RunDrivers.ps1` with no arguments from a fresh editor (about 90 minutes); do not touch the editor meanwhile.

## 5. What Claude does next under your lead (proposal; you decide)
1. Create the three typed-ABI fixtures (owner yes) and implement your 5 positive / 12 negative cases (`TYPED_ABI_CLOSURE_TEST_SPEC.md`), run automation and the editor/package checks.
2. Promote the step 2 then step 3 scaffolds in the order you set, with build, automation, targeted drivers and a full gate after each.
3. Support the P1 design (editor measurements, driver hooks) once you open it.
