# Queue AU — gameplay gaps from full-fight review

**Basis:** Claude C-1109; `FIGHT_VIDEO_REVIEW.md`, `FIGHT_VIDEO_REVIEW2_AG.md`, and `OWNER_REVIEW_PACK.md` read for this queue. **Protocol:** execute in five-task batches, send Claude one concise update after each batch, then continue without waiting for review. Check feedback every cycle; fix rejected work immediately and put the hotfix back in the next review update. Claude owns Unreal build/PIE runs. Codex may add offline tests and source/doc changes, but does not launch Unreal, build, commit, or push.

**Latest (C-1119/C-1120, 2026-11-09):** hotfixed natural-montage parry diagnostics/fallback and per-slot timeout logging; fixed comma-packed `-Env` parsing; replaced fixed aura warmups with a brightness-driven, 20-frame/four-game-second gate. AU-C41–C44 offline work adds four-state visual annotation validation, run/frame/action camera context (world occlusion remains explicitly unmeasured), seven-owner-box blank guard, and evidence-scope guidance. Combined hotfix/AU suite 72/72; Python syntax and diff check pass. AU-C40 smoke and AU-C45 representative visible/obscured frame review are Lead PIE gates; no runtime/editor work by Codex. See `AU_C1119_C1120_AND_C41_C45_HOTFIX.md`.

**Closeout (C-1121):** AU-C46–C50 reconcile all findings and preserve the owner checklist, record the C-1119/C-1120 offline hotfix and Lead gates, and draft next five offline tasks in `QUEUE_AV.md`. The final crosswalk is `AU_C46_C50_FINAL_HANDOFF.md`. AU-C40/C45 and C-1119/C-1120 runtime reruns remain with Claude; owner full-fight visual dispositions remain open.

**Progress:** AU-C01–C04 complete offline; AU-C05 DATA-default Lead PIE pending. AU-C06–C09 complete offline; AU-C10 DATA-default Lead PIE pending. C-1111 rejected the first Lead run at startup (health uninitialized); hotfix added readiness detection and a five-fight-second grace, regression tests pass 27/27, and Lead rerun is requested. AU-C11–C14 complete offline: evidence-stage reconciliation, IEND/truncation fixtures, run/phase failure receipts, frame hashes, and restore readback contracts. AU-C15 original-only DATA-default Lead PIE pending. AU-C16–C18 and C20 complete offline: the lifecycle probe has a 50.1%/50% boundary row, aura manifest/readbacks include active/attachment/transform identity, transient restore is explicitly read back after error, and the evidence-only comparison sheet preserves owner gates. Batch 4 focused contracts pass 16/16; Lead PIE was not run by Codex. AU-C19 paired capture remains gated on a valid AU-C15 source frame. See `AU_C01_C05_LIVE_PARRY_CAPTURE.md`, `AU_C06_C10_PARRY_RECEIPT_AND_FRAMES.md`, `AU_C1111_HP_INITIALIZATION_HOTFIX.md`, `AU_C11_C15_AURA_CAPTURE_DIAGNOSIS.md`, and `AU_C16_C20_AURA_VISIBILITY_GATE.md`. Continue AU-C21–C25 without waiting.

**Latest:** AU-C21–C24 are offline complete. Reconciled dynamic C-1051 intrusion versus C-1044 open-ground non-intrusion and bounded C-1105 B+C/look evidence; camera probe now emits structured geometry/obstruction/frame-time samples and labels unset startup as DATA-default (legacy requires explicit `RPG_LEGACY_STARTUP=1`). Receipt tests distinguish missing, malformed, stale and unknown values. Batch 5 focused contracts pass 8/8. AU-C25 DATA-default Lead baseline remains pending; C-1105's nine-start B+C case is not continuous circling coverage. No Editor run by Codex.

**Latest:** AU-C26–C29 are offline complete. Air Light start/end records now bind exact start distance and player/boss/camera/pivot/arm state to run/action/frame markers; the optional per-run `AIR_LIGHT_START_DISTANCE_CM` diagnostic setup is unset by default and adds no gameplay threshold. Receipt fixtures accept close/mid/open samples without a threshold and reject missing, malformed, non-finite or stale frame/run data. Batch 6 focused tests 20/20. AU-C30 three-cell DATA-default Lead matrix remains pending; no Editor run by Codex.

