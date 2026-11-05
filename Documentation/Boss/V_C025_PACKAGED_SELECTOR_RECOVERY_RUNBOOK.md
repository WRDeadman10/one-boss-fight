# V-C025 — Packaged selector recovery runbook

This is a lead-run procedure for a later real caller and A7-B gate. It does not convert PIE results into packaged proof. Do not modify a packaged manifest or reuse an already-running process between cases.

## Before each case

1. Record source revision/build ID, Shipping or Development target, executable SHA-256, staged/package manifest path and SHA-256, GPU/driver, console or RDP session, route, selector input, timestamp, command and exit code.
2. Preserve the complete run folder, raw log, structured encounter snapshot, and screenshot where required. Hash raw evidence and link each receipt to its package identity.
3. Start a fresh process for each selector case. Retain failed attempts. Never change the packaged asset or stable manifest hash to create a negative test.
4. Use only a separately authored, Lead-reviewed invalid fixture included in the package manifest; if no safe fixture exists, leave that case blocked rather than corrupting production content.

## Cases and expected recovery

| Case | Setup | Required outcome |
|---|---|---|
| Valid J049-A selection | Real approved Blueprint caller supplies the G044 object before world startup | Selected route, exact G044 identity/hash, selected components active, no legacy boss bundle; visible normal arena |
| Missing requested object | Use the approved missing-path selector only in a Development package, or a controlled caller refusal | `HardError` with `EncounterSelection.AssetLoad`, no legacy bundle, explicit visible refusal/recovery |
| Invalid definition/manifest | Use the packaged reviewed invalid fixture with recorded identity | `HardError` with `EncounterDefinition.ManifestShape` (or exact current refusal token), cleanup, no legacy bundle, visible refusal |
| Empty/no selection before A7-B | Fresh process, no setter call, `bUseLegacyStartup=True` | `LegacyNoSelection` and legacy components restored; captures rollback/control behavior |
| Empty/no selection after A7-B | Only after retirement is approved and its package exists | Clear no-selection refusal/no legacy attach, with the approved recovery route explained |

For each row, record route and outcome from raw log plus structured snapshot, component inventory, visible UI screenshot, and package identity. A refusal without visible owner-session confirmation is incomplete. The same result must be repeated in a fresh process before closing the package gate.

Source matrix: `Documentation/Boss/T025_G2_PACKAGED_RECOVERY_MATRIX.md`; source preparation: `Scripts/Editor/pie_selection_refusal.py` and `Documentation/Boss/G2_STARTUP_ACTIVATION_SOURCE_MAP.md`. Lead owns package/build/run; owner approves the caller and reviews visible recovery.
