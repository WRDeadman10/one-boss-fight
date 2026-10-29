# DD19 typed Bleed profile: state at the role swap (owner order, 2026-10-29)

Owner: Claude becomes LEAD REVIEWER, Codex becomes IMPLEMENTER and sole editor/build/automation operator. Claude edits no Source from now on. Nothing in DD19 was compiled or run.

## What exists (Claude wrote it against X-293 before the swap; Codex owns it from here)
Five files, all CRLF (0 bare LF), preserved as delivered in `Review/*.delivered_C251`:
- NEW Player/RPGBossBleedAdapters.h (60 lines) sha256 84a899804e0952e716fe87cedfcf09760b5ad334f5081c5302c779ffb39c6375
- NEW Player/RPGBossBleedAdapters.cpp (189 lines) f4e5c94bff50f3774b1b9700db74bf52b7207bac8f605d4165a041ffe0a6cc26
- NEW Tests/RPGBossBleedAdaptersTests.cpp (953 lines) 53c42ce5418d5b926f0e9853fb30a7f82ee0a48964b82e00b85bf5e22c263455
- EDIT Player/RPGEncounterBinding.h (347 lines) 58c4e5758160abad1770aa6c04519a33648196d9d4676b4732d03adcbb948bbb (was ce0a7da7...)
- EDIT Player/RPGEncounterBinding.cpp (373 lines) b4dc5c2654807131f18509949fba033661d2b52e8e197a5c90759f9a37520089 (was c7255051...)
Preimages: `Review/RPGEncounterBinding.{h,cpp}.preimage`; test file before the one-line include hardening: `Review/RPGBossBleedAdaptersTests.cpp.before_independent_review`. Diff: five_file.diff (1289 lines). Manifest: pre 191 files (`pre_source_manifest_sha256.txt`, equals DD18 final), post 194 (`post_write_source_manifest_sha256.txt`); `manifest_diff.txt` = two added files, three changed lines (Binding.h/.cpp, tests added); the other 189 files byte-identical.

## Design as written
FRPGBleedConfig (7 fields, defaults 100/20/200/0.03/170 + the two existing soft paths), `Bleed` on URPGBossDefinition and FRPGParticipantConfig, CompileParticipant calls ValidateBleed then copies. Validator order: all five scalars finite (InvalidBleed.NotFinite), then InitialThreshold>0 (NotPositive), ThresholdIncrease>=0 (Negative), ThresholdMax>=InitialThreshold (ThresholdMaxBelowInitial), HpFraction in [0,1] (FractionOutOfRange), EffectHeight signed (no floor), then ProcEffect, ProcSound required structural paths (InvalidDependency.Missing/Malformed). ConfigureBleed: exact class, lifecycle checks, validate all, then write seven public fields; no state, no load. Plan: class URPGBossBleed, name RPGBossBleed, required paths Bleed.<field>. Not inserted into preflight/preparation/registry.
Six tests OneBossFight.Binding.Bleed.{Assign,Validation,Isolation,Rejections,Compile,Authoring} (expected 6, total 135 only as an expectation).

## Independent pass (read-only sub-agent, supplemental, not an acceptance)
No certain compile error, no wrong test expectation, no BeginPlay/asset load on a bleed component. One low item applied: `#include "Materials/MaterialInterface.h"` in the test file (the one delta from before_independent_review).

## Open / honest limits
Not compiled, not run; the next build runs UHT (new reflected struct). The ComponentBegunPlay guard is NOT executed by the tests (a begun bleed component needs the native BeginPlay, which loads assets): source claim. Pins for Binding.h/.cpp in the DD18 pin files fail by design (edited files); all other pins, candidates and catalog assets verify. evidence_sha256.txt covers this folder as it was at the swap (17 receipts at creation, verifies); it does not cover files edited later.