**Latest:** C-1114 rejected the fixed-slot parry approach after Lead's 150 s run; the test-first opportunistic-window/parry-only hotfix was posted READY as X-1587, and its Lead rerun is pending. AU-C31–C35 are complete: separate capture identity checks, source-pixel counts (BUILD-255 six black lead-in frames; BUILD-259 seven), trim/ASS alignment fixture, and a BUILD-255 trim-six input-only handoff. Video-tool tests 13/13 pass; no MP4 rendered or reviewed. Owner decision on requesting the corrected excerpt remains open. Report: `AU_C31_C35_CAPTURE_IDENTITY_AND_TRIM_AUDIT.md`. Continue AU-C36–C40 without waiting.

**Hotfix:** C-1116/C-1117 both reproduced as test-first offline failures and are corrected: RunLeadPie lowercases its final Python path (including an 8.3 path) and the aura capture READY log uses its serialized manifest record instead of out-of-scope locals. Focused contracts pass 17/17. READY report: `AU_C1116_C1117_RUNNER_AND_AURA_HOTFIX.md`; Lead rerun remains with Claude.

**Latest:** AU-C36–C39 are offline complete. Driver action and frame markers now share unique run IDs; summary emits separate action/contact/refill/death/frame/boss-death totals, boss HP and AI controller readbacks, and driver-side boss write counters. `fight_capture_receipt.py` validates totals and explicit build/map/configured-route/Tier 2/tool-SHA provenance against the same raw log's activation witness, then emits JSON. Driver/receipt/video tests pass 44/44. AU-C40 30-game-second DATA-default Lead smoke is queued with a fresh-root invocation; no Editor run by Codex. Report: `AU_C36_C40_CAPTURE_RECEIPT_AND_SMOKE.md`.

## Evidence baseline and boundaries

- BUILD-259 / `fight_review2.mp4` is a distinct capture from BUILD-255 / `fight_review.mp4`. AG reports four ER moves visible in BUILD-259, no parry actions, and Phase-Two Aura not discernible on camera. The seven owner checklist boxes remain unchecked.
- BUILD-259 is a DATA-default run, ended at boss death after 7202 frames and 79 player refills. The driver does not claim natural player survival. It does not exercise a parry. Keep those limitations in any resulting capture summary.
- C-1042's focused PIE proves the controlled parry recoil/PPM response and aura lifecycle; this does not prove full-fight appearance. C-1075/C-1077 paired aura captures failed with black frames. The separately rendered aura options have no owner disposition. Do not change or save the approved original, select an aura option, or infer visual approval.
- AG's dynamic melee camera intrusion and Air Light close-start clipping are observations, not an approved camera/default change or a proven animation defect. Camera options and owner visual ticks are decision gates. No threshold or fix may be invented to close them.
- No legacy parity-only run. Acceptance route for Lead rows is DATA-default with same-run `[EncounterActivation]` witness. A legacy route is only a diagnostic control if Claude explicitly asks for it.

## Lead PIE receipt fields

Every row marked **Lead PIE** requires the BUILD ID, map and same-run route witness; driver/script revision; start/end game time; action/event markers; the relevant component and state readbacks; health before/after when contact matters; frame labels, PNG paths and hashes; and explicit PASS/FAIL/INCONCLUSIVE with the stopping reason. Parry rows additionally require A4 live-window observation, `RPGPlayerParry.press()` result, parried-count delta, recoil montage and PPM blendable/weight. Aura rows require component asset/active state, health fraction, camera/pivot, capture completion and decoded PNG metrics. A press alone, component lifecycle alone, or readable black PNG is not a visual pass.

## Batch 1 — establish a valid full-fight parry attempt

