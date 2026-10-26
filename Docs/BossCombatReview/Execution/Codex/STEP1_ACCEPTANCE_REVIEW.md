# DD-1 step 1 acceptance review

2026-10-26, Codex. **Overall: ACCEPT WITH CONDITIONS for the three-build editor compatibility milestone; NOT full v2/v3 acceptance and NOT promotion authorization.** Conditions below must close or receive an explicit owner-approved spec deviation before Claude presents full completion. Owner acceptance remains separate. P1 remains held.

## Evidence and method

Read v2 and v3 amendments; current catalog, loadout, UI and tests; compare stored BuildSelect preimage with live source. Gate raw `Claude/Evidence/exports/gate_step1_final_2026-10-26.txt` independently read/hash-checked: SHA256 `d97d839d9f8a2f0cb05769b1abcb267825e4759724fdb2a8c1b6945c2aadbbde`, 40/40 rows. `Saved/rebuild_step1_wp15.txt:50`: 41 finished/41 passed. These are Claude's runs, not Codex execution; final DLL pin is baseline supplement6, not a hash of today's scratch-modified DLL. No claim of fresh current-binary full gate.

Step0 supplements classify 36/39 old passing rows, two stale dormant-idle assertions and the WakeClip0 loop-stop defect. Final gate: soak213/213, death-reset25/25, damage17/17. Do not erase the earlier failures or call the original baseline clean. Three-build witnesses103/20/8/18/7 have unchanged counts. The new catalog91-check driver does NOT prove actual constrained viewport focus, travel, or simultaneous game-instance equip isolation.

## Per normative spec line

PASS = implementation + bounded evidence; PARTIAL = obligation not fully demonstrated; SUPERSEDED = v3 governs. Heading/table-label lines have no independent acceptance predicate.

| Spec line | Verdict | Basis / remaining obligation |
|---|---|---|
| v2:3 | PARTIAL | Three-build editor parity supported; new-weapon generality is not witnessed; baseline classifications preserved. Historical start gate is not retroactively certified. |
| v2:9 | PASS bounded | Stable id through parse/loadout/HUD; explicit legacy slots; enum99 remains Dex. Fourth fixture shares Sword, not a new weapon. |
| v2:10 | PARTIAL / amended | Value-copy snapshot + strong leases and single publication good. Closure validator gaps below; global restore clause superseded by v3A2. |
| v2:11 | SUPERSEDED in part | Startup modes and preimages used; v3 removes Shipping console/global push-pop/whole-file dirty rollback assumptions. |
| v2:12 | PARTIAL | See row-layout conditions. |
| v2:13 | PASS record | Versioned baseline/supplement exist; historical manifest retained. |
| v2:17 | PARTIAL | No balance/pack edits in step1 scope; real new weapon proof deferred P8. Legacy table remains compatibility view. |
| v2:21 | PASS bounded | New source/test/scripts and seven assets documented; one catalog driver row. Asset values supported by data-mode run, not decoded independently from uasset here. |
| v2:23 | PASS with documented deviation | Redundant write-only Chosen enum removed; legacy public API preserved rather than retaining misleading state. HUD witness consumes GetBuildLine. |
| v2:27 | PASS editor | Raw gate witnesses and automation totals above. |
| v2:28 | PARTIAL | LegacyParity asserts strings/enum/parser; gate supports equip outcomes. No new exhaustive pre-change trace of every requested call-sequence condition. |
| v2:32 | PARTIAL | Keys1..9/mouse/paint use geometry; no extended focus navigation or once-only overflow diagnostic. No actual constrained-viewport proof. |
| v2:36 | PARTIAL | Structural copied-legacy comparisons are not full comparison of independently authored catalog values. Positive resolved test now exists. |
| v2:37 | PARTIAL | Duplicate/reserved/missing-style/weapon covered; negative cook/ancestry/semantic wiring cases insufficient. |
| v2:38 | PASS bounded / amended | Fresh-mode fourth identity/defer/reset/respawn91 checks. Exact covered Sword route is correct per v3C2; do not manufacture fallback or new-art proof. |
| v2:39 | PARTIAL | Editor CookCoverage green; cold packaged load outstanding, procedure X-T8. |
| v2:43 | SUPERSEDED in part | Legacy rollback Development-startup only; restore owned deltas, not blind preimage overwrite. |
| v2:47 | PASS scope record | Claims/preimages present; distinct baseline test fixes and WP15 changes disclosed. |
| v2:51 | RESOLVED | Shipping source switch compiled out. |
| v2:52 | RESOLVED, proof partial | GI subsystem chosen; actual ordering/travel tests remain. |
| v2:53 | RESOLVED, implementation partial | Optional text fallback allowed; missing diagnostic still absent. |
| v3:3 | GOVERNING | Amendments take precedence. |
| v3:7 | PASS source | Non-Shipping controls; GetEpoch late-change diagnostic; Shipping auto policy explicit. No Shipping runtime proof yet. |
| v3:8 | PARTIAL | GI ownership/consumer-held refs/no GWorld good; no instrumented real first-consumer ordering or travel witness. |
| v3:9 | PARTIAL | Broken icon warning at Catalog.cpp:205; null icons skip loop at202, no once-per-entry absent diagnostic. Focus contract unproved. |
| v3:15 | PASS | Complete candidate or complete legacy, reason logged. |
| v3:16 | PASS | Legacy branch skips catalog load. |
| v3:17 | PASS | Strict null epoch disables selector; no lookup fallback. |
| v3:18 | PASS bounded | Startup test invalid fixture guarded; no asset rename. |
| v3:20 | PARTIAL | Two pure FContexts and fresh PIE/late cvar covered, not two actual GIs while one tears down and other equips. No global LIFO. |
| v3:24 | PASS bounded | Per action exact/any/fallback effective values captured at epoch compile; nonexact warnings emitted there, not on hot tick. |
| v3:25 | PASS bounded | Explicit Actions and bRequireExactRows; fourth uses existing exact style. Full authored new-weapon coverage remains P8. |
| v3:26 | PARTIAL, blocking full closure signoff | Full paths loaded, but configurable ItemBaseClass/any UClass ability and combined text membership do not prove typed compatible edges. See conditions. |
| v3:27 | PASS bounded | WP15 ambiguity fixes and tests; verified id drives presentation; shared style still not proof of distinct item identity. |
| v3:31 | PASS procedure, historical capture limited | Stored preimages and shared-row owned delta available; no destructive rollback authorized. Verify hashes immediately before any future reversion. |
| v3:32 | PARTIAL | Shared geometry guards real keys/mouse/paint; focus/once-only logs/actual constrained viewport test missing. |
| v3:36 | SUPERSEDED status only | Later step0 supplements record/classify gate; retain original contaminated run as provenance. |
| v3:40 | Historical gate | Spec review is not retrospective permission; current bounded acceptance does not approve promotion. |

