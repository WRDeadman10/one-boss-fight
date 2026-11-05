# H002 / H004 — selection contract and world lifecycle map

**Scope:** source review only. No build, Editor, PIE, or runtime sequencing claim.

## Current startup API map

| Contract | Source | What it establishes | Limit |
|---|---|---|---|
| Selection lifetime | `Source/OneBossFight/Player/RPGEncounterSelectionSubsystem.h:13-38`; `.cpp:25-70` | GameInstance subsystem stores one typed definition or a non-shipping CVar path; it does not store pawn pointers. | Current CVar value is process-global, not scoped to the GameInstance; `ClearSelectedDefinition` clears it. No persistent/default selection is approved. |
| Definition record | `RPGBossEncounterDefinition.h:15-35`; `.cpp` validation | Schema, encounter GUID, explicit manifest hash, role slots, initial phase and typed soft definition refs are validated. | Hash remains caller-authored membership data; not derived provenance or catalog epoch identity. |
| Startup boundary | `RPGPlayerMovesSubsystem.cpp:35-53,57-113` | Spawn handler is installed at `PostInitialize`; `OnWorldBeginPlay` selects the data route only if a request exists. Without a request the legacy Attach loop remains. Selected route builds a binding, activates, and has no legacy boss fallback on refusal. | No proof yet that every production level startup takes this ordering; Lead's prior BUILD-209 covers the no-selection regression snapshot, not latest tests. |
| Exact census | `RPGEncounterSelectionSubsystem.cpp:72-119` | Game thread, game world, pre-BeginPlay, same GameInstance, exactly one recognized pack boss and player, both unbegun; selected phase exists. | This is deliberately not callable after world BeginPlay. |
| Compiler | `RPGBossWorldInputCompiler.h:17-21`; corresponding `.cpp` preconditions and epoch acquisition | Explicit expected world, binding, role selections and manifest hash; acquires world catalog epoch and validates before publishing complete input. | Rejects begun world; successful compile is input/preflight only, not registration or readiness. Manifest provenance is caller-supplied. |
| Activation and release | `RPGPlayerMovesSubsystem.cpp:80-113,155-179`; `RPGBossActivation` result/lease APIs | Startup activation owns a lease; later selected participant spawn currently releases and fails closed. | Begun component cleanup may refuse destruction; KI-182 records they remain in place but inactive. |

## World-start / late-spawn sequencing

The supported current route is a single pre-BeginPlay census and activation at `URPGPlayerMovesSubsystem::OnWorldBeginPlay`. The late spawn callback is a post-BeginPlay observation, not a safe second startup window: the census builder and world compiler reject the begun world. The exact callback ordering on the pack's respawn is unproven. `URPGBossEncounter::TickComponent` notices a changed player pawn, then `ResetEncounter` increments the reset counter and generation (`RPGBossEncounter.cpp:115-141,303-323`); there is no current delegate notification (`RPGBossEncounter.h:48-62`). See H001 for the proposed post-reset seam and tests. Until that seam is approved and measured, selected mode keeps the C-803 fail-closed behavior.

## Minimal selection lifecycle receipt (proposal; does not alter parity v1)

For any future startup/rebind integration receipt, preserve the existing `onebossfight.encounter-parity/v1` comparator contract unchanged and attach this separate nested object:

```json
{
  "schema": "onebossfight.encounter-selection-lifecycle/v1",
  "selection": {
    "encounter_id": "<canonical lowercase GUID>",
    "definition_path": "<long package object path>",
    "manifest_hash": "<exact authored hash>",
    "boss_slot": "<explicit FName>",
    "player_slot": "<explicit FName>",
    "initial_phase": "<explicit FName>"
  },
  "world": {"map": "<long package name>", "catalog_epoch": "<epoch identity>"},
  "participants": {
    "generation": 1,
    "boss_actor": "<stable per-run actor identity>",
    "player_actor": "<stable per-run actor identity>"
  },
  "activation": {"outcome": "Ready|HardError", "refusal": "<empty on Ready, stable token otherwise>"}
}
```

Rules: exact schema only; nonempty and unique IDs; generation is positive and strictly increases on each accepted respawn rebind within the run; actor identities must be fresh per run and distinct; selection identity and record hash/slots/phase must remain unchanged across a rebind; world/catalog epoch must be explicit; refusal tokens come from the stable `EncounterSelection.*` / `EncounterActivation.*` vocabulary and are never replaced by a legacy fallback. Missing fields or mismatches mean INCONCLUSIVE/refused, not inferred success. Do not serialize pawn addresses or treat this receipt as proof that assets are cooked. The receipt remains a proposal; post-BeginPlay epoch acquisition has not been implemented or proven. C-804 approves a separate narrow rebind compiler entry only if needed, while preserving `CompileWorldInput`.

## H005 — released code vs product decisions

Released under C-800/C-803/C-804: opt-in selected startup only, strict pre-BeginPlay census, no-selection legacy behavior, selected-path fail-closed/no fallback, interim same-world respawn refusal, and Step A reset delegate/logging without rebind. G019–G023 paired PIE and G044 live PIE remain Claude-owned. H001 rebind Step B awaits Claude's live ordering measurement. Owner-only: production default selection, binary/main-map edits, A7 legacy retirement, and product scope. No H item here authorizes any of those changes.
