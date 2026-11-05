# Path normalization audit (S170)

Static review of filesystem-path handling in maintained Python offline tools, with a new safe temp-directory fixture for spaces, mixed Windows separators, and Unicode. No fixture or test was executed.

## Existing path behavior

| File:lines | Behavior and limits |
|---|---|
| `Scripts/Tools/evidence_pack.py:12-18,38-40` | `safe_output_path` resolves candidate output and refuses destinations whose resolved parent is not the output root; `main` resolves the output root before use. Existing symlink/overwrite guards are present. |
| `Scripts/Tools/verify_evidence_manifest.py:19,26-29` | Resolves the manifest parent and each entry, rejects absolute names, `..` components, and resolved escape. `Path` separator and absolute-path semantics are host-platform-dependent; verify on Windows for Windows-form manifest names. |
| `Scripts/Tools/check_doc_links.py:34-45` | URL-decodes relative Markdown paths, resolves them against the document or repo root, and checks existence. It does not write paths. |
| `Scripts/Tools/audit_tool_index.py:32,55-58` | Resolves the repo root and joins indexed relative script paths. The index is repository-controlled; the audit checks existence and child `--help` status. |
| `Scripts/Tools/evidence_summary.py:44-46` | Emits repo-relative POSIX paths when an input is under the root and an absolute string otherwise; it handles `relative_to` failure explicitly. |

The existing `test_queue_c_tools.py:196-230` uses `TemporaryDirectory` and checks output containment/traversal behavior, but its paths do not explicitly include spaces, mixed separators, or Unicode.

## Safe fixture added

`Scripts/Tools/test_path_normalization_s170.py:15-55` creates all files under a uniquely named temporary root, including spaces and Unicode in the root, source folder, output folder, and filenames. On Windows it constructs a source spelling with forward slashes in the root and a backslash before the Unicode filename; on other hosts it uses native `Path` joining. It checks the evidence destination remains a direct output child, verifies a Unicode filename through a manifest hash, and confirms traversal rejection without creating an outside file. The fixture has not been run.

## Disposition

S170 has a safe, isolated fixture and identifies the host-dependent Windows `Path` semantics that require a Windows run for validation. No production path code was changed. Test/build/Editor/runtime were not run; Lead should execute the new fixture on the project’s Windows Python environment before accepting runtime behavior.
