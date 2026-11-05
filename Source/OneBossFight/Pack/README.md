# Pack integration helpers

Pack helpers isolate reflection and asset-specific calls needed to work with the third-party Advanced ARPG Combat Blueprints without editing their assets. Keep these adapters narrow: validate object/class/function/property identity before invoking pack behavior.

## Main files

- `RPGBlueprintCall` finds and invokes a Blueprint function by name with checked parameter access (`RPGBlueprintCall.cpp`; API `RPGBlueprintCall.h`).
- `RPGPackReflect` provides validated reflected object/class/property/function lookup used by the adapters (`RPGPackReflect.h:12-72`).
- `RPGPackTrace` reads the pack weapon trace, contact and gameplay-tag fields through validated reflected access (`RPGPackTrace.cpp:34-62,85-119,175-193,344-370`).
- `RPGPackNotifies` provides native animation notify hooks for spawning a configured effect or charging toward a target (`RPGPackNotifies.cpp:14-36`).
- `RPGHideBones` hides configured bones on a character mesh at BeginPlay (`RPGHideBones.cpp:7-20`).

Pack helpers are not the owner of boss encounter state, damage decisions, or player input. Those belong to the encounter, resolver, and input components. Avoid hard-coded guesses where reflection validation can refuse safely; keep failures visible as named error/log tokens. Do not change third-party pack assets from this module.
