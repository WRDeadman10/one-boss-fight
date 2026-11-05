# S24–S25: legacy baseline generation and tuning guard

The G044 source-cited defaults table now powers two offline operations in `Scripts/Tools/compare_manifest_to_legacy_defaults.py`.

## S24 — generate a full baseline

Use an existing G044 manifest only as the shape and identity template. The generator copies it, sets every boss typed leaf from the exact or indexed source-cited defaults-table rule, verifies that every boss leaf was covered, and validates the output with the same audit. It refuses a missing citation, stale source line, uncovered boss field, non-comparable boss field, or existing output path. Player leaves and identity fields are retained from the template; this is not a new production manifest or a live route change.

```powershell
$out = Join-Path $env:TEMP ('G044_legacy_baseline_' + [guid]::NewGuid().ToString('N') + '.json')
python Scripts/Tools/compare_manifest_to_legacy_defaults.py `
  --manifest Saved/G044/encounter_manifest.json `
  --emit-legacy-baseline --output $out
```

Validation on the checked-in G044 shape produced 424 typed rows: 214 MATCH, 0 MISMATCH, 210 player NOT-COMPARABLE. All boss rows matched the cited defaults. The generated file was written only to a unique temporary path.

## S25 — fail closed on unlisted tuning

Ordinary comparison exits nonzero when any MISMATCH exists. An optional JSON array of approval records can explicitly mark intentional tuning. Schema: `Scripts/Tools/intentional_tuning.schema.json`.

```json
[
  {
    "field": "definitions.boss.stats.max_health",
    "value": 1999.0,
    "reason": "Example only: replace with the approved gameplay rationale.",
    "owner_approval_id": "OWNER-DECISION-ID"
  }
]
```

```powershell
python Scripts/Tools/compare_manifest_to_legacy_defaults.py `
  --manifest path\to\draft.json `
  --intentional-tuning path\to\intentional_fields.json
```

Each record must name a unique current MISMATCH, match the draft's exact value, include a nonempty reason, and cite a nonempty owner approval ID. The CLI checks record completeness and exact field/value binding; a reviewer must confirm that the ID resolves to a real owner decision. Stale/unknown fields and mismatched values are refused. Mismatch rows remain labeled MISMATCH; the exit gate passes only when every mismatch has an explicit record.

Tests cover full default emission, indexed fields, zero boss mismatches, unlisted/listed tuning classification, record fields/value binding, and duplicate/unknown paths. No Unreal asset, build, package, or route was changed.
