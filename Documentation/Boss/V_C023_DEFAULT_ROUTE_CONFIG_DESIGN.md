# V-C023 — Future default-route configuration design

**Design only; current config is unchanged.** `Config/DefaultGame.ini` currently sets `bUseLegacyStartup=True`. The owner selected A7 Option B (retire legacy later) and J049 Option A (the Blueprint setter is allowed in Shipping); neither decision makes a real Shipping caller exist today.

## Current behavior

- No selection request + `bUseLegacyStartup=True` enters the legacy startup path.
- Explicit valid definition uses the selected route regardless of the legacy switch.
- Explicit missing/invalid selection fails closed; it must not silently attach the legacy boss bundle.
- `rpg.EncounterDefinition` and `-RPGBenchmark` selectors are Development-only; Shipping selection must come from the approved stored-object Blueprint setter.

## Future design after gates

1. Add a real caller that supplies `/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter` before the world startup-selection boundary; validate setter call timing and game-instance lifetime in the actual content graph.
2. Keep `bUseLegacyStartup=True` while the caller is being introduced and packaged proof is collected. This preserves rollback and the parity control.
3. Only in a separate approved A7-B change, set `bUseLegacyStartup=False` (or replace the key with an explicit migration policy) after the caller is present and all release gates close.
4. Missing caller/empty selection after retirement must report a clear no-selection error and attach no legacy boss bundle. Invalid requested content remains hard-error/refusal.
5. Keep the explicit setter route and its package cook closure. Do not enable the Development CVar/benchmark selector in Shipping.

Risks to resolve before implementation: GameInstance initialization order versus world startup, level overrides, new game/continue flow, future multiple encounters, packaged cook references, and recovery after setter failure. Required evidence is in V-C021, V-C022, V-C024 and V-C025. No config or asset change is made here.
