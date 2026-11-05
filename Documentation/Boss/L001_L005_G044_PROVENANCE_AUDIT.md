# Queue L Batch 1 — G044 provenance and readback audit

## Status

L001 and L005 require Claude's current Editor snapshot and selection assets. No
`Saved/G044/source_snapshots/` files exist in this checkout, and the typed spec,
definition assets, manifest receipt, and selection are absent. Their values are
not inferred from historical/default data. Codex completed independent static
hardening for the parts of L002–L004 that do not require Editor access.

## Changes

- `create_g044_typed_definitions.py` now requires boss and player specs to cite
  the same SHA-256, checks it against the newest timestamped snapshot, validates
  snapshot schema/source roles, and compares every reflected property readback
  recursively against the authored encoding before any package is saved.
- `write_g044_manifest_receipt.py` now carries the exact source snapshot digest
  from those specs into the canonical receipt.
- `validate_encounter_manifest.py` rejects receipts without a lowercase
  64-character source snapshot digest, verifies that it matches the newest
  timestamped snapshot in the receipt's sibling `source_snapshots/` directory,
  and includes it in canonical payload hashing.
- The existing G044 selection validator cross-checks selected object paths,
  package paths, definition snapshots, phase and manifest digest. It remains an
  Editor read-only check and has not been run because its assets are absent.

## Remaining batch work

1. Claude captures and retains the fresh boss/player CDO snapshot and digest
   (L001).
2. Codex reviews the authored field citations against that snapshot (L002).
3. Claude runs the refusal-safe typed asset creator and retains full readbacks
   (L003).
4. Claude writes the manifest; Codex validates its identity, object/package
   path contract and digest (L004).
5. Claude creates the selection; the Editor validator checks it read-only
   (L005).

Static Python syntax compilation and scoped `git diff --check` passed. No Unreal,
Editor, tests, build, package save, or live receipt was run by Codex.
