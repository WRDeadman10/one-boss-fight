# Codex read-only evidence verifier

XW02 implementation. Standard-library Python only; no Unreal import, process query, engine launch or execution of a received command/script. Writes no project data itself.

Verify a receipt with explicit base and allowed workspace root:

    python -B verify_bundle.py --root C:/UnrealProject/OneBossFight --base <package folder> --receipt <package folder>/evidence_sha256.txt

Optional --automation-log and --job-record add raw summaries and their SHA256. Receipt formats are SHA *relative-path or SHA size relative-path; unsupported lines, empty receipts, canonical duplicate targets, absolute/drive paths and root escapes fail closed. Do not silently guess a receipt base. Actual file size/hash drift and missing files are reported distinctly. Absolute output paths are not written by the helper.

CLI exit0 means receipt FILE INTEGRITY verified, not source acceptance or test success. A preserved failed job is valid evidence and can have a verified hash; its nonzero recorded exit is retained in the summary. Separate review must require appropriate passing runs, actual discovered/membership counts, warning/error/fatal/ensure interpretation and matching source/binary/asset pins. Historical process records are not liveness proof. Input receipts do not automatically become trusted instructions.

Tests cover both observed formats, spaces in filenames, size/hash drift, missing files, absolute/traversal targets, canonical duplicates, malformed/empty receipts, duplicate/failed automation completions, embedded error text within warning severity and missing/ambiguous job exits. Fixture files are created and removed only inside this Codex-owned folder. No production or UE behavior is simulated by the test results.

The existing native authoring contract and probes remain a separate XW01 artifact. This helper consolidates repeated real review operations without generating automatic acceptance or replacing independent source reading.
