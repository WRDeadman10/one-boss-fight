# New boss checklist: data plus montage annotations

This checklist covers a third boss using the existing generic encounter and attack-tracker path. It is a workflow for common moves represented by the current tracker schema; it does not claim that every boss mechanic is data-only.

## 1. Prepare the definition asset

- Create a new `URPGBossDefinition` asset from the approved definition/schema workflow. Give it a unique definition ID and presentation ID.
- Populate required stats, phase data, presentation, and component configuration from source-backed manifest rows. Keep references and required typed fields complete; use native defaults only where the compiler documents additive defaults.
- Keep `bUseMontageNotifyTimings` false until timing annotations exist and pass strict audit. Afterward, opt in on this boss's definition and retain the typed source-manifest field and its provenance. Do not change Ember or Greystone as part of this proof.
- Run definition/preflight validation and the native binding suite. The data route must activate from the definition without per-boss C++ wiring.

## 2. Annotate the boss montages

- Inventory the actual montage assets and their sections, source sequences, notify events, and timing ranges. Use engine readback for asset facts; do not infer a montage's length from separate sequences.
- Prepare a reviewed move-to-montage timing table for each common attack: move ID, commitment, active window, recovery end, turn-rate/branch values, and authored-windup behavior.
- Use `Scripts/Editor/author_ember_move_timing.py` only after adapting its explicit asset list and values for the new boss. The script must be idempotent, refuse unrelated conflicting notifies, preserve existing events, and verify saved/reloaded values. Never point it at pack assets.
- Run the strict montage timing audit against that boss's annotation manifest. Resolve every mismatch, duplicate, invalid range, and required missing row before enabling the definition. Capture the audit log and manifest hash.

## 3. Run the timing parity PIE gate

- Use a boss-specific copy/configuration of `Scripts/Editor/pie_ember_notify_timing_parity.py`; keep its data collection based on native `LogRPGAttack` transitions and a fresh run-specific `-abslog`.
- Compare timing off and on for equivalent representative attacks, including startup/commit, active-window opening, recovery, and valid terminal outcomes. Warm up the first montage play before measured trials. Treat a paired A3a-style chain stop during Active as a terminal event; compare Complete only when both trials have matching end reasons. Missing or unlike terminal reasons are informational, not a fabricated timing match.
- Run under the engine-lock protocol. Save raw logs, the driver version/hash, the strict-audit receipt, definition/source-manifest hash, build identity, map/route, and the summarized comparison. A script contract or build is not a PIE result; the Lead reviews the actual run before declaring parity accepted.
- Require the new boss to pass the same documented timing tolerance and no-mismatch audit criteria used by the accepted parity gate. Keep pack parry/collision-trace tests separate from tracker timing parity.

## 4. Identify what still needs code

The generic data path supports configuration already represented by the definition, adapters, attack tracker, and annotated montage events. A new boss needs an add-on code module when it introduces a unique move decision rule, target-selection mechanic, custom phase behavior, new interaction/contact semantics, a new runtime component or adapter, or timing/data semantics the existing generic tracker cannot express. Document the smallest reusable extension and add native tests before wiring it. Do not encode a unique mechanic as misleading timing data.

## Completion record

The third-boss proof is complete only when the definition is source-backed, the strict audit passes, the Lead accepts a fresh parity PIE receipt, and every remaining code-only mechanic is listed with an owner and scope. Until then, report the exact gate still open; do not treat authoring plans or offline tests as runtime proof.
