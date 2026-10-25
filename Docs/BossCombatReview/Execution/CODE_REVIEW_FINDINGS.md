# Independent review findings

Updated 2026-10-25. No implementation submitted for this initiative; no change accepted. Prior audit findings are carried as review candidates, not newly reproduced defects.

## Current review queue

| ID | Observation / evidence | Confidence and boundary | Required resolution | Gate impact |
|---|---|---|---|---|
| RV-01 | Wave rendering guarded by !UE_BUILD_SHIPPING; prior G01/KI-065 | Source-confirmed path; no fresh packaged capture or proof excluding independent VFX | Claude identifies renderer; AG debug-off capture and geometry match | P1 candidate; P0 validation priority |
| RV-02 | Tracker checks ActiveEnd before ActiveStart; specials poll Active; ring checks current annulus | Source-confirmed mechanisms; skipped-event/contact occurrence not freshly reproduced | Bounded hitch/rate tests with continuing vs aborted attack and geometry chronology | P2 candidate |
| RV-03 | Authored/fallback montage names resolve same timing row | Source-confirmed mapping; actual fallback contact mismatch requires current track inspection | Effective montage/notify/rate matrix for both | P2 candidate |
| RV-04 | Native HP-only specials separated from pack outcomes; wave priority uses HP delta | Source-confirmed coupling; intended per-move guard/parry policy not fully resolved | Current production resolver graph, attributed direct/wave contacts and owner policy | P3 candidate |
| RV-05 | Native identity allocated after playback; index-based tracker; default recovery not enforced by RecoveryEndTime | Source-confirmed native contract; pack safeguards and real punish length unresolved | Start/finalize path, montage-instance restart and next-damage timing | P2/P5 candidate |
| RV-06 | A4 natural scheduling absent in historical KI-067; native test entry exists | Historical/source evidence; current BT overrides need verification | Live eligible selector graph plus natural opportunities/selections | P4 candidate |
| RV-07 | Visible follower sword and hidden pack trace differ as owners | Structural fact, not measured unfair contact | Synchronized actual sweep/visible blade capture | P4 validation |
| RV-08 | KI-106 earlier stale-montage/pose-damping diagnosis superseded by C-84 | Evidence conflict resolved historically; current setup discrepancy remains | Compare heading/setup only if needed for baseline; no speculative gameplay repair | Do not reopen product diagnosis without evidence |
| RV-09 | Old audit ANM-003 N/A reflects current fixed-delay implementation; approved A2 includes authored stable hold intent | Design reconciliation required; “not implemented today” alone cannot make target N/A | Compare Freeze 30.2, approved A2 scope and actual hold/variable-delay distinction | P0 classification review |
| RV-10 | TASKS/PROJECT_STATE summary test totals predate C-84; M14 raw set has 7 wins/2 deaths, not 9 wins | Documentation freshness; no new product defect | Use dated primary records and maintain separate six-run telegraph set | P0 evidence integrity |

Evidence: [ranked prior findings](C:/UnrealProject/OneBossFight/Docs/BossCombatReview/ExistingBossAudit/04_CRITICAL_GAPS.md), [source and graph analysis](C:/UnrealProject/OneBossFight/Docs/BossCombatReview/ExistingBossAudit/05_ANIMATION_AND_DAMAGE_AUDIT.md), [M14 section 14](C:/UnrealProject/OneBossFight/Documentation/M14_FIGHT_NOTES.md:154), [mailbox C-84](C:/UnrealProject/OneBossFight/Documentation/TEAM_MAILBOX.md:2746). Core four source hashes remain equal to prior audit; compiled/asset identity still requires P0.

## Review method

Read actual submitted changes or probe sources plus callers, not only report text. For asset behavior require current graph/notify export or captured runtime evidence. Check state ownership, identity, event ordering, failure/abort paths, generation, duplicate handling, defense policy, motion owner, rates, recovery and test setup.

A test passes only its assertions under its recorded conditions. An artificial HP loss does not prove central-hit identity; forced StartMove does not prove selector reachability; observer sweep does not prove production trace; offline render does not prove packaged cue.

Review response must name severity, exact file/function/graph/frame, failing scenario, cause/proof boundary, required correction and retest. Findings are returned to the accountable implementer, not silently fixed by Codex.

## Acceptance ledger

- A-39 / CI-P0-A-01: **CHANGES REQUIRED**, X-95, 2026-10-25. Independently inspected all four submitted documents and relevant source. Runtime absolutes exceed offline/source evidence; A4 reach arithmetic and coordinate/capsule comparison invalid; raw extraction provenance absent; timing and VIS IDs need correction. See [review 01](C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/P0_AG_REVIEW_01.md). No implementation or gate accepted; AG revises its own files.
- A-40 / CI-P0-A-01 Revision 02: **CHANGES REQUIRED (narrowed)**, X-96, 2026-10-25. All 20 raw-log input hashes/sizes match current files and the major A-39 evidence-boundary errors were corrected. Remaining failures: the script hard-codes rather than derives pose labels, inclusive-frame durations are one sample high, VIS-07 contradicts raw foot-bone bounds, visible follower sockets are still conflated with production trace sockets, live StaggerGetUp routing is wrong, and A2/fallback claims exceed current runtime evidence. See [review 02](C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/P0_AG_REVIEW_02.md). Partial offline measurements are usable; report and P0 are not accepted.

- A-41 / C-87: X-97, 2026-10-25. AG Revision 03 is usable partial offline evidence with residual corrections; complete baseline remains pending. Claude's raw exports confirm MidRange/Sprint/Retaliation montage assignments absent from native tracker rows. Missing pack safeguards and actual natural frequencies remain unresolved. Correct style/live boss ability count to 11 including ragdoll death. Two bounded bot samples are within existing P0 scope. See [review 03](C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/P0_REVIEW_03.md).

No complete technical/visual baseline or phase accepted. Record future verdicts here with task revision, evidence IDs, reviewer and residual limitations. P0 gate cannot pass with critical evidence gaps silently waived.


- A-42 / CI-P0-A-01 Revision 04: **ACCEPTED WITH DOCUMENTED LIMITATIONS (offline subset only)**, C-89, 2026-10-25, reviewer Claude (acting lead). 20/20 input hashes and sizes verified; nine corrections requested (paths of three pack montages, A1 fallback 0.115 s, runtime clip swap, VIS-08 severity, links, A4 wording, header, extractor provenance, riposte root). Runtime, contact and Shipping items remain UNVERIFIED. See [review 04](C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/P0_AG_REVIEW_04.md).
- RV-11 (new, Claude, source-confirmed + live-resolved): `Mid01_Anim_Montage`, `GS_SprintAttackFollowUp_Montage` and `RetaliationAttack_Montage` are live natural damaging pack moves absent from `RPGAttackTracker::Attacks` (E-002, E-002-10). `Mid01` observed once in a bot fight (E-004, B warm, 129 cm). Pack-side safeguards unread; natural frequency unmeasured. P4 candidate (coverage); no change proposed yet.
- RV-12 (new, harness): a minimized editor window makes PIE tick at about 3 fps and invalidates every timing driver (E-004). Operational note for the editor owner; not a product defect.