| Task | Work | Acceptance |
|---|---|---|
| AU-C01 | Map the current full-fight action scheduler, action counts and termination conditions against `pie_tier2_parry.py`'s real-contact witness. | A source-cited note distinguishes scheduled input, successful parry, recoil and visible PPM; does not treat a button press as success. |
| AU-C02 | Add offline tests first for a parry action slot and its required outcome fields in the full-fight driver/parser. | Tests reject a schedule without parry and reject a report that counts attempts as successful parries; no Unreal dependency. |
| AU-C03 | Implement an event-driven parry action that responds to an observed live A4 active window, using the established parry component API; do not hard-code wall-clock timing. | Driver emits attempt and observed-window markers; it never labels `opened=true` as a successful contact by itself. |
| AU-C04 | Add bounded timeout/cleanup behavior for no A4 window, missing parry component, or a parry that does not contact. | Offline fixtures prove each case terminates, releases held keys, and reports INCONCLUSIVE/FAIL rather than hanging or passing. |
| AU-C05 | **Lead PIE:** run one full-fight-driver parry probe on DATA-default. | Receipt has A4 active-window position, press result, parried-count delta, health/contact, and final outcome; a miss is retained as a miss, not hidden by later actions. |

## Batch 2 — prove parry feedback and preserve capture evidence

| Task | Work | Acceptance |
|---|---|---|
| AU-C06 | Extend the offline receipt parser to distinguish attempt, window-open, real parry, recoil, PPM and frame-ready markers. | Synthetic valid and missing-marker fixtures prove each state is independently represented; no success is inferred from action count. |
| AU-C07 | Add test-first checks for exactly one parried-count increment and matching recoil montage after contact. | Duplicate parry, no count delta, absent recoil, and stale prior count fixtures fail closed. |
| AU-C08 | Capture labeled pre-contact and post-contact frames in the full-fight driver using the established completion wait. | Offline contract checks stable unique labels, no overwrite, bounded PNG wait and a manifest row per accepted frame. |
| AU-C09 | Record FollowCamera blendables and PPM weight at press/contact/frame times using the existing readback boundary. | Missing/unreadable blendables are explicit UNKNOWN; the parser does not claim PPM visibility based only on a component or CVar. |
| AU-C10 | **Lead PIE:** verify the integrated real-contact parry path and feedback in DATA-default. | Receipt includes same-run route, contact/count delta, recoil montage, blendable weights and readable frames at the requested offsets; visual PPM judgment remains Lead/owner-scoped. |

## Batch 3 — diagnose the failed aura comparison capture path

| Task | Work | Acceptance |
|---|---|---|
| AU-C11 | Reconcile C-1075 and C-1077 aura comparison failure markers against the current driver and PNG decoder before proposing a cause. | A short evidence note names only the observed failed stage(s); it separates PNG completion, pixel decoding, black-frame rejection and runtime asset readback. |
| AU-C12 | Add tests first for aura comparison outcomes: missing file, truncated PNG, all-black image, dark valid arena, and usable non-black image. | Fixtures prove malformed/black captures cannot become a comparison pass and avoid declaring arbitrary exposure/brightness a gameplay fix. |
| AU-C13 | Instrument each capture phase with unique request ID, route, game time, phase, camera/pivot, asset readback and completion/failure reason. | Offline contract verifies all lifecycle phases are attributable to one run and old files cannot satisfy a new request. |
| AU-C14 | Add fail-closed preconditions and cleanup assertions around the paired comparison's world, camera, active component, transient asset swap and restore. | Offline contracts cover each missing precondition and prove the original asset restore path remains mandatory on success and error. |
| AU-C15 | **Lead PIE:** run the original-only DATA-default capture path before another paired comparison. | Receipt identifies source frame files/hashes, camera/pivot, brightness metrics and exact failure point; do not proceed to visual comparison if source frames are black or incomplete. |

## Batch 4 — make aura visibility evidence decision-safe

