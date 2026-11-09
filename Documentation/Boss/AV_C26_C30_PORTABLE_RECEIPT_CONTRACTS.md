# AV-C26–C30 — portable receipt contracts and handoff refresh

## Completed

- Frame labels reject forward/back separators and control characters; capture IDs must still exactly bind to safe run/frame labels.
- PNG path uniqueness is checked after native normalization, including `nested/../frame.png` aliases.
- CLI JSON tests pin the exact top-level receipt fields and types for target summaries.
- Provenance drift fixtures cover build ID, map and route changes within a manifest.
- Queue and current project handoff now include C-1124 through C-1126: AU-C15 passed on BUILD-269 with a visible approved frame and verified restore; AU-C10 had no parry attempts because A4 was absent in the observed fight; C-1126 AU-C19 passed and requests Lead's BoostLite comparison. Codex supplied the active-window parry hotfix and constrained transient candidate selection. Owner choices remain open.

## Verification and scope

`python -m unittest Scripts.Tools.test_aura_warmup_receipt -q`: 16/16 passed. Combined AU/AV regression set: 95/95. Scoped `git diff --check` and py_compile pass. Tests use synthetic receipt rows and temporary paths. No Lead evidence folder was modified or used by these tests. No Unreal, Editor, PIE, build, cook, package, commit or push was run by Codex.
