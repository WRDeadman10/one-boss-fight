# DD19: typed Bleed profile, SOURCE ONLY

Claude: C250 is accepted within Codex/C250_DD17_DD18_VERIFICATION_ACCEPTANCE.md. Proceed with actual code for the next remaining consumer profile; do not wait for routine acknowledgment or substitute another planning document.

Allowed delta: THREE NEW files Player/RPGBossBleedAdapters.h/.cpp and Tests/RPGBossBleedAdaptersTests.cpp, and existing ONLY Player/RPGEncounterBinding.h/.cpp. Capture exact preimages and full current191 Source manifest before editing. Final expected194 files; all189 preexisting files other than Binding.h/.cpp stay byte-identical. Native RPGBossBleed.h/.cpp, RPGBleedRules.h, PlayerMoves, existing adapters/planners/tests, assets/Config/Scripts remain unchanged. No engine/build/UHT/automation release until actual five-file diff/test/pin review.

Implement reflected FRPGBleedConfig (use this exact new name unless a source collision requires reporting before edit), a Bleed property on URPGBossDefinition and corresponding immutable compiled participant config copy. Seven fields, copied and assigned without Value parsing:

- InitialThreshold, ThresholdIncrease, ThresholdMax, HpFraction, EffectHeight.
- ProcEffect (TSoftObjectPtr<UNiagaraSystem>), ProcSound (TSoftObjectPtr<USoundBase>).

Declaration defaults match actual current RPGBossBleed constructor/header:100,20,200,0.03,170 and the exact existing effect/sound soft paths. They are additive authoring defaults ONLY, never invalid-input substitution. Existing fixture definitions can retain defaults; no fixture/test cleanup or migration.

Provide shared ValidateBleed and exact-class lifecycle-safe ConfigureBleed/MakeBleedPlan using the accepted FRPGComponentPlan contract and native instance name RPGBossBleed. Required manifest paths explicitly Bleed.<each of seven fields>. Validate ALL before any write. Reject invalid/destroying component, wrong class, registered/begun component, absent/invalid/destroying/begun owner. No runtime state, loaded refs, counters, threshold seeding, attribute writes, timers or proc operation. Validation and assignment never load assets.

Numeric authoring contract: all five finite; InitialThreshold >0, ThresholdIncrease >=0, ThresholdMax >= InitialThreshold, HpFraction in [0,1]; EffectHeight finite and signed (do not invent a height floor). This is a structural authored contract, not a balance retune, and the editor's ClampMin1 is not a mandatory runtime minimum. Reject bad values by field name, do not clamp. Soft refs must be non-null structurally valid object paths appropriate to the typed properties; class resolution/cook/VFX/audibility remain unproved until a separately released load. Preserve actual native behavior and existing defaults.

CompileParticipant uses the shared structural validator, then copies the typed record; no synthetic bypass of scalar/required structural checks. This fragment is NOT inserted into current five-plan preflight/preparation or registry and does not turn it into a complete playable bundle.

New tests must cover reflection/schema/default declaration and compiler copy, actual nondefault assignment of all seven fields (including negative height and zero-valid increase/fraction), boundaries/nonfinite/invalid refs, complete no-write on a late invalid field, exact required-path set and callback behavior, wrong class/component/owner lifecycle and isolation of unrelated native configuration/state. Follow accepted synthetic dev-only config contract for callback fixtures. Do not call AddBuildup/BeginPlay/proc or add fixture cvars.

Deliver actual source/diff, preserved preimages, full194 manifest, five live/Review pins and receipts. No automatic compiler-fix rounds or assumed test totals. No asset creation, engine operation, registration, startup wiring, target/reset/Ready/activation, legacy suppression, package or git release. All83/networking remain required; A5 remains parked.

Antigravity continues X291 staged toolkit corrections in parallel. DD19 adds a future reflected record; do not silently include its unreviewed schema into a claimed frozen toolkit revision. Publish your exact implemented schema pin and unresolved future-profile boundary. Codex maintains independent evidence and native-contract tooling while both lanes execute.
