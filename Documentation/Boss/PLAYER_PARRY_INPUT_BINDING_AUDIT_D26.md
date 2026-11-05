# Player parry input binding audit (Queue D26)

Scope: source-level bind, retry, replacement, and teardown map for `URPGPlayerParry`. No live controller readiness is claimed; no code/tests/build/Editor/PIE run.

## Attachment and binding flow

1. The game-world `URPGPlayerMovesSubsystem` handles pawns already present at world begin play and later actor spawns (`Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:48-80`). `Attach` recognizes the pack player by Blueprint-generated class ancestry (`:83-94`) and find-or-add registers `URPGPlayerParry` (`:254-303`, specifically `:280-283`). This is pawn-class attachment, not proof of possession or input readiness.
2. The parry component enables ticking and stores a soft object path to `IA_Parry` in its constructor (`Source/OneBossFight/Player/RPGPlayerParry.cpp:17-22`). `BeginPlay` calls `TryBind`; if it fails, `TickComponent` retries every tick while `bBound` is false (`:24-42`). This covers an input component/action becoming available after component BeginPlay at source level.
3. `TryBind` requires an `APawn` owner, casts that pawn's current `InputComponent` to `UEnhancedInputComponent`, synchronously loads `IA_Parry`, binds `ETriggerEvent::Started` to `OnParryPressed`, then sets `bBound=true` (`:49-62`). The binding code does not install an input mapping context; it assumes action mapping is provided by the surrounding player setup.
4. `OnParryPressed` calls `Press` (`:64-67`). The press path performs configured stamina validation/cost first; on an accepted window it raises the owned pack parry tag and records the press (`:69-108`). This audit makes no claim about which controller, mapping context, or hardware produces the action event in a live run.

## Replacement and teardown boundaries

- The component retains `bBound`, not the bound input-component pointer or a binding handle. It has no controller-change delegate, input-component replacement check, or explicit unbind call. Once `bBound` is true, the tick retry branch no longer calls `TryBind` (`:30-42,49-61`). If the pawn's input component is replaced after binding, the source does not attempt to bind the replacement; whether the binding remains effective depends on engine/controller lifecycle and is unverified.
- `EndPlay` retries any pending stamina refund/rollback and owned parry-tag removal up to five times before calling `Super::EndPlay` (`:182-186`). It does not explicitly remove the Enhanced Input action binding or reset the parry timing state. No conclusion is made here about delegate safety after UObject teardown.
- While active, the component closes its owned `Status.ParryActive` tag once the rule window expires and then finishes pending cost/refund handling (`:30-42`). Failed tag removal preserves the ownership flag for later tick/EndPlay retries (`:189-200`).
- The world subsystem's `Deinitialize` removes only its actor-spawn handler (`RPGPlayerMovesSubsystem.cpp:68-76`); it does not walk pawns to unbind parry input. Component lifetime cleanup belongs to actor/component teardown.

## Test evidence and gaps

`RPGParryTests.cpp`, adjacent cooldown/window tests, and cost/grade tests exercise pure rule behavior; no test directly exercises `URPGPlayerParry::TryBind`, an Enhanced Input binding, controller replacement, or unbinding. `RPGPlayerMovesAttachWitnessTests.cpp` records component registration order but its own comments explicitly say a bare world does not witness actor BeginPlay chronology (`:8-11`); attachment presence does not prove a successful input binding.

Bounded next checks, if runtime fixture access is approved: (1) spawn a pawn with no input component, then install an Enhanced Input component/action and verify the tick retry binds once; (2) replace the component/controller after successful binding and verify whether the new component receives one press; (3) tear down while the window/tag/refund is pending and inspect cleanup. Setup failures must be reported as blocked, not passes. Keep live input readiness UNKNOWN until one of these checks runs.

## Conclusion

The implementation retries until first successful binding and performs bounded tag/refund cleanup at EndPlay. It has no explicit input-binding replacement/unbind lifecycle. That is an unverified lifecycle boundary, not a reproduced user-facing failure. No production change proposed from static inspection alone.
