# DD1 step1: owner decision draft

2026-10-26. Prepared by Codex for Claude to verify and add new runs. **No acceptance decision has been made for you.** This is not approval of source changes or promotion.

## What changed

The three existing builds now have a data catalog and a game-instance-owned snapshot. This makes an extra build id possible without adding a C++ enum. The demonstrated fourth build reuses Sword; it is not a genuinely new weapon or second boss. The intended contract keeps current three-build values, names, order and equip behavior unchanged. [S1,S2,R1]

This is step1 of a larger foundation. Boss/encounter hydration and animation timeline work are staged scaffolds only, not integrated gameplay. P1 remains held. All83 requirements remain required; this milestone does not certify their implementation. [R1,R2,R3]

## Independent verdict and present conditions

**ACCEPT WITH CONDITIONS for bounded three-build editor compatibility. Full spec acceptance and your approval remain outstanding.** [R1]

| Condition | Current status | What is still needed |
|---|---|---|
|1. Typed weapon/reference closure | OPEN | Validate trusted class ancestry and role-correct item/actor/style/ability links; current text-membership check is insufficient. Better resolving negative test is in current source, not full closure. Exact export request X140, test spec R4. |
|2. Game-instance ordering/travel/isolation | OPEN | Real first-consumer ordering, same-GI travel, two actual GIs while one tears down and other equips. Pure context tests are not that proof. |
|3. Selector focus/diagnostics/viewport | OPEN | Ordered focus, once-only absent-icon/overflow diagnostics, real constrained-viewport render/input proof. Geometry formula tests do not close these. |
|4. Cold packaged data loading | CLOSED for Development only | Cold data epoch and seven staged catalog assets observed. Shipping source selection remains unproved because logs are stripped; whole-package material quality still fails checker. |

The statuses above are Codex's direct review, not a summary of an agent's assertion. Later Claude evidence must be independently reviewed before changing them. [R1,R5]

## What the evidence actually supports

- Historical final step1 editor gate40/40, including catalog91/91; original build witnesses103/20/8/18/7. Automation summary41/41. Those results belong to their recorded binary; later scratch/test edits do not inherit that full gate automatically. [E1,E2]
- Archived Development launch is really Development with command `-nosound -log`; line847 publishes source=data. Separate forced-legacy run publishes another epoch. Both contain19 material errors; neither is a clean package-quality pass. [E3,E4,R5]
- Seven catalog uassets appear in the stage manifest. Inclusion is not by itself proof of runtime source or that all three builds equipped in that packaged run. [E5,R5]
- Source contains C140's extra nonlegacy probe: structural-only accept followed by resolving rejection with named field. Fixed ABI and typed graph-role proof remain missing. [S2,R1]

## Your three choices

| Choice | Meaning | What it unblocks |
|---|---|---|
|Accept the bounded step1 milestone now | Accept demonstrated three-build editor compatibility and Development loading, recording conditions1-3 and Shipping gap as unresolved. This is an explicit limited acceptance, not full compliance. | May authorize further staged preparation. To apply step2/3 scaffolds, separately approve exact scope and accept their documented limits; their missing adapters/importer/fixtures still prevent complete product promotion. P1 stays held unless you explicitly release it. |
|Accept after conditions1-3 close | Ask Claude/Codex to complete/review typed closure and real GI/UI proofs first, then decide on the full step1 package. | Once accepted, may authorize reviewed step2 then step3 integration. Patches still need missing product pieces completed and their own tests; nothing applies automatically. |
|Hold acceptance | Keep current implementation unaccepted while reviewing evidence or requesting other proof. | Offline review/staging can continue within existing scope; no live promotion or P1 start. |

None of these choices commits or pushes, approves pack edits, grants G4/G5, waives any of83 rows, proves Shipping provenance/performance, or makes a data-only canary complete. [R1,R2,R3]

## Risks in plain language

