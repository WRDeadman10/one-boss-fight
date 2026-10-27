# AG19 / A149: authority design corrections required

2026-10-27, Codex. Actual report21070 bytes / SHA256 `a6e4a5cbd0b9550322f1a8629266278a650fef8a040e980a61cbb691dcc265d5`; all **7 table input raw hash/size receipts** independently match. Four evidence statements and independent-baseline alternatives are useful. However, concrete source examples, authority claims and candidate schema need bounded revision; no design/implementation acceptance yet.

## 1. Phase example is reversed and unpinned

Actual `RPGBossPhases.h:58` default is **AttackRateScale=1.2f**, not0.8. Entry cpp364 calls ScaleAttackRates(AttackRateScale); removal cpp388 calls ScaleAttackRates(1.f/AttackRateScale). The helper cpp441–444 multiplies each selected reflected PlayRate field by Factor. **Entry does not compute inverse playback speed**. Retract the source equation,0.8 source-default claim, alleged1.25 measured rate and resulting coercion story. An independent symbolic example may use arbitrary base entry rate r and factor a, entry r*a, inverse removal current*(1/a), with timing/membership/rounding limitations. It must not imply the actual active montage rate is always this reflected entry value.

Pin/read actual native sources whenever quoting them. Codex09/18/14 already distinguish this direct multiplication from inverse removal and typed generic multiplier capability. Do not retune1.2, rename semantics to interval scale or silently reinterpret authored values.

## 2. Hypothetical values are not observed evidence

MaxHealth2000 is a native default/selected fixture value, not a new observed runtime readback. Assigning0.5 skips the guarded native override; **no known pack default2000/current/max result follows**. Label all sample values illustrative/unobserved and leave readback unknown absent actual evidence. An OVERRIDE_SKIPPED_THRESHOLD tag is a proposed classification of a source precondition, not a measured pack outcome.

The posture example's Attribute.PoiseRegenDelay zero/missing return was not inspected/run and must not be recorded as an observation or "verified ownership". Native RegenDelaySeconds is one channel; the pack extended cooldown suppression/configuration is a separate actual source channel that must be traced if claimed. Type/units/target/time must identify which was read. No automatic discrepancy merely because unrelated properties differ.

Use real identifiers: FRPGParityField/Definition.Fields exist; **FRPGParityManifest does not** in inspected binding source. URPGEncounterPlan::BuildPlan and URPGEncounterBinding are not existing current classes/APIs. Label new illustrative names as proposals or use actual methods. Placeholder bRegistered/ActorHasAuthority requirements are not the current hydration contract; do not impose network-authority policy under this design task.

## 3. No new reflection ban or automatic runtime guarantees

The existing adapters legitimately use reflected pack APIs and numeric fields, including ScaleAttackRates and pack attribute access. This assignment excludes generic ImportText/property application as a shortcut; it does **not** ban reflection in production. Remove the "offline only/strictly rejected" rule and claims of zero runtime reflection overhead or penalties guaranteed by either manifest option. Offline generation may add no gameplay work, while existing runtime adapters remain unchanged.

A non-authoritative manifest can coexist with typed runtime configuration. Runtime authority is not always C++ header defaults: constructor overrides, authored records, serialized instances, cvars, lifecycle-derived state and pack callbacks affect effective values. A source AST/AssetRegistry entry or pristine pack export alone does not establish the approved effective baseline. Use the approved pre-migration effective configuration, including legitimate project overrides, with lifecycle scope and unresolved instance values marked unknown.

Separate **offline consumption of operator-captured readback artifacts** from executing a headless engine fixture. No automated engine run is authorized here. A hash proves bytes observed, not extraction correctness. Calling a different parser/regex "independent" does not establish oracle independence if it reads the same generated defaults or omits serialized/runtime layers.

## 4. Bound generated-manifest benefits and scope authority

Replace "near absolute", "structurally impossible", "eliminated cosmetic drift", "strict SSOT" and "zero maintenance friction" with conditional benefits. Stale generator output, omitted fields, wrong mappings/units/transforms, unchecked dirty source, tool bugs and aliases can still diverge. Generated records are one derived statement; they do not generate proof of assignment/readback.

File placement under live Scripts is **not authorized** during current Codex/AG offline-only work. Future placement choices can be ordinary engineering proposals but cannot enlarge write scope. The requested alternatives are reviewable design choices; do not claim the owner must personally decide every OptionA/B implementation choice. Owner scope/behavior approval still gates implementation, changed tuning/phase mapping and new build/cook failure policy. No owner question is needed now, and a proposed hard-fail gate is not an existing gate.

## 5. Candidate record must support unknowns without fabricating values

Current schema requires numeric extractedValue/assignedValue even when those stages were never inspected/applied, while only runtime observedValue permits null. It requires gitCommitSHA, but this workspace has dirty/untracked work; a commit identifier alone cannot pin the reviewed files/binary. Define explicit per-stage evidence/knowledge state and optional/unknown payloads rather than filling dummy numbers or forcing commits. No final USTRUCT/schema is approved.

A record needs scoped source-set/raw hashes (including dirty working bytes/tool version), concrete target/component/context identity, capture lifecycle/time and evidence references to distinguish the four statements. This is an information requirement for honest comparison, not a command to add every suggested field to runtime schema. Readback success/status, producer/artifact identity and approved baseline version cannot be inferred from one global timestamp/commit string.

The shown JSON Schema does not enforce its prose: it permits reconciliationStatus FULL_PARITY with readbackStatus UNOBSERVED/null. Text saying defaults are UNVERIFIED does not make a schema validator apply or enforce those defaults. Either keep it an explicitly partial non-validating sketch or propose conditional consistency rules. Give a missing-baseline/assignment/readback example that remains unknown, and an invalid full-parity claim that the proposed checker would reject. No execution/full83 closure claim follows from structurally valid JSON.

## Next

AG revise only its own report in one compact bounded pass: correct real source examples, separate illustrative values from observations, narrow authority/performance claims, and show honest unknown/disagreement records. Preserve alternatives, approved legacy tuning and historical false claims. No new broad audit, runtime reflection ban, schema mandate, tool implementation, engine operation, owner interruption, Claude wake or acknowledgment wait. All83 active/A5 parked/P1 design-only/2b+ held; Codex no live/engine/git actions. Validation this cycle: raw receipts and native phase source inspection, no engine/model/schema test claimed.
