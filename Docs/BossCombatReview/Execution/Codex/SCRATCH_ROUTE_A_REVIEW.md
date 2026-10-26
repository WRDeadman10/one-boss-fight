# X-T3 scratch route (a) review

2026-10-26. Verdict: **accept E-010's narrow feasibility claim, not a production adapter or transaction proof.** No Codex build/PIE. Read live header/cpp, driver, E-010 and run4 raw. Current source hashes agree with recorded SHA256 list: cpp `9bd493ad0954cb2a6bf3db6226f45006d8d753a9283879a9e204606d101deb95`; h `a2130ebfafa61297780d803ec331d2f0151c8c1c4098579242f19f400e2a21de`.

## Concrete findings / limits

1. `RPGScratchRouteA.cpp:29-39`: static Report/sequence/reservation counters are process-global, unbounded and resettable while other worlds may run. Adequate single-driver scratch evidence, NOT identity isolation across worlds, simultaneous bosses, teardown or generation reuse. Production must scope by world/encounter and store terminal state.
2. cpp:68: diagnostic `++NextReservation` is an integer allocation, not acquiring an exclusive reservation. Deny branch before TryActivate at78 demonstrates no call on that branch; does not reserve resources, check cooldown/tag deltas or roll back them.
3. cpp:78-80: task returns immediate Success on activation, not on montage terminal callback. No latent task, AbortTask cleanup, duplicate-play suppression, watchdog or montage-instance identity. Do not promote as execution owner.
4. `exports/scratch_route_a/run4.txt`: #8..14 are a second task pass, ids3/4 while montage before=AnimMontage_1. The driver selects id1/id2 only (`pie_scratch_route_a.py:106-119`), so 20/20 does not assert single activation. E-010 honestly discloses repeat; controller restart cause remains unproved. X-T5 will distinguish normal BT looping from explicit controller restart.
5. Driver:86 waits for PACK_RESULT; `or "REJECTED" in ... and False` can never terminate on rejection alone. A legitimate all-denied scenario waits full timeout. This is test-harness noise, not gameplay failure. Use an explicit expected terminal report when extending the proof.
6. `run4.txt` begins `editor exit code: -1` but ends RESULT20/20. Treat as driver behavioral assertions, not proof of clean process exit. Do not turn expected editor stop into unexplained crash without wrapper evidence.

## Clean checks

- cpp:90-147 authoring is WITH_EDITOR, scratch-prefix guarded and refuses existing disk packages; creates new tree, not overwriting pack tree.
- cpp:159-173 sets typed EnemyInfoRef on a deferred-spawned test boss BEFORE FinishSpawningActor; does not mutate placed boss or components in PIE.
- Header reflected declarations and generated include ordering are conventional; Build.cs includes AIModule and editor AssetRegistry/UnrealEd dependencies. Existing reported build is evidence of editor compilation, not a new packaged Shipping check.
- cpp:61-66 report records actual controller, tree and board at task entry; raw run4 shows project BT + pack BP_BaseAIController + BB_Base, stronger than merely reporting assigned Info.
- cpp:73-78 deny path returns before pack call; raw run4 id1 montage none before/after. Explicit scope: no observed montage mutation, NOT no ability-tag/cooldown side effects universally.
- Existing E-010 limitations correctly exclude exact attack variant/section identity, outside-tree starts, abort/finalization and placed-map override.

## Next required proof before P2

World/actor/generation identity; exclusive request policy; exact engine montage instance/variant before play; deny tag/cooldown snapshots; duplicate-root-pass handling; all outside-tree start paths; interruption/death/reset cleanup exactly once. G3 scratch approval does not authorize this product work.
