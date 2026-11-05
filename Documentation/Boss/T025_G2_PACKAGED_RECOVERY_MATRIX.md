# T025 — G2 packaged recovery acceptance matrix

Use one row set per tested package identity. Fill from the preserved package smoke and packaged-runtime artifacts; do not convert offline PIE evidence into packaged evidence. A blank field means evidence has not been supplied.

## Package identity

| Field | Shipping | Development |
|---|---|---|
| Build ID / source revision |  |  |
| Configuration and target |  |  |
| Executable SHA-256 |  |  |
| Package/stage manifest path + SHA-256 |  |  |
| Run command, timestamp, exit code |  |  |
| Complete raw output/log paths + SHA-256 |  |  |
| Reviewer and review date |  |  |

## Recovery cases

| Case | Required setup and observable result | Shipping evidence | Development evidence | Verdict |
|---|---|---|---|---|
| Missing selection path | Set a nonexistent `/Game/...` definition before startup. Show selected-data route, `HardError` refusal with `EncounterSelection.AssetLoad`, and no legacy boss component bundle. Capture the visible refusal UI. |  |  | OPEN |
| Invalid manifest | Use a controlled invalid-hash definition whose package identity is recorded. Show `HardError` refusal with `EncounterDefinition.ManifestShape`, no legacy boss component bundle, and visible refusal UI. |  |  | OPEN |
| Empty selection | Start a fresh process with `rpg.EncounterDefinition ""`. Show legacy startup (`LegacyNoSelection` or package-appropriate attached outcome) and required legacy boss components restored. |  |  | OPEN |

For each case, record the exact selector value, package/build identity, raw log token or structured snapshot, and screenshot path where required. Preserve failed attempts. Do not edit a packaged manifest or reuse a stale process between cases. Any missing identity, absent refusal UI, unexpected fallback on invalid input, or incomplete legacy recovery remains OPEN/FAIL for Lead disposition.

Source preparation: `Scripts/Editor/pie_selection_refusal.py` and `Documentation/Boss/G2_STARTUP_ACTIVATION_SOURCE_MAP.md`. The driver is authored for PIE; this matrix requires separate packaged evidence and visual confirmation.
