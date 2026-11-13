# Queue BJ-X06–X10 — Sevarog S1/S2 and approach evidence

**Status:** Static report/decision reconciliation. No raw trace log, asset, test, build, Editor, PIE, or package was opened or run in this batch.

## X06 — approved source range versus saved/live state

`BE_X26_X30_S1_S2_RANGE.md` records C-1274 approval for the two named medium cards only: inclusive `MinRangeCm=90`, `MaxRangeCm=120`, with timing/windows unchanged. Its C-1155 receipt establishes Development build and transient dry-run status as recorded, not current saved-card readback or S2 live acceptance. The later handoffs `BF_X26_X30_SEVAROG_CARD_AND_LIVE_EVIDENCE_AUDIT.md`, `BF_X46_X50_CLOSEOUT.md`, and `BG_A11_A40_DISPOSITIONS_AND_CHECKS.md` continue to leave saved/live reach and S2 acceptance open for Lead.

## X07 — reported hit/reach evidence

`C1269_S1_S2_RANGE_PROPOSAL.md` reports isolated S1 and S2 runs at 140 cm finishing with zero card hits. Its cited 140 cm trace samples put S1's active-window endpoint 106.114 cm from capsule surface; S2 samples put its closest endpoint 45.422 cm and `weapon_r` 37.022 cm away, against a 15 cm trace radius. These are cited findings from the existing report; raw logs were not re-read here. They support the observed 140 cm misses, not a precise hit threshold or proof that a 90–120 cm band alone resolves S2.

The same proposal records a distinct S4→S5 combo hit for 25 damage at 120 cm. That is not an isolated S1 or S2 positive result. The saved card values, isolated S1 positive at the approved edge, and isolated S2 hit/whiff threshold remain unconfirmed by the checked handoffs.

## X08 — approach and navigation diagnosis

`C1258A_SEVAROG_IN_BAND_NAV_AND_END.md` records an in-band self-test at 140 cm when the then-current card ranges were 90–180 cm. It shows that those cards started/ended, but it is not evidence for the later 90–120 range. `TEST_PLAN.md` records an earlier spawn at 205.6 cm ending `Framework.Nav.MoveFailed`, and a subsequent 140 cm run with zero S1/S2 card hits. Neither record supplies the current same-run full path request, terminal code/flags, projected goal, actor terminal position, and remaining distance required by `BE_X16_X20_NAVIGATION_DIAGNOSIS.md` to determine general approach root cause.

Keep in-band card playback, card reach/contact, and autonomous approach/navigation as three separate claims. A `Finished` card does not prove contact; a miss does not by itself diagnose pathfinding.

## X09 — minimum identity-matched evidence intake

For each isolated S1/S2 attempt, record one named build/package and map, route/definition, actor identities and generation, saved card path/hash and read-back range/windows, measured start range and orientation, request/terminal route and generation, weapon/capsule trace distances during the active window, accepted hit count/damage, and final card result. For approach attempts, also preserve navigation system/Recast availability, goal projection, request ID/full-path result, terminal code/raw flags, terminal actor/goal positions and remaining distance. Repeat only under Lead's run plan and preserve each result separately.

## X10 — disposition

The existing approval and traces justify a 90–120 cm test candidate for S1/S2, not final saved/live acceptance. Lead still owns saved-row confirmation and isolated live S1/S2 reach/contact; general approach diagnosis needs an identity-matched navigation receipt. No tuning or acceptance status changed.

**Validation:** manual reading of current reports and mailbox/status references only. No raw logs, tests, checkers, builds, Unreal, PIE, assets, or packages were accessed.
