# AC-C36–C40 — ER controls, animation review, receipts, and issue index

Date: 2026-11-07. Static cross-check of Source, current docs, and mailbox receipts. No Source/asset change, test, Unreal, build, cook, or PIE run in this batch.

## AC-C36 — player-controls spec versus Source and receipts

Refreshed `ER_PLAYER_CONTROLS_SPEC.md` against `RPGDodgeTiming` optional fields and retained receipts. ER AirLight/AirHeavy optional paths remain empty-default and restore their pack arrays; C-975 exercised runtime-assigned routes and C-978 verified post-air grounded R1/R2 restoration on both routes. Owner review and saved asset assignment remain pending. The spec now distinguishes intended R2 hold mapping (C-944/C-945) from C-971's 0.36 s observation: legacy selected ChargedAttack while data selected Ability_E; all are game-tick-bounded and the cause is not established. C-980's later retained movement diagnostics show nonzero speed/last input, while earlier zero-input injected cases remain invalid under KI-196.

## AC-C37 — GATE-07 and newest animation receipts

Cross-checked the current GATE-07 table against C-977/A-589/C-979/A-590 for ER, C-982/C-983 for Tier 2 partial acceptance, A-594 delivery, C-985 owner-review acceptance, and C-986's failed notify-presence asset check. GATE-07 distinguishes visual acceptance for owner review from final owner approval; the aura reads salmon in the unlit preview, with final look in engine. The current five new montages have zero notifies per Lead, so content readbacks do not establish combat functionality. Lead PIE/cook/runtime and any field assignment remain separate. The A-594-referenced strips, PNGs, and MP4s are present under `Docs/BossCombatReview/Execution/Antigravity/Tier2_Art/`.

## AC-C38 — TEST_PLAN receipt/count/date reconciliation

The 2026-11-07 build rows are separate receipts: BUILD-241 through BUILD-246 remain 482/482; BUILD-247 is 483/483; BUILD-248 is 484/484 and Shipping compiled. Those are successive build IDs, not competing same-run counts. PIE evidence is separately dated and scoped: C-971 latency (11 cases per route); C-975 runtime-assigned air routes; C-978 post-air ground restoration; C-980 backstep probe. The C-971 latency row now replaces the earlier stale “not run” plan text. Its R2 data is retained; moving-case classification is separately invalidated by C-980. Offline counts are not native builds: A-590 419/1, A-593 421/1, A-594 latest 422/1 (broken links 0). Importer fixture X-1383 9/9 is historical; X-1389 later reports 11/11. No counts were merged.

## AC-C39 — ER/Tier 2 known issues

KI-191 remains open for BeginPlay-only PPM resolution, unmeasured load cost, and missing Lead UE runtime proof; A-594 preview delivery does not close it. KI-192 remains open for the C-971 R2 route split, without threshold tuning or device-latency claims. KI-193 remains open for ER owner video review and saved-field assignment. KI-194 is closed only for C-978's tested post-air grounded R1/R2 routes. KI-196 remains open for corrected moving-probe Lead reruns on both routes; C-980's final backstep-specific log is distinct from earlier failed synthetic-IA_Move evidence. These scopes agree with current test-plan receipts.

## AC-C40 — mailbox index

`DECISIONS.md` indexes through C-984 and includes the C-983 partial Tier 2 acceptance, C-984 follow-through order, and A-594 R3 delivery plus latest offline-suite receipt. This index remains navigation; mailbox messages and raw evidence remain authoritative.

