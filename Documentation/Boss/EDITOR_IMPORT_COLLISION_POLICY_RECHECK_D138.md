# Queue D138 — editor import collision policy recheck

Date: 2026-11-03  
Method: read-only spot-check of the post-Queue-C usage boundary, S161/S162 audit, and representative destructive/non-destructive importers. No Editor script was run.

## Current policy map

`Scripts/Editor/README.md` directs reruns that create, duplicate, or import assets to `EDITOR_ASSET_OVERWRITE_AUDIT_S162.md` and `EDITOR_ASSET_DELETION_AUDIT_S161.md`. Both files exist and distinguish explicit replacement, load/reuse, refusal/leave-existing, destructive delete/recreate, and unresolved factory collision behavior. The current source still supports the key distinctions in the sampled cases:

- `import_boss01.py` sets both import replacement flags true and separately deletes existing clips before import; the destructive deletion is listed in S161 and must not be rerun without per-asset reference review.
- `import_boss01_clips_r14.py` queries package referencers before reimporting in place; with references it preserves the existing asset. Its old comment describes a one-time 2026-10-24 observation, not a guarantee for current project state.
- `rpg_content_lib.py::recreate` deletes an existing caller-supplied target without checking referencers; S161/S162 mark it destructive and unsafe absent manual reference review.
- `fix_grey_layers_2.py` is the one sampled deletion path that queries referencers before deleting its temporary copy; this still depends on the live query result.

## Finding

The README and reports do not recommend delete-and-recreate for referenced assets. The destructive paths remain present and are explicitly marked unsafe without manual referencer checks; they are catalogued, not authorized for execution. Import `replace_existing=True` is identified as intentional content replacement, not proof that dependent behavior remains valid.

## Limits

This spot-check does not re-audit all 52 scripts/70 sites, inspect live asset references, or establish Unreal factory collision behavior for unguarded creates. No destination was created, overwritten, deleted, or saved.
