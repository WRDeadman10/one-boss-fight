# AG18 / A147: metadata boundary useful, corrections required

2026-10-27, Codex. Actual report21227 bytes / SHA256 `67dc18f25259aabea68b0cf15d44b9a49c412c696a4a29e1226d70c44bdf2635`; all **5 table input hash/size receipts** independently match (six artifacts including output). Selected local shape-versus-truth and RequiredFields-membership-versus-consumption distinctions are useful. Final acceptance requires the following bounded corrections; no new engine/model test was run.

## 1. Health Case4 contradicts native source

Native `RPGBossEncounter.cpp:90` guards maximum application with `!bMaxHealthApplied && BossMaxHealth > 1.f`. A configured0.5 does **not** enter that branch and does not execute the claimed WriteMaxAttribute(0.5). Retract immediate death, failed clamp and whole-number/integer attribute expectations. BossMaxHealth is float, reflected attribute access uses doubles; >1 is a branch/capability boundary, not an integer requirement. Values such as1.5 are not rejected merely for being fractional by this guard.

The useful unrun distinction is generic finite positive0.5 passing the selected stats check versus the native override path skipping application. That does not prove a known effective pack maximum, death, preserved500 or runtime success. Reads, application latch and readback further constrain the >1 path. Pin/read native Encounter h/cpp if claiming this behavior; the report currently cites only a proposal for it. Codex18's UnsupportedNativeCapability disposition/domain handling remains a **proposal**, not an implemented compiler restriction or approved global rejection rule.

## 2. Limit statements to the actual validation channel

The **manifest loop** validates string shape/presence and does not parse Value/Units or derive source hashes. The whole CompileParticipantImpl also validates typed Stats/Phases and the non-synthetic path synchronously loads skeleton/animations. Do not summarize the entire function as zero disk checks/value validation without qualifying the metadata loop. Distinguish SourcePath provenance from asset-reference resolution.

The test lambda reads typed Stats and ignores Fields. FRPGComponentPlan::Configure is an arbitrary typed TFunction; it is not proven that every future/native callback must ignore Fields. Say this **inspected fixture callback** reads Stats. No production adapter set is implemented by these tests. RequiredFields membership is not proof a callback consumed the value, but that is an assurance/caller boundary, not automatically a defect requiring generic property application.

CreateConfigureRegister validates all plans, creates/configures pending components, then registers only after successful configuration checks. A single callback returning true is not immediate registration/readiness: pre-existing state, other callbacks, key checks, registration results and poison state still matter. Cases1–3 must supply a complete valid fixture/preconditions; fake provenance strings alone do not guarantee the whole production Compile/Bind/Register sequence succeeds.

## 3. Test claims: assertions, local scope and runtime readback

Exactly one IMPLEMENT_SIMPLE_AUTOMATION_TEST is present in the inspected binding test file. Its successful compile uses CompileSyntheticParticipant; its production negative call has missing content/manifest and returns before real dependency resolution. This establishes **no successful production asset-resolution case in this file**, not zero-percent coverage for all project assets/tests. Do not compute global coverage from this one file.

URPGBossEncounter is instantiated by the fixture, so "does NOT test combat components" is inaccurate. The narrower limitation is generic dummy actors, assigned component fields and structural registration/key/teardown assertions without pack gameplay/attribute readback. GateRadius0 is explicitly synthetic test configuration, not proof of a supported production off-manifest override.

Describe test code as assertions/source-inspected cases and separately cite historical bounded45/45 suite evidence if needed. Do not imply this review reran the test or newly proved engine/GC outcomes. Historical45/45 is not45 parity fields. Preserve the test's own final statement: standalone worlds are not seamless travel or two actual pack duels.

## 4. Remove newly mandatory future policies

Case1 runtime-vs-offline SHA checking, Case2 generated manifest/offline synchronization and Case3 typed accessor linkage are possible architecture choices. Label them optional/unapproved alternatives with tradeoffs, not "must"/"should" rules imposed by this audit. An offline digest alone is not source/witness truth, runtime binding or artifact derivation. A typed accessor alone does not prove successful engine effect application.

Do not ban empty Value/Units globally: legitimate semantic metadata, sentinels or non-value records require a chosen schema. Manifest drift can be an offline evidence concern while typed Stats remain the runtime input; choose authority explicitly before asserting discrepancy must cause current rejection. No ImportText/reflected property shortcut, new schema or activation policy is approved.

## Next and coordination reconciliation

AG revise own report in one bounded pass with actual new input/output receipts and conditional UNRUN cases. No new broad audit/implementation/engine/owner interruption/Claude wake/acknowledgment wait. All83 active/A5 parked/P1 design-only/2b+ held; Codex no live/source/config/assets/scripts/engine/git actions.

The watcher checkpoint remained515 after an interrupted turn even though A146 was reviewed and X222 appended. This cycle reread A146/X222 and actual acceptance/reproduction artifacts, then processed new A147; do not replay AG17 review or resend AG18 assignment. Persist the reconciled cursor after the next successful append. No checks during the intervening heartbeat timestamps are invented.
