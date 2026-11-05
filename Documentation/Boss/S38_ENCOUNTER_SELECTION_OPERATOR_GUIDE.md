# S38 — Encounter selection, clear, and refusal guide

## Select a definition in a Development test session

The approved G044 object path is:

```text
/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter
```

For an authorized Development/PIE test, set the non-Shipping console variable explicitly:

```text
rpg.EncounterDefinition /Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter
```

The runtime selection is process/world test state. Record the exact map, build/content identity, selection path, output directory, and raw log. Require the runtime snapshot to say `route=data`, selected activation to complete, and the expected participants/slots to match the setup.

## Clear selection explicitly

Clear with an explicit empty-string value:

```text
rpg.EncounterDefinition ""
```

Omitting the value only prints the current variable; it does not clear the previous selection. For a clean control, use a fresh process and confirm the snapshot reports `route=legacy` and `LegacyNoSelection` with the expected legacy component bundle. The G2 driver uses the explicit empty-string form in a fresh PIE session.

## Fail-closed outcomes

| Scenario | Expected activation result | Expected reason token | Required check |
|---|---|---|---|
| Missing definition object path | `HardError` | `EncounterSelection.AssetLoad` | No silent legacy bundle fallback |
| Invalid manifest hash on an unsaved transient copy | `HardError` | `EncounterDefinition.ManifestShape` | Source asset remains unchanged; no legacy bundle leak |
| Explicit empty selection in fresh session | `LegacyNoSelection` | none | Legacy route and full legacy bundle restored |

Claude's BUILD-222 G2 PIE record reports 13/13 checks passed. That run requested visual screenshots, but its screenshots were black in the agent session; owner visual confirmation and packaged recovery proof remain open. These reasons are outcome tokens, not instructions to bypass activation validation. Stop and retain evidence on any other token, missing snapshot, timeout, or unexpected fallback.

The console variable is non-Shipping. Owner decision J049=A separately permits the Blueprint `SetSelectedDefinition` route in Shipping, but C-876 found no current content caller; packaged proof is deferred until the first real caller. The `-RPGBenchmark` selector is a separate benchmark-only route and is not Shipping selection.

Sources: `Scripts/Editor/pie_selection_refusal.py`, `Docs/BossCombatReview/Execution/Claude/C872_G2_REFUSAL_v2/editor_raw.log`, `Documentation/Boss/G044_ENCOUNTER_SELECTION_PIE_EXPECTED.md`, and C-872/C-873/C-876.
