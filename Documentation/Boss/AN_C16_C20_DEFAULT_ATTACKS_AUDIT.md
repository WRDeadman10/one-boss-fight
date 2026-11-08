# AN-C16–C20: Default-Wired Attack Source and Evidence Audit

Status: offline source/documentation audit complete. No gameplay Source or content changed. Lead owns native build, PIE and package evidence.

## Source path map

- `RPGDodgeTiming.cpp:536-573` binds the Elden Ring R1/R2 actions and, while each short injection window is open, injects the pack's original light/strong actions. The source does not directly play the ground attack montage. Thus grounded R1/R2 behavior is determined by the pack arrays/default route; C-1042 is the relevant default-wired live receipt.
- `RPGDodgeTiming.cpp:578-594` handles R1. On a newly triggered input only, it checks `IsFalling()` and the optional AirLight route; when selected, it transiently replaces the pack's `FallingAttackMontages` array with the AirLight montage and records JumpLight semantics. Grounded R1 does not enter this replacement branch.
- `RPGDodgeTiming.cpp:597-628` handles R2. A recent successful guard first selects the counter path. Otherwise a new heavy input checks falling state and optionally replaces `StrongAttackMontages` with AirHeavy / JumpHeavy. Grounded R2 does not enter the air override branch.
- `RPGDodgeTiming.cpp:759-857` snapshots each matching pack array before replacement, inserts the selected montage, records the active override kind and sets a one-second fallback deadline. A failure to apply an override restores prior arrays.
- `RPGDodgeTiming.cpp:860-919` restores the serialized array contents when montage playback begins, while retaining semantic override identity until montage exit; it also restores on expiry or missing montage. BeginPlay/end-play cleanup is handled at `RPGDodgeTiming.cpp:53` and `:918`.
- `RPGSwingTracker.cpp:183-215,228-264` classifies the actual montage, prefers an active override identity, then falls back to pack montage arrays; it records the swing and table row at montage start.
- `RPGHitIntake.cpp:362-407,568-612` records the current montage and override kind at hit time, resolves the canonical attack-data row for the override kind, and records hit/damage attribution. This source mapping is not itself proof that a montage reaches the target or causes damage.

## Evidence reconciliation

- Default-wired proof: `Documentation/TEST_PLAN.md` C-1042 row and `Docs/BossCombatReview/Execution/Claude/P_C1042_DEFHITS/`. Lead reports no runtime montage assignment, both routes, ground R1/R2 `Attack_PrimaryA` / `Ability_E`, and air R1/R2 `AM_ER_Attack_Air_Light` / `AM_ER_Attack_Air_Heavy_Plunge`, with respective HP changes about -15.99 / -22.386. This closes the live default-wired hit sample recorded there, not package acceptance or broader combat balance.
- Older C-1004/A-607 proof in `P_C992_AIRHITS` used runtime-assigned air montage arrays. It remains useful historical comparison and must not be cited as default-wired proof. Its r5 result was correctly distinguished from `run5_probe_*` r4 backups by C-1024.
- `RPGAutomationTests.cpp:1228-1232` checks that the four default soft montage references load. `test_air_attack_wiring_contract.py` checks the two air asset path literals, expected pack-array names, rule selection, injection windows, and override backup/restore calls. These are load/source contracts, not runtime montage selection, hit, or cook tests.
- `RPGAutomationTests.cpp:1368-1393` describes and begins the cook-coverage path scan. `TEST_PLAN.md` requires the Lead native CookCoverage run and staged-package asset verification. The source/ini directory coverage and C-1042 PIE do not establish a packaged runtime.

## C18–C19 review result

No demonstrated gap justifies adding another test: the source contract, native load assertions, and Lead C-1042 receipt cover distinct layers. Keep the four states separate in review records: owner visual approval, saved asset/readback, runtime behavior, and package/cook. In particular, C-1042 runtime hit evidence does not mark the package gate accepted.

## Open gates

Keep KI-193 package/cook acceptance open until a Lead records CookCoverage plus staged-package asset/runtime evidence. Ground and air hit samples remain scoped to the C-1042 setup and two routes; no claim is made here about other weapon styles, all attack traces, or release performance. Codex ran no native build, Unreal Editor, PIE, or package operation for this batch.
