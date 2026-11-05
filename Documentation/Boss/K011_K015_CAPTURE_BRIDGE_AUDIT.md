# Queue K K011–K015 — runtime capture bridge audit

## Driver and runtime interface findings

The existing A4 probe is `Scripts/Editor/pie_a4_low_sweep.py`. Its `tick(dt)` is registered with `unreal.register_slate_post_tick_callback`; `_tick` begins PIE and obtains the active game world with `UnrealEditorSubsystem.get_game_world()`. It writes `[A4]` observations and a `RESULT passed/total` marker to the Editor log, then requests PIE end. It does not currently read a `URPGPlayerMovesSubsystem`, retain a run envelope, or write a receipt.

The only selected-route snapshot API found is `URPGPlayerMovesSubsystem::BuildEncounterParitySnapshot()` in `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.h`. It is exposed as `UFUNCTION(BlueprintCallable)`, but no Python driver call path or verified Python `UWorldSubsystem` accessor is present in this repository. The current Slate callback therefore has no documented, verified bridge to the subsystem. This is a real K011 blocker; do not guess a Python object path or call.

The snapshot fields and omissions are listed in `J001_RUNTIME_CAPTURE_SNAPSHOT.md`. It contains route, selection, participants, activation and component census, but not driver identity/arguments, build/content/settings/input hashes, seed, check totals, terminal state, measured observables or raw-log identity. It cannot be passed directly to the strict v2 receipt builder. The existing receipt schema and required envelope are defined in `Scripts/Tools/encounter_parity_receipt.py`.

## K012 — minimum truthful run envelope

The capture must combine, without inference:

1. Runtime snapshot from the exact PIE world.
2. Driver identity, ordered arguments, input digest, declared seed and run ID.
3. Build/binary identity, content/settings digests and map identity.
4. The driver's actual final marker, passed/minimum counts and clean terminal result.
5. Each measured observable with trial ID, source-log path and SHA-256.

These map to the v2 `identity`, `selection`, `participants`, `final_marker`, `checks`, `terminal`, `activation`, `components` and `observables` fields. Missing runtime or log facts must produce refusal/INCONCLUSIVE, never placeholders.

## K013–K015 disposition

- **K013 BLOCKED:** no verified Python-to-world-subsystem API exists in the checked source. A safe implementation needs a Lead-verified bridge for the current PIE world and atomic, collision-safe output; it must remain opt-in and leave driver defaults unchanged. No production or gameplay code was changed in this audit.
- **K014 ALREADY IMPLEMENTED:** `Scripts/Tools/compare_encounter_parity.py::verify_source_logs` resolves each cited log and checks SHA-256; `--verify-source-logs` enables it. J028 also added report-destination collision refusal. This covers byte provenance for receipt observables, but does not create the missing capture envelope.
- **K015 LEAD-RUN BLOCKED:** no truthful v2 capture can be run until K013's bridge exists and G044 content enables a selected route. Existing synthetic fixtures are not live receipts.

No A4 driver, receipt or runtime behavior was changed. This is a static interface audit only; no tests, build or Unreal execution were performed.
