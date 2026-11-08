# Owner brief — controls/art remaining before a 95% claim

**Evidence cut:** mailbox C-1077 (2026-11-08 18:03) and current issue/test/review records. A-646 candidate boost values are accepted as asset readback; C-1075's comparison and the C-1077 hotfix rerun both failed to produce rendered frames. Claude's `P_SHOWCASE/aura_options.mp4` and `aura_compare.png` show current, boost-at-origin and boost-on-spine options (reported means 52.8/77.2/71.3) and were sent to the owner; no owner disposition is recorded. C-1076 confirms KI-196 default-wired moving control cases without runtime assignment on both routes; its package gate remains open.

**Requested decision:** What should “95% complete” mean for controls and art? No owner-approved milestone denominator, weighting, or completion rule is recorded. Readiness is therefore **UNDEFINED**; 95% is a requested target, not a measured result.

## Evidence status by gate

| State | Current evidence | Still required | References |
|---|---|---|---|
| Proven controls in PIE | KI-198 real blocked-contact counter sequence and damage on both routes. | Packaged runtime proof. | `KNOWN_ISSUES.md:322`; `TEST_PLAN.md` PIE ER-GUARD-COUNTER A4 r4. |
| Workaround-backed controls | KI-199 first standing and moving dodge after draw works on both routes; repeats work and no duplicate activation was observed. Root cause is not isolated. | Package/cook proof; investigate cause separately if required. | `KNOWN_ISSUES.md:323–324`; `TEST_PLAN.md:1900`; C-1067. |
| Open controls | KI-192 0.36 s charged-hold route split; KI-190 stamina-cost wording decision. | Bounded route comparison; owner/design decision. | `KNOWN_ISSUES.md:314,316`; `TEST_PLAN.md` KI-190 / C-971 entries. |
| PIE-proven, package open | KI-193 four default-wired ER attacks have 4/4 damage cases per route; KI-196 no-assignment moving dodge is proven both routes; KI-198 counter is proven. | Same-build staged manifest and packaged runtime checks, separately. | `KNOWN_ISSUES.md:317,320,322`; C-1076; `TEST_PLAN.md` C-1042/A-633/C-1076 receipts. |
| Accepted art direction, full-fight disposition pending | Owner approved the seven-item reel for implementation and the backstep default. Team technical review of the later fight video reports the aura is not discernible; owner checklist remains blank. | Owner reviews current footage and records item-specific verdicts. | `OWNER_REVIEW_PACK.md` status and Tier 2 Aura row; `FIGHT_VIDEO_REVIEW.md`; `FIGHT_VIDEO_REVIEW2_AG.md`. |
| Unapproved art / owner choice | A-646's separate aura candidate boost/readback is accepted; comparison driver failed in C-1075 and still rendered black on both routes in C-1077. The separate Lead showcase renders current, boost-at-origin and boost-on-spine options and was sent to the owner; disposition remains pending. Camera A/B/C remains unselected. | Owner visual choice on the delivered aura options. Camera requires dynamic baseline, then owner option. | A-646/C-1075/C-1077; `KNOWN_ISSUES.md:315`; `P_SHOWCASE/aura_options.mp4`; `CAMERA_MELEE_OCCLUSION_PROPOSAL.md`; `AN_C21_C25_CAMERA_DIAGNOSTIC.md`. |
| Release process risk | KI-197 stamped-stage preflight passes; this is not evidence of current artifact contamination. | Align roots before the next dual package. | `KNOWN_ISSUES.md:321`; `CONTROLS_STATUS.md` release-gate note. |

## Milestone denominator options

No existing owner-approved definition was found, so this brief does not calculate a readiness percentage or select an option. The owner decision needed is:

| Decision | Possible rule to specify (no option selected) |
|---|---|
| Scope | Enumerate milestone features and exclusions. |
| Weighting | Define equal feature weights or separate controls/art weights. |
| Completion | Decide whether workaround-backed, PIE-proven/package-open, and partially proven items count as complete, partial, or open. |
| Visual acceptance | Define who reviews, which retained capture is authoritative, and what disposition closes each visual item. |

Until these are defined, report each gate state above and leave 95% readiness **UNDEFINED**. Evidence index: `Documentation/Boss/AO_C05_KI_95_PERCENT_GAP_CENSUS.md`.
