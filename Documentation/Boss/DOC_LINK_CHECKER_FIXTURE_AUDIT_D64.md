# Documentation link checker fixtures (D64)

Date: 2026-11-03. Added `Scripts/Tools/test_check_doc_links_s64.py` with temporary-root fixtures and ran it from `Scripts/Tools`: 3 tests passed.

## Coverage and behavior

- Percent-encoded spaces are decoded before relative filesystem resolution; the fixture verifies a nested relative link to a filename containing a space.
- A fragment-only link is skipped. For a path plus fragment, the checker verifies only that the file exists; it does not validate the fragment target/anchor.
- Missing relative paths are reported with source path, line, and decoded target.
- `http(s)` and protocol-relative URLs are skipped. `check_doc_links.py` imports `urllib.parse` only and has no network client; the fixture also checks no `urlopen` symbol exists.

The checker scans Markdown under `Documentation/`, ignores fenced code and inline code, and excludes image links. It is a path-existence scan, not a complete CommonMark parser or anchor validator. No project-wide link scan was run.