## F5 / F6 / F7 against actual code and preimages

**F5: not a demonstrated regression; AG30's residual wording is incorrect.** `preimages/Source_OneBossFight_UI_RPGBuildSelect.cpp:419` already compared raw argument with chosen display name; current UI:428 does the same. Both delegate to SetBuild. Current Loadout:426 computes bSame using parsed stable id, calls Poll and returns `Same` at433; ReadChoice:549 avoids restarting the transaction. `Pick` returns that result at435, not "requested". Poll may perform normal outstanding work; the alias does not create a redundant new equip cycle. Add an alias-same selector assertion if desired; don't invent a new product defect or claim a corrected behavior change.

**F6: original proposed topology too strict, but not CLOSED.** The pack need not store every dependency on Item. Requiring Item->Ability directly without graph evidence is wrong. However Catalog:188-193 concatenates arbitrary property text from Item, actor CDO and Style and tests substring membership. References in unrelated fields (or strings) can satisfy it; no typed edge identity/role or fixed ability ancestry enforced. Allow actual pack topology, but validate the specific typed property routes. Preimage consumer shows no prior catalog validator; this is a new safety obligation, not a three-build gameplay regression. AG30 "concatenation is required" is not proof of sufficiency.

**F7: not a human-input bypass.** Preimage Pick had no geometry check. Current UI:418 and465 exempt first3 only for programmatic Pick/click hook; actual mouse:162 and keys:184 guard RowVisible for every row. Retain this compatibility test-hook behavior unless owner changes API contract. It does NOT excuse missing actual focus/overflow/constrained-viewport evidence; don't claim headless necessity was experimentally demonstrated here.

## Conditions for full acceptance

1. Fixed expected weapon/ability ancestry and typed compatible dependency routes, plus negative resolving tests that reach that block; X-T1 documents the early structural rejection trap. Assert specific failure text. If deliberately postponing hardening, owner must approve a bounded trusted-authoring-only contract rather than calling v3C3 complete.
2. Real publication-before-consumers instrumentation, same-GI travel, and two-GI teardown/equip proof; pure context tests are not substitutes. EDITOR NEEDED, Claude owns execution.
3. Implement/prove ordered focus behavior and once-only missing-icon/overflow diagnostics, actual constrained viewport test (render/input, not `is_row_visible(3,200)` alone), or obtain explicit spec deviation.
4. Cold packaged source=data proof with no missing-path compatibility fallback before marking board step1 fully accepted. Shipping currently strips logs: X-T8 distinguishes content listing from runtime provenance.

No source edits by Codex. No promotion, P1 implementation, owner acceptance, cook or gameplay tests claimed.

## C-140 concurrent follow-up

Read the revised Resolution test immediately after X-131: a nonlegacy ProbeWeapon/ProbeBuild now passes Compile(false), fails Compile(true), and checks ProbeWeapon + References in the failure text. **The early structural-negative test gap is closed in source.** Claude reports a new41/41 run; this is not the old final full-gate binary and has not been independently rerun by Codex. Fixed expected ABI / typed semantic compatibility remains an explicit condition, not waived by this test.

## C-142 / X-T8 packaged addendum

Archived Development cold logs independently read/hash-checked: data run9e0ec499... line847 source=data; separate legacy8e549091...; stage manifest includes seven catalog assets. **Condition4 closed for Development cold catalog publication.** Both runtime logs contain19 material errors and checker remains FAIL. No whole-package acceptance or Shipping runtime source=data witness. Remaining conditions1 typed closure,2 actual GI/travel/concurrency and3 focus/diagnostics/constrained viewport still open. Details/commands and Shipping provenance gap in CATALOG_PACKAGED_PROOF.md.
