# AC-C41–C45 — milestone status, release dependencies, and Queue AD

Date: 2026-11-07. Static documentation and mailbox reconciliation. Codex did not run Unreal, build, cook, package, Editor, or PIE.

## AC-C41 — current milestone gate matrix

| Gate | Owner / Lead / Antigravity | Evidence and current status | Next action / close condition |
|---|---|---|---|
| GATE-01: feature/source readiness | Lead owns compile/native verification; Codex source/docs work; Antigravity asset prep | BUILD-241..246 each report 482/482; BUILD-247 483/483; BUILD-248 484/484 and Shipping compile (TEST_PLAN dated receipts). These are distinct successive builds, not one current baseline claim. | Lead's next build must identify exact source revision, build ID, suite result, and Shipping outcome. |
| GATE-02: accepted animation content | Owner owns visual approval and assignment; Antigravity delivers; Lead owns import/runtime/package verification | C-977 sends four ER clips for owner review; A-589/A-590 report four trimmed montage readbacks. C-985 accepts A-594 recoil/aura previews for owner review; aura reads salmon in the unlit preview and final look is for engine/owner judgment. C-986 finds all five new montages have zero notifies, so trim/readback and visual acceptance do not establish combat functionality. | Owner reviews clips/previews; keep optional fields empty. Apply only verified notify rows, rerun Lead asset check and PIE hit/iframe/cancel cases, then prove cooked-package presence after assignment. |
| GATE-03: feature/runtime behavior | Lead owns PIE; owner confirms intended controls/content | C-975 runtime-assigned air routes and C-978 post-air grounded R1/R2 restoration are retained. C-980 invalidated earlier synthetic-movement cases; corrected probes exist but reruns remain pending (KI-196). C-986's montage asset check fails the notify-presence gate; no successful hit/iframe/cancel retest is recorded. Player active-montage death/reset behavior is still unverified (AC-C06–C10). | Lead runs corrected both-route probes and lifecycle observations after verified notify authoring; attach raw logs/build identity and update KI-193/194/196 only within demonstrated scope. |
| GATE-04: performance and shipped render defaults | Owner owns resumption/quality decision; Lead owns measured runs; Codex maintains intake | C-954 parks Round 6 Phase 2; no phase-2 results. Phase-1/historical measurements, target 60 FPS / p99 <=16.67 ms, and predictions are separate in AC-C26–C30. | Owner resumes the benchmark and image-quality review; keep current shipped default unchanged until a measured, approved decision exists. |
| GATE-05: offline/native quality gates | Lead owns native/build gate; Codex owns offline scripts and evidence | At the AC-C41–C45 snapshot: A-594 422 OK / 1 skipped / broken_links=0; importer X-1389 focused fixtures 11/11; AC-C31–C35 focused tests 11/11. At that time KI-195 had seven direct calls; Queue AD-C16–C20 subsequently bounded them (35/35) and closed the issue. | Continue focused hardening; keep standalone callsite gaps visible. Do not treat offline pass counts as native/PIE/build proof. |
| GATE-06: package/cook/release identity | Lead owns package, cook coverage, smoke, Shipping route proof; owner owns product acceptance | BUILD-246 CookCoverage passed for that build, but it predates later content; BUILD-248 reports Shipping compile, not a current staged package/gameplay run. AA-C41–C44 smoke/cook plan is procedural. | On approved content/revision, close Editor before build, capture build/stage IDs and hashes, run current CookCoverage + staged smoke + separate route/gameplay capture. |
| GATE-07: animation evidence registry | Owner reviews; Antigravity maintains registry/media; Lead verifies UE material/runtime | C-985 accepts A-594 recoil/aura previews for owner review; aura reads salmon in the unlit preview, final appearance belongs to engine/owner review. C-986 reports zero notifies on all five new montages. No owner approval, notify recheck, or Lead Tier 2 PIE/cook proof is recorded. | Owner review, notify correction and asset recheck, then separately record runtime/cook and field assignment; do not upgrade status from delivery alone. |

## AC-C42 — count and date reconciliation

