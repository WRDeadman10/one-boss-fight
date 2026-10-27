# AG17 / A145: bounded corrections required

2026-10-27, Codex. Actual report24298 bytes / SHA256 `7009593cbb059a2db21f8bc71e653bb811c94ab6a9fb1455d7b74a69a6c171e1`; all8 table input raw hash/size receipts match. A145 counts9 artifacts including output. AG16 Rev3 report32104 bytes / `a8c8566cfa67aec72beacedb0dbc933673259501aca57c4b096381ccff8710de`, all15 table receipts match; IFrame ownership/timing/conditional controls/TrackedMontage precision fixes accepted bounded.

The21-event inventory/order, two source triggers, inheritance-name walks and manual-review limits are useful. Revise the following before final acceptance. No engine test or extraction occurred.

## Candidate exit0 is not fingerprint/configuration equivalence

The helper final exit condition checks order, Attach hook-call patterns and raw source hash **only when not --candidate**. It reports triggerTokensUnchanged but does not fail on false. It reports bodyTokenSHA256 but does not enforce equality to the baseline in candidate mode. Extraction changes body structure, so generic equality is not automatically an appropriate replacement policy either.

Two independent targeted probes are saved in `Codex/Step2Preparation/ag17_candidate_review_probes.json`, pinned to unchanged helper SHA256 `995376c1f0ca8a2c81a4d6032a1cf00f8df730bd883f2ea48b66afab7e42fe01`:

| Synthetic candidate | Actual result |
|---|---|
| Changed Phase1 music asset path inside Attach | exit0/orderMatches=true; body hash de3575a8...19558 differs from baseline |
| Duplicate Attach(Actor) in spawn callback | exit0/orderMatches=true; triggerTokensUnchanged=false |

These are two offline false-acceptance cases, not runtime tests. Temporary .cpp text was confined to a Codex-owned child directory, never compiled/loaded, then cleaned. Live Source/helper/baseline unchanged. Each invocation includes11 existing fake selftests; do not inflate an Unreal total or claim equivalence passed. Correct section4.1/Witness1: exit0 and21 events alone do not verify defaults or hook equivalence. AddFootsteps/static helper bodies also lie outside the Attach fingerprint and need their own review/pins.

## Guard preservation and source distinctions

- Counts10 IsPackPlayer(Pawn)/18 IsPackBoss(Pawn) are **syntactic call sites**, independently counted; else-if short circuit makes actual runtime counts path dependent. Nine player construction sites plus footsteps and21 boss events are categories, not an actor's total component count.
- Do not call reducing18 checks to1 "semantically desirable" or prescribe a new null guard. PacketB preserves original short-circuiting, branch independence, evaluation/registration interleaving and scope until a separately reviewed choice permits change. Existing null path is safe via classifier false results. A hybrid classification control is hypothetical, not proof of an actual overlapping asset hierarchy.
- CombatDebug attaches/registers under boss/component guards regardless of rpg.Debug. The source comment says it **shows nothing** until the cvar is positive. Fix the event configuration column to separate attachment from presentation.
- Death::Attach and DamageResolver::FindOrAdd return an existing component without resetting its mode/config. Local no-duplicate creation is not proof of zero repeated-callback side effects. Pin actual helper implementations if quoting their guards; Codex independently read Death.cpp41–56 and DamageResolver.cpp20–34. AddFootsteps is in the pinned subsystem. Preserve Death-before-Look/Legend-last source order without claiming new proof of BeginPlay/tick order or all ragdoll/cosmetic effects.

## Future witnesses

Attach is private: use actual triggers or identify a future authorized fixture seam, not an existing external API. Compare added/retained component identities/classes with known fixture preconditions, not exactly21 total boss components or9 total player components. Partial preattachment must retain existing identity/config; do not guarantee20 new components without knowing other initial state. Spawn handler wiring does not prove exact BeginPlay timing. Witnesses remain UNRUN; no fixture asset, callback result or new class policy is established.

AG revise own report in one bounded pass, using the actual probe outcomes. No Codex helper/baseline/live edits, candidate extraction patch, broad audit, engine job, owner interruption, Claude wake or acknowledgment wait. Codex06 documentation now states this exit-code boundary; its receipt intentionally changes while historical receipt remains valid for old bytes. All83 active/A5 parked/P1 design-only/2b+ held. No Codex git actions.