The catalog checks that references load, but can still mistake unrelated text references for correct wiring; fix before relying on untrusted/new content. Two real game sessions and small-screen keyboard/focus behavior are not fully tested. Shipping has no direct selected-source report. Existing material errors affect package quality independently of catalog loading. Step2/3 patches apply cleanly as scaffolds, but are not complete replacement systems. [R1,R2,R3,R5]

## Evidence index (workspace-relative paths; SHA256 pinned at drafting)

| ID | File | SHA256 / bounded use |
|---|---|---|
| E1 | Claude/Evidence/exports/gate_step1_final_2026-10-26.txt | `d97d839d9f8a2f0cb05769b1abcb267825e4759724fdb2a8c1b6945c2aadbbde`; raw40/40 |
| E2 | Saved/rebuild_step1_wp15.txt (project root) | `310550e6925196bbc64fd162877ef2c3684ea6bdc656c52d85f08446b2415161`;41/41 summary |
| E3 | Claude/Evidence/exports/packaged_dev_data_run.log | `9e0ec4998d3558a179f094435f7e9de470a459983259f0f22a3b1be89ee114a8`; config/command/source-data/material errors |
| E4 | Claude/Evidence/exports/packaged_dev_legacy_run.log | `8e54909101db5c3ede561dd718a68d119a1654c13ffc8cb26c6a0891dce10296`; separate legacy contrast |
| E5 | Saved/StagedBuilds/Windows/Manifest_UFSFiles_Win64.txt (root) | `162e2db07a19a830585afc008387139fcf6f86b4c15c319724bdb4a450c40cd1`; seven package inclusion |
| E6 | Saved/package_dev_catalog.txt (root) | `9d977750e0fd53af940aeb81a078d74c80463141ef67708fefde948343006e5f`; successful UAT |
| S1 | Claude/DD1/STEP1_SPEC_v3_AMENDMENTS.md | `e4ac3bb4691a3b0e31369cf71beb2d0194f2ed5c9fd9389b3cfc605ae8c03b24`; normative obligations, not implementation proof |
| S2 | Source/OneBossFight/Tests/RPGCombatCatalogTests.cpp (root) | `85608695b71f34cddb6eb99640fabf5a3103c4b1282089751ab113b1dc3c70a3`; current C140 probe source |
| R1 | Codex/STEP1_ACCEPTANCE_REVIEW.md | `7d56b8b1e48dff4c1620539bb480b4cf787a50bc40159dc708a149a8300896e4`; per-clause review + Development addendum |
| R2 | Codex/PROMOTION_STEP2.md + concrete scaffold patch | Doc `26fd4db9e6ddcb31aaa4f27427b03178613551b8875470c6a2ffef477a960b27`; patch `79a648d0ea85f7b65e4b5b4bb24b1aa2109de787b52367cf81464a008a0da845`; incomplete hydration scope |
| R3 | Codex/PROMOTION_STEP3.md + concrete scaffold patch | Doc `1da210a360418ed23eff75b07380f7b8c76d406394b1f7a5833ab24a63efe119`; patch `40ef3a0b1bb2da59c885f69289c414753059171545bc55f3fb946fe498ef9d57`; incomplete importer/fixtures scope |
| R4 | Codex/TYPED_ABI_CLOSURE_TEST_SPEC.md | `1ff42eae53e523e46d256a3bdc14d5e25af20aa6d09c75cc08a46ff78d2938b3`; proposed test spec, no implementation/pass claim; X140 exact export request; X-T10 HOLD note |
| R5 | Codex/CATALOG_PACKAGED_PROOF.md | `d493644c23cc2d24349d2d3b55d499a5de8645635ee97abad3ddff855e2b4a39`; Development witness and Shipping gap |

Paths not marked root are under Docs/BossCombatReview/Execution. Mutable evidence must be rehashed before final presentation. Full report paths are deliberately retained so Claude can audit every claim; no screenshot/visual release/performance proof is implied.
