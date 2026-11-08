# AD-C36–C40 — Release gate and readiness audit

Date: 2026-11-07. Static documentation/mailbox audit only. Codex did not run Unreal, build, cook, package, Editor, PIE, tests, or benchmarks.

## Evidence boundary and authority

Latest relevant mailbox evidence read for this batch: C-988, C-989, C-990, C-991, X-1401, and this batch's X-1402 Antigravity status ping. C-989 corrects C-988's saved-asset readback: exactly one of five montage assets matches the intended table. C-991 accepts X-1400, orders continuation from AD-C31+, and asks for a one-line Antigravity status ping; X-1402 records that status request. No newer Lead verification, owner decision, or asset correction receipt is present in the checked mailbox tail. Absence of a receipt is not evidence of completion.

## AD-C36 — refreshed milestone gate matrix

| Gate | Accountable party | Current evidence/state | Close condition / dependency |
|---|---|---|---|
| GATE-01 Source/build | Lead owns compile/native verification; Codex source/docs; owner commits | Historical BUILD-241..248 receipts remain distinct; latest listed is BUILD-248 484/484 plus Shipping compile. No newer build identity/result in the checked tail. | Lead supplies revision/build ID, native suite output and Shipping outcome for the chosen current revision. |
| GATE-02 Animation/content | Owner approves visuals/assignment; Antigravity authors; Lead verifies UE/import/runtime/package | C-989 records the earlier 1/5 state. A-597's new Lead lines show the four C-988 repair criteria and GuardCounter trace present. The separate AA-A08 GuardCounter FootStep target is absent from that readback. C-985 recoil/aura previews and ER clips remain owner-review evidence only. | Resolve the FootStep/table discrepancy; owner visual review and explicit assignment; Lead PIE and staged-package proof. |
| GATE-03 Runtime behavior | Lead owns PIE; owner confirms product intent | C-978 closes only post-air grounded R1/R2 restoration on tested routes. C-980 invalidates earlier moving-dodge samples; corrected probe requires Lead rerun. C-986/C-988 notify state means hit/iframe/cancel proof on corrected saved assets is absent. Death/reset montage lifecycle remains unverified. | Corrected both-route moving probe with nonzero speed/input; notify-dependent hit/iframe/cancel checks; lifecycle checks; retain raw logs/build identity. |
| GATE-04 Performance/render default | Owner controls resumption and quality decision; Lead measures | Phase 1 has 13 accepted measured runs; C-951 selects Performance/50% as experiment base. C-954 parks Phase 2. No Phase 2 run or shipped-default change. | Owner explicitly unparks; Lead runs authorized treatment and supplies measured performance plus image-quality review; owner decides shipped default. |
| GATE-05 Test quality | Lead owns native/build evidence; Codex offline tools | KI-195 closed with focused timeout fixtures 35/35. This is offline evidence, not native/PIE proof. BUILD-248 remains historical. | Lead provides current native/build gate for selected revision; keep offline, native and runtime evidence separately labeled. |
| GATE-06 Cook/package/release identity | Lead owns cook, stage, smoke and gameplay route proof; owner accepts product | BUILD-246 CookCoverage and BUILD-248 Shipping compile are historical and do not establish current staged package/gameplay. KI-197 documents shared stage-root ambiguity, without asserting contamination. | Configuration/build-specific stage identity and manifest; current CookCoverage; staged smoke; separate data-default route and player-controlled gameplay capture. |
| GATE-07 Evidence registry | Owner reviews; Antigravity maintains media/registry; Lead verifies UE/runtime | C-989's “C-988: 1 of 5 match” is historical. A-597's five new Lead lines show the C-988 repair criteria on all five montages; the GuardCounter FootStep proposal remains unconfirmed. Owner review, runtime and cook are separate statuses. | Resolve FootStep/table discrepancy; record owner review/assignment separately; then Lead verifies runtime/cook and packaged presence. |

## AD-C37 — KI-191–KI-196 source/status drift audit

- **KI-191:** status remains open. Development-only Tier 2 distortion loading is conditional at BeginPlay; cold-start/load and actual UE appearance remain unmeasured. Look-target/preview delivery is not owner approval or runtime proof.
- **KI-192:** status remains open. C-971's 0.36 s route split is game-tick-bounded and not physical input latency/root cause. The legacy/data values and unchanged 0.35 s threshold remain accurately scoped in the issue. No new probe was found.
- **KI-193:** remains open. A-597's new Lead readback shows the four C-988 repairs and target notify rows; the proposed GuardCounter FootStep row is absent. Owner review/assignment, PIE and package gates remain.
- **KI-194:** resolved only for C-978's tested post-air grounded R1/R2 restoration routes. No extension to death/reset, field assignment, or other lifecycle cases.
- **KI-195:** closed for the audited offline test-subprocess boundedness scope; all formerly unbounded calls were bounded and focused fixtures passed 35/35. The remaining direct calls listed in the issue have explicit timeouts. Reopen only for a new unbounded call.
- **KI-196:** open. C-980 identifies invalid earlier standing-tap samples; corrected probe source exists, but corrected Lead PIE remains absent. Do not treat source correction as probe acceptance.

## AD-C38 — release evidence and unresolved dependencies

Release evidence is layered: source/native compile; owner-approved content; runtime behavior; performance/image quality; cook/stage/package identity; and player-controlled packaged gameplay. The current receipt set does not close overall release readiness. In particular, BUILD-248 compile is not a current package; accepted clip delivery is not owner approval; preview acceptance is not UE runtime verification; offline tests do not replace native tests; a successful smoke is not gameplay; and historical Phase 1 numbers do not satisfy the parked Phase 2 decision. The source/config stage-root issue KI-197 must be resolved or controlled with explicit stage identity before treating a staged artifact as unambiguous.

## AD-C39 — GATE-07 terminology check

Use these distinct terms in the registry: **delivered** (artifact receipt), **trim/readback verified** (saved timeline/duration evidence), **accepted for owner review** (Lead/Claude delivery gate), **owner approved** (explicit owner visual/product decision), **assigned** (explicit field/asset wiring authorization), **runtime verified** (Lead UE/PIE result), and **cooked/staged verified** (asset presence in identified package). C-989's 1/5 finding is historical; A-597's new readback shows the C-988 target rows across all five assets. The GuardCounter FootStep target is still absent from the output, so full table matching is not claimed. The Tier 2 previews remain accepted for owner review; final visual approval, assignment, runtime, and cook are unresolved. These distinctions are reflected in GATE-07 and KI-193; older AC-C41–C45 rows remain a dated snapshot, with this section superseding their animation status.

## AD-C40 — owner-controlled decision sheet

Prepared separately at `AD_C40_RELEASE_READINESS_DECISION_SHEET.md`. It lists evidence, dependencies and owner decision fields without selecting a release option or changing any product setting.

## Later receipt update — A-597

A-597 arrived after the AD-C36–C40 batch post. C-992 accepts its five Lead output lines as 5/5 table match; C-993 says GuardCounter's absent FootStep row is cosmetic and requires no change. C-992 separately reports a live zero-damage ER air-attack failure and orders the AA-A08 property/timing/blend-in hotfix. A-597's 426 OK / 1 skipped / broken_links=0 offline result remains mailbox-reported because no raw suite summary was attached. No post-hotfix runtime pass, owner approval/assignment, or cook result is included.
