# AC-C46–C50 — independent cross-check and Queue AD handoff

Date: 2026-11-07. Read-only consistency/path/receipt review plus documentation reconciliation. No asset edits, Unreal, Editor, build, cook, package, PIE, or tests run by Codex.

## AC-C46 — cross-check against Source, tests, config, and mailbox

| AC report | Cross-check result | Status / correction |
|---|---|---|
| AC-C01–C05 | Importer status grammar and 9/9 receipt are the historical X-1383 run; X-1389 later reports 11/11. Four accepted sequence ranges and montage durations match A-584/A-589/A-590 and GATE-07. `RPGAutomationTests.cpp:1192-1195` confirms four optional fields default null. | No mismatch in the report's historical scope. Later 11/11 is correctly recorded in newer AC-C16/C36/C41 summaries. Montage readback says trim/shape only, not hit functionality. |
| AC-C06–C10 | `RPGDodgeTiming::EndPlay` restores temporary arrays but does not stop player montage; reset source stops boss mesh montage. C-978 only proves grounded R1/R2 after air route on both routes. | Behavior remains unverified rather than claimed broken; test matrix correctly scopes the open question. |
| AC-C11–C15 | `RPGFrameworkMoveExecutor` has two guarded-contact callbacks and separate parry path; the 0.60 s counter window is declared a proposal. | No broad damage-path or runtime guarantee is inferred. |
| AC-C16–C20 | Importer validation, editor-only helper and tests, AN-sequence versus AM-slice distinction, and `DefaultGame.ini` cook root have corresponding source/config references. BUILD-246 CookCoverage and BUILD-248 compile are not current package proof. | Updated the C-20 task-time “Claude review pending” wording: C-985 accepted A-594 previews for owner review. Added C-986 zero-notify failure state and KI-193 handoff. |
| AC-C21–C25 | Tier 2 preview source hooks remain default-off/optional. C-985 accepts A-594 visuals for owner review; aura is salmon in unlit preview. C-986 asset check says recoil montage has zero notifies. | Updated acceptance table/source state; retain owner/runtime/cook gates and zero-notify hotfix. |
| AC-C26–C30 | C-971 raw route split is at 0.36 s with legacy ChargedAttack vs data Ability_E; Phase 2 remains owner-parked. C-951 experiment base is not a ship default. | Consistent with source callback limits and C-954 order; no cause/device latency is inferred. |
| AC-C31–C35 | At that batch's snapshot, KI-195 listed seven direct test calls without per-call bounds. Queue AD-C16–C20 later converted all seven and closed KI-195. | This remains offline wrapper/test-process evidence, not a full suite/native gate. Current callsite census is `AD_C16_C20_SUBPROCESS_TIMEOUT_HARDENING.md`. |
| AC-C36–C40 | Movement probe fix and prior invalid samples are distinguished; build/offline/importer/PIE counts are separated. C-985 adds preview review acceptance; C-986 adds montage failure. | Updated the GATE-07 reconciliation paragraph with C-985/C-986. Historical C-971/C-980 observations remain scoped. |
| AC-C41–C45 | Gate matrix and owner summary separate source, offline, PIE, package, owner and Lead gates. A-595 is not approval; C-985/C-986 are now captured. | Current status consistent; Queue AD has 50 ordered IDs. |

No unresolved source/report contradiction remains among the nine AC reports after the noted C-985/C-986 updates. Explicit open evidence gates remain: notify helper output for Ability_E/hit-react and cancel template, corrected Lead asset/PIE checks, owner animation review/assignment, and current cook/package proof.

## AC-C47 — paths and machine assumptions

Scanned the nine AC reports and `QUEUE_AD.md` for drive-letter paths, user-profile paths, `/home`, and `/tmp`: none found. Repo-relative references are intentional. Existing GATE-07 media `file:///c:/...` links are outside the new AC reports and intentionally point to local review media; they are not carried into Queue AD.

## AC-C48 — newest Lead/Antigravity receipts

- **C-985:** accepts X-1391/X-1392 and A-594 Tier 2 R3 previews for owner review. Aura colour reads salmon in the unlit preview; final look is reserved for engine/owner judgment.
- **C-986:** Lead asset check confirms class/slot/skeleton/length and material/effect load checks, but all five new montages have zero notifies. This is a real functionality gate: GuardCounter and air attacks lack the hit trace; Backstep lacks iframe/cancel windows. `AA_A08_NOTIFY_FRAMES_TABLE.md` was corrected to use real classes and evidence-backed scaled rows. The exact `Ability_E_Anim_Montage`, hit-react, and cancel-template helper output is not in retained exports and remains explicitly unfilled; do not fabricate these timings.
- **A-595:** completes AA-A17..A25 documentation/art tasks and reports the same 422/1 offline count; AA-A21 remains owner-waiting. No effect on C-986's asset failure or the owner/Lead gates.

## AC-C49 — next-lane handoff

Queue AC is closed after this batch. Queue AD is in `Documentation/Boss/QUEUE_AD.md` (ten batches, AD-C01..C50). AD batch 1 is complete in `Documentation/Boss/AD_C01_C05_ER_NOTIFY_AND_ASSIGNMENT_AUDIT.md`:

1. Keep optional montage references empty until owner visual review and assignment authorization.
2. Populate notify proposals only from real `describe_notifies` output and cite the template; exact missing timelines are Ability_E, the chosen hit-react montage, and the Dodge cancel template.
3. Antigravity may author verified notifies under ENGINE_LOCK with assert-before-save; Lead repeats asset check and PIE to verify damage/iframes/cancel behavior.
4. Lead verifies cooked package and Shipping behavior after owner approval/assignment; existing cook root and historical BUILD receipts do not prove current staged content.

At the time of this handoff, current evidence boundaries were BUILD-248 484/484 plus Shipping compile; A-594 offline receipt 422/1, broken_links=0; C-985 visuals for owner review; and C-986's zero-notify check. A-596 later reported authoring; C-988's Lead readback partly rejects that post and assigns four asset repairs. Fresh Lead asset check/PIE and owner review/assignment remain open. Round 6 Phase 2 remains owner-parked; KI-191..193 and KI-195..196 stay open, KI-194 is limited to C-978 post-air restoration.

## AC-C50 — closure

Queue AC C01–C50 is closed. X-1394 is the batch receipt. Queue AD batch 1 is complete; AD-C06–C10 continue without waiting for review. No project gate or asset acceptance is changed by this closeout.
