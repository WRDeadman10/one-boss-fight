# BI-X31–X35 — Offline Tool Portability and Parser Boundaries

**Status:** Read-only source and fixture audit. No tool code or tests were changed; no tests were run.

## BI-X31 — Queue validator scope

`Scripts/Tools/validate_queue_batches.py` validates only hardcoded `QUEUE_AA.md`, `QUEUE_AB.md`, and `QUEUE_AT.md` families and their AA/AB/AT task-ID dialects. It checks ordered IDs 01–50, duplicate/missing/extra IDs, malformed task cells, and family-specific batch/marker rules. It does not discover arbitrary queue documents or validate newer BF/BI table formats. UTF-8 decoding and file I/O are handled in its CLI loop, but unsupported row families are outside the parser's scope. Existing fixtures cover supported families, duplicate/missing/regrouped rows, and empty/short rows; tests were inspected, not run.

## BI-X32 — Evidence manifest portability and integrity boundaries

`Scripts/Tools/verify_evidence_manifest.py` reads schema-1 JSON as UTF-8, checks payload path containment after `Path.resolve()`, compares hashes (case-insensitively for listed payloads), and optionally checks sizes, JSON source references, and strict directory membership. Source-reference hashes require lowercase hex. The implementation and inspected fixtures establish traversal/absolute-path refusal and source-reference membership/hash checks; the external symlink test is skipped when Windows refuses symlink creation.

Portability and exception gaps to preserve in any future contract:

- `Path(name)` uses host path semantics. Drive/UNC paths, backslashes, case folding, and slash aliases do not have identical interpretation on Windows and POSIX.
- Duplicate detection uses the original manifest string, so alternate strings resolving to the same path may bypass the textual duplicate check.
- Listed-path `resolve()` is not guarded for resolution errors (for example, a symlink loop or access failure); strict-membership traversal does catch `OSError` around resolution. A malformed filesystem tree may escape the verifier's normal issue-list error path.
- The symlink-to-outside fixture is source-reviewed but not executed on this Windows host; in-root symlink and symlink-directory traversal behavior are not established by the inspected tests.
- Strict membership exempts the manifest and `evidence_sha256.txt`; behavior for aliases and inaccessible nested directories needs dedicated fixtures before broad portability claims.
- UTF-8 BOM handling is not explicit for the manifest (`encoding="utf-8"`), unlike the separate evidence SHA list checker that uses `utf-8-sig`.

These are audit findings, not claims that a current evidence bundle was corrupted. No fix was made because changing verifier error handling needs focused fixtures and cross-platform verification.

## BI-X33 — Proposed platform-sensitive fixture matrix

| Case | Windows expectation | POSIX expectation | Current coverage/status |
|---|---|---|---|
| Valid nested relative path with spaces and Unicode | Accept, hash bytes | Accept, hash bytes | Not found in inspected verifier tests |
| `../` traversal and rooted absolute path | Refuse | Refuse | Covered |
| Windows drive-root and UNC path strings | Refuse as outside/absolute | Explicitly classify portable input instead of relying on host `Path` | Not covered cross-host |
| Backslash traversal spelling | Refuse when interpreted as Windows path | Treat as literal or reject by portable schema | Not covered cross-host |
| `./x`, `dir/../x`, separator/case aliases to same target | Define canonical duplicate policy | Define canonical duplicate policy | Textual `seen` set only; not covered |
| External symlink file and symlink directory | Refuse; skip/report inability to create fixture | Refuse | File test exists but may skip; directory not found |
| In-root symlink and dangling link | Define allowed/rejected policy | Same explicit policy | Not covered |
| Symlink loop, inaccessible path, or resolution exception | Return issue instead of traceback | Return issue instead of traceback | Listed candidate resolution is unguarded; not covered |
| UTF-8 BOM, malformed UTF-8, malformed JSON | Explicitly accept BOM or return one diagnostic | Same | Invalid UTF-8 and JSON handling covered; BOM not covered |
| Hash case, malformed digest, size mismatch | Define strict schema and byte comparison | Same | Payload comparison is case-insensitive; malformed syntax not separate |
| Strict membership: extra file, nested directory, link | Reject per policy without following outside link | Same | Some cases source-reviewed; incomplete coverage |

## BI-X34 — Documentation link checker semantics

`Scripts/Tools/check_doc_links.py` scans Markdown under `Documentation`, parses a limited Markdown link form, URL-decodes target text, checks relative path existence, and skips every parsed URL scheme and protocol-relative URL. Fragment-only links are accepted. Inspected tests confirm encoded spaces, missing relative paths, fragment-only links, and external-scheme skipping. It does **not** validate anchors, link semantics, paths outside the scanned docs, or `file:` URLs; all schemes are skipped. Text uses `errors="replace"`, so invalid UTF-8 is not separately reported. Its supported Markdown syntax is determined by one regex, not a full CommonMark parser.

## BI-X35 — Batch result and boundedness

No active corruption was found that can safely be fixed without adding/running focused tests. Keep the resolution-exception path and cross-platform path normalization as bounded follow-up candidates. Current tooling remains within its documented scope; this audit does not upgrade coverage or portability acceptance. Continue BI-X36–X40.
