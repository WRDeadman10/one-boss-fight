# Evidence manifest path-safety test audit (Queue D D54)

## Implemented boundary

`Scripts/Tools/verify_evidence_manifest.py:11-44` accepts schema 1 with a `files` list, then requires string `file` and `sha256` fields. Each path is interpreted relative to the manifest directory, resolved, and rejected if absolute, lexically contains `..`, or resolves outside the evidence root. It rejects a repeated identical path string, reports missing/non-file targets, and compares optional byte count plus SHA-256. The CLI is read-only and returns 1 when any issue is found.

`Scripts/Tools/test_queue_c_s36_s40.py:16-30` covers a valid in-root file, changed bytes/hash, missing file, and `../outside.log` traversal. The Unicode/path-normalization fixture at `test_path_normalization_s170.py:34-52` checks a normal in-root file and traversal rejection through the path-creation helper; neither inspected test creates a symlink. `test_queue_c_tools.py` covers a mutated manifest target/hash but no duplicate paths or symlink escape.

## Limits beyond current tests

| Case | Implementation behavior | Test coverage / limit |
|---|---|---|
| `..` or absolute path | Explicitly refused. | Traversal fixture and absolute-path predicate are source-visible; direct absolute-path fixture absent in inspected targeted tests. |
| Symlink resolving outside root | `resolve()` follows it; resolved candidate fails `is_relative_to(root)`. | No symlink escape test; this behavior is inferred from pathlib semantics and source. |
| Symlink resolving inside root | Accepted if it resolves to an in-root file with matching bytes/hash. | No symlink-in-root fixture. |
| Duplicate identical path string | Second entry rejected. | No duplicate-entry fixture found. |
| Two different in-root paths/aliases to same target | Not considered duplicate because dedupe key is the original `name` string. | No alias/case/separator-equivalence fixture. |
| Missing target or directory | `is_file()` false, reported missing. | Missing-file case covered; directory target not separately covered. |
| Hash/size mismatch | Both are independently reported; byte count is optional. | Mutation/hash fixture exists; exact size-only mismatch coverage not found in inspected cases. |
| Symlink loop or resolution error | `Path.resolve()` may raise before an issue is returned. | No exception-path fixture or local catch around resolve. |
| Hard link whose in-root name shares an inode with an outside path | Accepted as an in-root path; path containment does not prove inode exclusivity. | Outside-object identity is outside this path-based contract. |

Conclusion: path containment is enforced for resolved paths and the documented no-out-of-root claim should stay scoped to resolved-path containment. Alias deduplication, symlink tests, resolution exceptions, and hard-link identity are not established. Source and fixture inspection only; no tests were run.
