# Queue AN-C41–C45 — regression and evidence audit

**Scope:** tool, test and evidence cross-check. This document does not close any owner, camera, visual or package gate. After this audit, Lead's C-1067 BUILD-263 artifacts appeared in the workspace and were reviewed: the one-route standing showcase passes the first-dodge retry; broader first-use acceptance and root-cause identification remain open.

## C41 — reference checker results

- `check_test_plan_ids.py` currently reports `build_rows=47 unique=43`, duplicate `BUILD-003` through `BUILD-006`, and nonnumeric order. Inspection shows legacy TEST_PLAN entries reuse those short IDs across distinct historical sections (for example BUILD-03 at lines 443 and 456); the recent C-1065/C-1066 and Queue AN notes add no BUILD table rows. This global checker output is therefore an existing cross-section collision, not evidence of newly introduced duplicate IDs. Keep the output visible; do not renumber historical evidence.
- `check_ki_references.py` found 33 Source references and 199 documented issue IDs with no current missing IDs. Source review found a real checker defect: missing references printed an error but still exited 0. Changed it to return nonzero when a missing reference is found and added isolated present/missing fixtures in `test_check_ki_references.py`.

## C42–C44 — coverage and current review state

- `test_first_dodge_after_draw_contract.py` requires the retained V2 load before input binding, a real R2 draw before first probe press, both standing/moving expected montage names, no runtime assignment, and cleanup of held input/callback/PIE. Its fixture is a source contract, not proof of runtime activation. The separate C-1065 test covers the pure one-shot eligibility predicate; neither test proves the Blueprint ASC dispatch at runtime.
- Native coverage is split by layer: `RPGDodgeInputRulesTests.cpp` covers standing/backstep vs directional roll selection and the empty optional-clip fallback; `RPGAutomationTests.cpp` `OneBossFight.Pack.Wiring` checks the four ER montage references load; `FRPGDodgeActivationRetryTest` covers five pure eligibility cases; startup/attachment suites cover player component attachment and route lifecycle. No native test simulates the pack InputBuffer or confirms first post-draw montage activation. Lead BUILD-263 is still required.
- Latest Claude task is C-1066: prioritize C-1065 before AN-C36+. X-1487 handed the candidate over. Lead C-1067 artifacts now show BUILD-263 and suite success (486/486) plus one retained first-standing showcase pass. No rejection is present; KI-199 remains open for both-route standing/moving checks, delayed-duplicate checks and root-cause isolation. KI-196 remains open for no-assignment moving-control proof. C-1051 camera A/B/C and C-1062 aura visibility proposal remain owner decisions; KI-191 is partial, KI-193 package proof remains open.

## C45 — acceptance matrix

| Area | Evidence currently in hand | Required next acceptance | Status |
|---|---|---|---|
| First dodge after R2 draw | BUILD-263 suite 486/486; C-1067 Lead PIE reports both-route standing V2 travel, moving quick rolls, normal repeats and no duplicate; guarded retry activates once | Keep package proof separate; reopen on first-use regression or duplicate. | CLOSED FOR PIE — KI-199; package open |
| Default-wired moving dodge | C-980 runtime-assigned logs show movement classification; probe has corrected per-tick movement input | Lead no-assignment `pie_er_default_wiring_dodge.py` both routes; verify press-time input/speed and exact standing/moving montage, then keep package proof separate. | OPEN — KI-196 |
| Camera composition | Static and full-fight reports differ in conditions; dynamic camera probe is authored; A/B/C options documented | Owner selects option; Lead dynamic probe captures arm length, actual hit component, camera-in-boss-bounds and safe wall/floor behavior before any Source change. | OPEN — owner choice/runtime |
| Tier 2 aura / PPM | Aura lifecycle witness and PPM PIE witness exist; Antigravity full-fight report says aura not visible on camera; C-1062 proposal awaits owner | Owner decides visual proposal; separate first-use and package evidence from lifecycle and screen-space PIE proof. | PARTIAL — KI-191 / OPEN package KI-193 |
| Fight video | BUILD-259 report indexed; owner boxes remain unchecked; BUILD-255 trim issue remains specific to prior video | Owner reviews exact retained MP4; new capture retains source-frame count, log, ffconcat/ASS and output together. | OPEN — owner review |

No runtime findings were promoted beyond the referenced Lead/Antigravity records. No Editor, build, package or PIE was run by Codex.
