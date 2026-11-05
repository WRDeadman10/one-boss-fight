# Queue D136 — pack class-name matching audit

Date: 2026-11-03  
Method: static comparison of name-based pack lookups and configured subclass checks; no asset/runtime reflection.

## Matching modes

- `RPGPack::FindComponentByClassName` enumerates actor components and compares `Component->GetClass()->GetName()` exactly with a literal (examples: `BP_AdvancedAbilitySystemComponent_C`, `BP_AttributesComponent_C`). A derived Blueprint component with a different generated class name does not match. A different class in another package with the same short UObject name could match; this helper does not compare full class paths or base classes.
- `FindAbilityByClassName` requires the exact `GetFName()` on an ability instance in the exact-name ASC component's `CreatedAbilities` array. A subclass/renamed ability does not match unless its generated class name equals the requested name. Class-path identity is not checked.
- Framework proof target selection is different: the configured soft `TargetPawnClass` is resolved and `InTarget->IsA(TargetClass)` is used. This intentionally accepts subclasses, so a configured base class may admit descendants beyond one concrete Blueprint class; sibling classes are refused.

## False positive / negative boundaries

Exact short-name comparisons can false-positive a same-named class from another package, or false-negative a semantically compatible subclass with a distinct name. `IsA` avoids the subclass false negative but broadens the accepted set to descendants. These are consequences of the current matching contracts; this audit does not recommend renaming any pack class or changing behavior.

## Evidence limits

The reviewed source confirms the matching operators and configured class path, not the actual loaded Blueprint class hierarchy, generated class names, package collisions, or project asset identity. Those require reflection/runtime readback. Static only; no assets or tests run.
