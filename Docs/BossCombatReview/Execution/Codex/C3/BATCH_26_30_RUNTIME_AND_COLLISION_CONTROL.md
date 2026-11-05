# Queue F-C C3 tasks 26–30: production surface and collision controls

The existing Editor utility's valid authoring path is: validate config against the live attack rows and asset existence; preflight registration paths and root; plan; require `--apply`; then write/read back the attack rows and create/read back the definition assets and catalog references. It has no native `URPGCombatCatalogSubsystem` compile API. The C++ catalog is compiled by `URPGCombatCatalogSubsystem::Initialize` at game-instance startup (`RPGCombatCatalog.cpp`); `new_weapon.py` emits `CATALOG_COMPILE_PENDING` after its Editor writes. Runtime acceptance therefore requires the Lead's fresh startup/PIE log.

The preflight now loads existing root entries and refuses duplicate weapon IDs, style names/aliases, build IDs, console names, and build aliases. Any unresolved current definition fails closed. Destination existence, distinctness, and root existence are also checked before attack-table mutation. `fixtures/catalog_collision_cases.json` records the refusal/control matrix.

`capture_prerequisite_hashes.py` is a read-only control tool. The checked-in example manifest fingerprints six existing pack prerequisite/icon packages; intended mutation targets (`DA_WeaponAttacks` and `DA_CombatCatalog`) are deliberately excluded. Lead should capture separate before/after manifests on a unique fixture and verify prerequisite hashes unchanged, then verify only the declared table/catalog/new definition packages changed.

Codex checks: Python AST parse and targeted diff check only. The hash helper captured the example's current prerequisite baseline. No tests, Unreal Editor, PIE, or build were run; the authoring path and native startup compile remain unverified at runtime.