| Task | Work | Acceptance |
|---|---|---|
| AU-C16 | Add tests for aura activation boundary and cleanup claims against the existing C-1042 lifecycle scope. | Test assertions cover threshold boundary, active state, reset/death/EndPlay cleanup only where corresponding source APIs exist; no claim exceeds the probe. |
| AU-C17 | Add a read-only diagnostic row to the aura Lead probe for health fraction, Niagara asset, active state, attachment/socket, component transform and camera/pivot. | Offline contract requires each value or explicit UNKNOWN and keeps the approved asset path visible in the receipt. |
| AU-C18 | Test candidate swap/restore as a transient operation without editor-property mutation or save. | Synthetic contract confirms original path is restored after both normal completion and injected failure; no asset mutation is included. |
| AU-C19 | **Lead PIE:** collect same-run original/candidate paired captures only after AU-C15 has a non-black source path. | Same camera, health fraction, settle interval and route are witnessed; each PNG is decoded and hashed; candidate readback is recorded; no visual selection is stated. |
| AU-C20 | Prepare an evidence-only comparison sheet that separates full-fight “not discernible,” lifecycle proof, failed black captures and owner choice. | Every row links to its capture/source; owner choice remains unselected and owner checklist boxes remain untouched. |

## Batch 5 — characterize the dynamic melee camera observation safely

| Task | Work | Acceptance |
|---|---|---|
| AU-C21 | Audit existing camera telemetry and C-1051 evidence for the beside/behind-player sequence; identify unobserved values only. | Read-only gap note distinguishes open-ground C-1044 from dynamic C-1051 and bounded C-1105; it proposes no camera option as selected. |
| AU-C22 | Add offline parser tests for camera distance, spring-arm length, boss-relative angle, obstruction/hide state and frame association. | Valid, missing, malformed and stale-frame fixtures are distinguished; unknown values cannot be interpreted as zero intrusion. |
| AU-C23 | Extend the diagnostic-only Lead driver to log those camera values while the boss circles beside/behind the player. | No production camera behavior/default changes; telemetry is time-aligned with action and frame markers. |
| AU-C24 | Add a bounded scenario receipt that explicitly labels the C-1105 nine-start B+C case as limited coverage. | Receipt rejects claims of continuous circling/full-fight coverage from the nine-start matrix. |
| AU-C25 | **Lead PIE:** run dynamic diagnostic on DATA-default with current defaults, then stop for owner choice. | Receipt shows camera/pivot/arm, boss relative location, obstruction/hide state and frames for each event; no A/B/C/B+C option is applied by Codex. |

## Batch 6 — characterize Air Light's close-start crop

| Task | Work | Acceptance |
|---|---|---|
| AU-C26 | Map Air Light's action start, montage window and full-fight camera framing instrumentation. | Source note links the AG observation (25 appearances; mid-range readable, close start clipped) to the exact capture, without inferring an animation defect. |
| AU-C27 | Add offline tests for per-action start distance and camera-frame metadata association. | Tests reject missing distance/frame identifiers and do not embed an unapproved minimum-distance threshold. |
| AU-C28 | Add diagnostic-only start distance, player/boss positions and camera framing markers to the Air Light action receipt. | Existing move timing and input are unchanged; all values are logged from the same action window. |
| AU-C29 | Define a Lead observation row for open, mid and close starts using the same route/build/action, without changing production distances. | Matrix requests observed distance and clipping/framing evidence; labels each cell NOT RUN until Lead supplies it. |
| AU-C30 | **Lead PIE:** capture those three Air Light start-distance observations on DATA-default. | Receipt correlates each action with actual distance and frame crop; no threshold or source fix is approved absent reproducible evidence and owner review. |

## Batch 7 — keep full-fight capture versions and action coverage honest

| Task | Work | Acceptance |
|---|---|---|
| AU-C31 | Add offline tests that bind BUILD-255 and BUILD-259 manifests/review notes to distinct capture IDs. | Fixtures reject cross-version transfer of BUILD-255's first-six-black finding or its missing Guard Counter into BUILD-259. |
| AU-C32 | Add a source-frame audit report for black/near-black runs with frame index, game time and action marker. | Report identifies the BUILD-255 six black source PNGs and first visible frame without relabeling BUILD-259. |
| AU-C33 | Exercise existing six-frame trim and subtitle-offset logic with test-first synthetic frame/label fixtures. | Tests prove the trim changes frame timeline and ASS offsets by the same amount, with untrimmed input preserved. |
| AU-C34 | Prepare a BUILD-255 trim/review handoff using existing generated media tooling only if source frames are retained. | Handoff lists exact input/output identity and says owner review is still required; no BUILD-259 claim is derived from it. |
| AU-C35 | **Lead/Owner review:** confirm whether a corrected BUILD-255 excerpt is needed, and keep BUILD-259 as its own review. | Both capture IDs, Tier 2 state and distinct finding scope are explicit; owner box remains unchecked until owner responds. |

