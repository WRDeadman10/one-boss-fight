# Offline tool Unicode path fixtures (D70)

Date: 2026-11-03. Reviewed and ran `test_path_normalization_s170.py` and `test_atomic_io_s171.py` from `Scripts/Tools`: 3 tests passed on Windows.

The S170 temp-only fixture covers a root, directory names, and evidence filename containing spaces and Unicode; creates the source spelling with forward slashes plus a backslash separator on Windows; checks in-root destination resolution; writes/reads UTF-8 manifest JSON through `verify_evidence_manifest`; and rejects a Windows backslash traversal. S171 additionally exercises atomic replacement/create with Unicode filenames and checks exact temp cleanup.

This Windows run exercises the Windows-specific branch, unlike a POSIX run where the fixture uses native separators. The fixture calls `evidence_pack.safe_output_path` and the manifest verifier directly rather than executing the entire `evidence_pack.py` CLI; end-to-end Unicode source copying and console rendering are not covered. Tests use only temporary directories and clean them automatically.
