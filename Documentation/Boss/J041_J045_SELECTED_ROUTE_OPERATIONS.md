# Queue J J041–J045 — selected-route operations

**Scope:** authoring workflow, read-only validation, failure recovery, evidence retention and claim readiness. This is operational documentation/tooling; it does not authorize a production default, a Shipping selector, or new gameplay behavior.

## Current evidence boundary

Claude reports BUILD-212 v12 at 459/459 automation tests (C-819). That accepts the native rebind path at automation level. It does not prove that typed definitions exist, that selected startup/rebind works in PIE, that the root graph cooks, or that Shipping selects this route. Claude owns Editor, build, automation, PIE and cook execution. At this update, the authoritative CDO snapshot, typed definitions, canonical manifest receipt and selection asset are still prerequisites.

## J041 — G044 authoring and readback order

Run each Editor command in the already-open UE 5.5.4 Editor through the plugin bridge. Do not run `RunEditorScript.ps1` for this chain: `Scripts/run_in_editor.py` sends the script to the open Editor and leaves it running.

```powershell
python -I Scripts/run_in_editor.py Scripts/Editor/export_encounter_definition_sources.py
```

Retain the timestamped `Saved/G044/source_snapshots/encounter_sources_*.json` and its logged SHA-256. From that current snapshot and reviewed source citations, author the required `Saved/G044/typed_definition_specs.py`; every definition property must be explicit and every non-provenance leaf must have a path/line citation. Do not promote stale/historical values. Then run:

```powershell
python -I Scripts/run_in_editor.py Scripts/Editor/create_g044_typed_definitions.py
python -I Scripts/run_in_editor.py Scripts/Editor/write_g044_manifest_receipt.py
python -I Scripts/Tools/validate_encounter_manifest.py Saved/G044/encounter_manifest.json
python -I Scripts/run_in_editor.py Scripts/Editor/create_g044_encounter_definition.py
python -I Scripts/run_in_editor.py Scripts/Editor/validate_g044_encounter_selection.py
```

The creator paths are package paths. Editor `get_path_name()` readbacks are object paths (`<package>.<object>`); compare the package portion with `object_path.split(".", 1)[0]`. UE Python removes the `E` prefix from reflected enum class names. These scripts must not load a map. Each content creator refuses an existing target, resolves dependencies and checks fields/readbacks before saving; the selection validator is read-only and must never save.

Only after all commands pass, record a fresh empty-selector legacy control, then the selected startup in `L_SevarogArena`, followed by the selected H019 respawn/rebind driver. The opt-in console command is:

```text
rpg.EncounterDefinition /Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter
```

Stop on any refusal or missing readback; preserve the existing assets and logs. Do not turn a selected-route failure into a legacy pass.

## J042 — read-only designer selection validator

Run `Scripts/Editor/validate_g044_encounter_selection.py` in the open Editor using the command above. It checks exact selection field paths, typed definition classes/identity, phase membership, skeleton/animation resolution, manifest schema/canonical digest and package/object path agreement. It uses `EditorAssetLibrary.load_asset` for assets only; it never loads a map, mutates an object, or saves a package. Failures print `field=...` diagnostics and return a failed Editor task; success prints the selected object path, definition object paths, phase and manifest digest.

The validator is an authoring preflight, not proof that the production compiler accepts every nested definition field or that the route activates in PIE.

## J043 — failed selected-activation recovery

1. Stop PIE and preserve the raw log, selected asset path, command/settings and any parity/cook receipts. Record the exact `[EncounterActivation] outcome=HardError reason=...` token; do not guess from a generic editor failure.
2. Selected activation is fail-closed. The subsystem disables the framework boss and does not add the legacy boss bundle. Independently attached player setup is retained. Rebind failures clear the pending timer/delegate; clean release removes the transient binding, while unsafe release intentionally retains the lease/binding for diagnosis.
3. Do not manually delete actors/components or delete and recreate referenced assets. Correct a source field or reference deliberately, validate again, and refresh the canonical manifest only when the typed definitions change.
4. To return to legacy startup, stop PIE and explicitly clear selection with `rpg.EncounterDefinition ""`, then start a fresh run. Typing `rpg.EncounterDefinition` with no value only prints the current value and does not clear it. Do not treat this as recovery of the failed selected run; retain that failure as a separate result.
5. Re-run the read-only selection validator, the successful selected startup, then the relevant selected refusal/recovery control. Keep each run and result separate.

## J044 — retain raw evidence and hashes

Allocate a fresh run directory before each control, selected, refusal or rebind run; fail if it already exists:

```powershell
$runId = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ') + '_' + [guid]::NewGuid().ToString('N')
$runDir = Join-Path 'Saved/G044/runs' $runId
if (Test-Path -LiteralPath $runDir) { throw "Refusing existing evidence directory: $runDir" }
New-Item -ItemType Directory -Path $runDir | Out-Null
```

Retain the unedited raw Editor/PIE log, command and settings record, source-snapshot hash, manifest receipt, selected asset object path, binary/build identity, map/content identity, terminal result and any generated runtime receipt. Hash every retained evidence file after capture:

```powershell
Get-ChildItem -LiteralPath $runDir -File -Recurse | Get-FileHash -Algorithm SHA256
```

Never edit a captured input in place. A corrected or rerun capture gets a new run directory and run ID. A paired comparison requires matching declared inputs/build/content/settings and distinct run IDs; missing or unmatched source evidence is inconclusive, not a pass. The manifest validator and parity comparator do not fabricate runtime facts.

## J045 — readiness matrix

| Claim | Current evidence | Status and owner boundary |
|---|---|---|
| Native selected activation/rebind behavior | BUILD-212 v12, 459/459 (Claude, C-819) | **Automation accepted.** This is source/build evidence only. |
| Typed boss/player data and selection record | No current Editor CDO snapshot/specs/assets reported | **Blocked.** Requires Editor readback and safe creation before selected PIE. |
| Canonical manifest | No saved G044 receipt reported | **Blocked.** Generate from current typed readback and validate its hash. |
| Selected startup and respawn/rebind in PIE | No selected-route PIE receipt | **Not witnessed.** Claude owns PIE and must retain raw logs. |
| Cook/package reachability and packaged activation | No root graph/cook receipt for the selected asset | **Not witnessed.** Requires Editor graph export and cook/package evidence. |
| Shipping selector/default | No approved Shipping selector or owner default decision | **Owner gate.** No readiness claim or default change is implied. |
| Paired parity and performance | No paired data-route receipts or matched selected-route samples | **Not measured.** No parity/cost conclusion is implied by automation. |

Each readiness claim must cite its own build/run/evidence identity. Do not promote a successful native suite or Editor asset readback into PIE, cook, packaged, parity, performance or Shipping evidence.