## Batch 8 — capture-context and fight termination telemetry

| Task | Work | Acceptance |
|---|---|---|
| AU-C36 | Add tests for full-fight summary accounting of actions, successful contacts, refills, frames and boss-death termination. | Synthetic logs with duplicate, missing or contradictory totals fail; 79 refills remains historical BUILD-259 data, not a target. |
| AU-C37 | Improve the driver summary to separate player refills from player deaths and boss health/AI changes. | Runtime report states whether boss health/AI remained untouched and records each refill event; no “natural survival” wording. |
| AU-C38 | Add action-to-frame linkage tests for Backstep, Guard Counter, Air Light and Air Heavy markers. | Each event points to frames from the same run; absent actions are explicitly zero/NOT SEEN. |
| AU-C39 | Add a machine-readable full-fight provenance row with build, map, route witness, Tier 2 setting and capture tool revision. | Parser fails on missing or inconsistent provenance and never infers route from a filename alone. |
| AU-C40 | **Lead PIE:** produce a short DATA-default full-fight driver smoke receipt before another long review capture. | Receipt validates startup, route, frame readiness, action counters, refill context and clean stop; Lead decides whether a longer fight is warranted. |

## Batch 9 — protect the full-fight review from false positives

| Task | Work | Acceptance |
|---|---|---|
| AU-C41 | Add tests for the review parser's seen/not-seen/obscured/inconclusive states. | Obscured or missing frames cannot be counted as visible; component activation cannot substitute for image evidence. |
| AU-C42 | Add explicit metadata for camera occlusion and boss/player framing at action time. | Logs can distinguish effect absent from effect hidden/unclear without claiming visual interpretation automatically. |
| AU-C43 | Add a no-owner-judgment contract for the seven-row review sheet. | Static check confirms all owner boxes remain blank and no automation writes a verdict/timestamp into owner fields. |
| AU-C44 | Update the review guide to identify Lead technical observations versus owner visual disposition. | BUILD-255 and BUILD-259, focused PIE and separate showcase each have distinct evidence scope and owner action. |
| AU-C45 | **Lead PIE:** run a focused capture-quality check for one representative move and one obscured camera case. | Receipt demonstrates readable frame versus explicitly obscured frame and includes camera/action linkage; no owner verdict is inferred. |

## Batch 10 — close the evidence loop and hand off the next batch

| Task | Work | Acceptance |
|---|---|---|
| AU-C46 | Reconcile every finding in `AU_GAMEPLAY_GAP_INVENTORY.md` against resolved evidence, open code work and owner/Lead gates. | Each original finding has one current status and evidence pointer; no finding silently disappears. |
| AU-C47 | Cross-check AU changes against current Source, scripts, focused offline tests and latest Claude mailbox feedback. | Report distinguishes implemented, offline-tested, Lead-PIE-pending and owner-pending; no stale acceptance claim. |
| AU-C48 | Apply any Claude rejection from prior batches immediately as a bounded test-first hotfix. | Hotfix includes regression fixture and exact rejected claim addressed; return it in the current five-task review message. |
| AU-C49 | Refresh the owner-facing full-fight evidence handoff without filling owner-only review fields. | All seven checklist rows, aura/camera choices, source/build scope and capture limitations are accurate and unselected. |
| AU-C50 | Close Queue AU and draft the next five-task queue from remaining proven gameplay gaps. | Ten batch receipts, unresolved gates and next queue are indexed; closure means Codex offline work complete, not owner/Lead/game acceptance. |

## Execution rule

Execute each five-task batch, report to Claude after the batch, then proceed to the next batch while review runs. Inspect new Claude feedback each cycle and hotfix rejected work immediately, including its regression fixture and evidence in the next batch update. Do not perform any Lead PIE row, owner selection, media judgment, asset save, package run, commit or push as Codex.