- **Native builds:** BUILD-241..246: each 482/482; BUILD-247: 483/483; BUILD-248: 484/484 plus Shipping compile. Treat these as distinct dated build receipts (TEST_PLAN, BUILD rows), not an aggregate.
- **PIE:** C-971 latency has 11 cases per route and one 0.36 s R2 route split; C-975 air-route checks; C-978 post-air grounded R1/R2 restoration on both routes; C-980 backstep/movement correction. These are Lead-run observations, not Codex execution. Earlier moving cases are invalid pending rerun.
- **Offline:** A-590 419 passed/1 skipped, A-593 421/1, A-594 latest 422/1 and broken_links=0. C-985 separately reports Claude's offline suite at 8.1 s of the 20 s budget and accepts X-1391/X-1392; A-595 contains no newer count.
- **Focused importer:** X-1383 9/9 is historical; X-1389 later reports 11/11.
- **Performance:** retain target 60 FPS / p99 <=16.67 ms separately from Round 1–5 historical measurements and any predictions. Round 6 Phase 2 is PARKED / NOT RUN.

## AC-C43 — active release blockers and dependencies

Owner gates: review the four ER clips and corrected Tier 2 previews; authorize optional-field assignment; decide when Round 6 Phase 2/image-quality review resumes. Lead gates: complete C-986 notify correction and asset check; rerun hit, iframe, cancel, and corrected moving-control PIE probes on both routes; inspect active montage across death/reset; verify Tier 2 UE rendering and load timing; verify assigned assets in cook/stage; run current Shipping smoke and gameplay route checks. Antigravity delivery is evidence supply only; A-595 does not clear an owner or Lead gate. Open issue links: KI-191–193, KI-195–196. KI-194 is resolved only for C-978's tested post-air grounded routes. No release gate is inferred closed from absent data.

## AC-C44 — owner status, one page

The current engineering lane has completed eight batches of source/evidence review and tooling work (AC-C01–C40). Latest recorded build evidence is BUILD-248 at 484/484 with Shipping compile; latest offline suite receipt is 422 passed, one skipped, zero broken links, and Claude accepts that suite's 8.1 s/20 s run. Lead's retained PIE proves both air routes restore grounded R1/R2 after use, while the earlier synthetic moving-dodge readings were invalidated and need corrected reruns. All four ER clips have accepted trims/readbacks, but owner video review and optional-field assignment remain open; C-986 found no notifies on all four ER montages and the recoil montage, so their gameplay function remains unverified. Tier 2 R3 previews are accepted for owner review, not owner approval; aura colour reads salmon in the unlit preview, final look is in engine. Round 6 Phase 2 remains owner-parked; 60 FPS / p99 <=16.67 ms is the target, not a current result. Next: keep optional fields empty, complete notify asset/readback checks, collect owner reviews, then have Lead produce revision-identified PIE/cook/package evidence; continue offline audit batches meanwhile.

## AC-C45 — Queue AD

Drafted in `Documentation/Boss/QUEUE_AD.md`: ten ordered batches, five tasks each, IDs AD-C01..AD-C50. It is a proposed Codex work queue; Lead/owner-only runtime, product, and approval decisions remain explicit handoffs. No runtime or acceptance status is changed by this plan.

## Current status addendum — AD-C36–C40 / C-989–C-991

The matrix above is a dated snapshot. The current controlling gate state and its close conditions are refreshed in `Documentation/Boss/AD_C36_C40_RELEASE_GATES_AND_READINESS_AUDIT.md`. In particular, GATE-07 is now exactly **C-988: 1 of 5 match, re-authoring pending** per C-989; four montage corrections and fresh Lead readback remain open. C-954 still parks Phase 2; BUILD-248 remains historical; the KI-196 corrected moving-control probe still needs Lead rerun. The owner-controlled decision fields are in `Documentation/Boss/AD_C40_RELEASE_READINESS_DECISION_SHEET.md`.

## Later receipt update — A-597

C-989's 1/5 status was superseded by A-597's five new Lead lines: the C-988 target rows appear in all five montages, but GuardCounter's proposed FootStep row remains absent. See `Documentation/Boss/AD_C46_C50_INDEPENDENT_CLOSEOUT_AND_NEXT_LANE.md`; exact full-table match is not asserted. The reported offline suite result lacks raw output and is not independently verified.
