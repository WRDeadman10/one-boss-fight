# Arena module

This folder contains runtime dressing and lightweight arena presentation components: greybox geometry, instanced dressing, fire sources, fog gate, ember field, and the performance-switch facade. It does not own gameplay arena bounds; boss arena center/radius policy lives in the profile and framework boss.

## Files and ownership

- `RPGGreyboxArena` rebuilds the collision/greybox arena during construction (`RPGGreyboxArena.cpp:98,234`).
- `RPGArenaDressing` creates instanced dressing and applies visibility/shadow settings; its tick reads performance switches (`RPGArenaDressing.cpp:29-90`).
- `RPGFireSource`, `RPGFogGate`, and `RPGEmberField` own their respective cosmetic actor state and construction/rebuild paths (`RPGFireSource.cpp:42-73,93-134`; `RPGFogGate.cpp:35-66,119-149`; `RPGEmberField.cpp:24-61,103`).
- `RPGPerfSwitches` exposes Development-only `rpg.Perf.*` controls; Shipping stubs keep the features on and do not read CVars (`RPGPerfSwitches.cpp:6-27`; declarations `RPGPerfSwitches.h:7-22`).

## Practical notes

Performance switches are measurement controls, not gameplay tuning. The group covers fire lights/shadows/effects, gate mist, dressing visibility/mist/shadows, and embers. In Shipping the feature code remains active. Use `Documentation/Boss/TEST_HOOKS.md` for the list and defaults.

Construction rebuilds should stay idempotent: clear/reuse the component-owned generated instances and preserve authored component references. Avoid deleting/recreating referenced content assets. Several construction helpers are editor-only guarded; do not assume they are packaged runtime operations.
