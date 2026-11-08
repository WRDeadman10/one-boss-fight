# AQ-C41–C45: scoped offline final audit

**Scope:** re-run AQ's focused offline contracts and syntax checks; inspect the AQ Python tools for writes, save calls, destructive operations, and Engine/editor boundary; reconcile current status; validate local links. No editor, Unreal, build, PIE, cook, or package was run.

## C41 — focused contracts

Ran:

```text
python -m unittest Scripts.Editor.test_pie_camera_engage_contract Scripts.Editor.test_prepare_aura_choice Scripts.Tools.test_aq_package_gates Scripts.Tools.test_aq_evidence_freshness
```

Result: **24 tests passed**. This covers the maintained probe configuration/telemetry contracts, aura planner dry-run boundary, package-vs-PIE gate distinctions, and evidence freshness classifications. The live B+C observation remains the single bounded C-1090 attack case; no package claim is inferred.

## C42 — Python write and execution boundary

Inspected the AQ-maintained files: `Scripts/Editor/pie_camera_engage.py`, its contract, `prepare_aura_choice.py` and contract, `aq_evidence_freshness.py` and contract, and `test_aq_package_gates.py`.

- No `set_editor_property`, asset-save, delete, recursive-delete, or filesystem unlink API occurs in the AQ tools. The aura planner is data-only and its test explicitly rejects Editor property/save APIs.
- `pie_camera_engage.py` intentionally has runtime-driver side effects: it sets test CVars and requests PIE (`:279–300`), moves the player and changes control rotation (`:212–235`), and may inject look input or start tracker moves (`:216,238`). The new C37 AST contract restricts only the observation/aggregation helpers; it correctly does not mislabel the whole driver read-only.
- No `RPGCameraRig` source change, asset edit, raw evidence rewrite, build, or runtime execution was made in these batches.

Syntax check:

```text
python -m py_compile Scripts/Editor/pie_camera_engage.py Scripts/Editor/test_pie_camera_engage_contract.py Scripts/Editor/prepare_aura_choice.py Scripts/Editor/test_prepare_aura_choice.py Scripts/Tools/aq_evidence_freshness.py Scripts/Tools/test_aq_evidence_freshness.py Scripts/Tools/test_aq_package_gates.py
```

Result: **PASS**.

## C43 — status reconciliation

`Documentation/KNOWN_ISSUES.md` records the C-1090 B+C result as one tested two-route attack-mode case and leaves broader scenarios, owner choice, and package proof open. KI-037/KI-066 remain open. The package gate in `AQ_C21_C25_PACKAGE_GATES.md` likewise requires owner selection and a separate staged-package run. Corrected the stale historical AP summary in `Documentation/TASKS.md` to include C-1090's limited result; no KI was closed or broadened.

## C44 — local links and whitespace

`python Scripts/Tools/check_doc_links.py .` returned `broken_links=0`. `git diff --check` exited 0; Git printed only the repository's LF-to-CRLF notices.

## C45 — scope conclusion

The queue's AQ implementation remains offline authoring, static evidence review, and test contracts. `prepare_aura_choice.py` plans three aura options without an Unreal/asset write path, while camera behavior remains selectable only by the owner; the camera experiment CVars are Development-only and package acceptance stays separate. No additional API or status mismatch was found in this audit. Queue census and exact row acceptance are verified in the following C46–C50 audit batch.
