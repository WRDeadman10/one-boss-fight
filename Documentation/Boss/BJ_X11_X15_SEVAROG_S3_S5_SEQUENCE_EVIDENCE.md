# Queue BJ-X11–X15 — Sevarog S3–S5 sequence evidence

**Status:** Static reconciliation of existing Lead/Codex reports and status entries. No raw logs, media, assets, tests, build, Editor, PIE, or package were accessed or run.

## X11 — source values versus observed gameplay

`C1276_S6_RECONCILE_S7_S8_PROVISIONAL_AND_PHASES.md` records S3's 55 damage and S5's 25 damage as design/source values and labels new phase/effect values provisional pending PIE. This batch treats those as source/design records. The relevant recorded live observations below are attributed to the Lead's BUILD-295 / P_C1265_SEVAROGLIVE4 entry in TEST_PLAN, not independently verified here.

## X12 — S3 step-in/contact

TEST_PLAN records S3 `Swing3_Slow` stepping in 37.0 cm and applying 55 damage in the later live run. An earlier run recorded 37.7/50 cm step-in and 55 damage. These values are run-specific; do not collapse them into an exact guaranteed displacement. A proper acceptance record should bind the card, actor, start/end transforms, requested warp, actual capsule displacement, target range, hit delta, and the same run/build ID.

## X13 — S4→S5 combo and per-card attribution

The BUILD-295 status entry records S4 `Speedburst` dash 330 cm with zero S4 card hit/damage delta, followed by the actual combo gate `Whiff -> Continue next=S5`; S5 `Swing1_Medium` then hit for 25 at 120 cm. This supersedes the earlier BUILD-294 observation where a target-life abort prevented S5 and the old lifetime total looked like S4 contact. The Codex C-1262a report also records the separate per-card delta fix and four bright retained captures. These reported events show one run's S4/S5 sequence; they do not establish repeated reliability, S1/S2 isolated contact, or global navigation acceptance.

## X14 — remaining F5 evidence

| Observation | Current record status | Remaining evidence |
|---|---|---|
| S1/S2 at 140 cm | Reported zero card hits; traces support a weapon/capsule miss | Isolated contact under saved approved card values; S2 positive/negative distances |
| S3 step-in | Reported 37.0 cm and 55 damage in BUILD-295 | Identity-matched setup/transforms and repeat per Lead plan |
| S4 | Reported 330 cm dash and 0/0 card delta | Live behavior across intended setup; keep dash displacement and damage distinct |
| S5 | Reported combo continuation after S4 whiff and 25 hit at 120 cm | Standalone/pattern relevance only if Lead's acceptance criteria require it |

Do not count a S4→S5 combo result as isolated S1/S2 evidence. Keep the per-card delta separate from encounter lifetime totals and prior-run results.

## X15 — disposition

Existing reports document a successful S3/S4/S5 sequence in BUILD-295 and the prior iteration history. S1/S2 140 cm misses remain open and are not closed by S5's combo hit. No source value was changed and no Lead acceptance verdict was found in the checked mailbox through X-1910. Lead owns any further live run and card-level acceptance.

**Validation:** manual report/status/mailbox reads only; no raw logs or media accessed, no tests or engine operations.
