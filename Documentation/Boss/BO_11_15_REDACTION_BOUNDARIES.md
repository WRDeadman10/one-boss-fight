# BO-11..15: adversarial redaction-boundary batch (lane BO, batch 3 of 10, per X-2241/X-2243)

C (implementer), 2026-11-12. Synthetic temp fixtures only.

**Not done:** no Unreal, build, PIE or asset work, no KNOWN_ISSUES status change, no commit or push.

## Changes

| Task | File | Change |
|---|---|---|
| BO-11 | `Scripts/Tools/redaction.py` | `install_stream_redaction(False)` after `True` now flushes and **restores the original stdout/stderr**. Repeated enables never double-wrap. A disable with nothing wrapped is a no-op. Before this, the wrapper could not be turned off within a process |
| BO-12 | `redaction.py` | `_RedactingStream` is **line-buffered**: text is held until a newline, so a path split across `write()` calls is redacted as a whole. The held tail is written, redacted, on `flush()`, on disable, at interpreter exit, and by an atexit backstop. Before this, each chunk was redacted separately and a split path leaked |
| BO-13 | `redaction.py` | POSIX machine roots are now an explicit, case-sensitive `POSIX_MACHINE_ROOTS`: `home tmp var mnt opt root private media srv etc usr run data workspace workspaces proc dev Users Volumes Applications Library` (added: usr, run, data, workspace(s), proc, dev, Volumes, Applications, Library). Unreal mounts (`/Game`, `/Engine`, `/Script`, `/Temp`, `/Memory`, `/Config`, plugin mounts) are preserved |
| BO-14 | tests only | path-form matrix: raw, forward-slash, JSON-escaped, upper-case root, other-drive (all three forms), UNC, JSON-embedded, `Path={…}`, and in-project paths. False-positive controls stay verbatim: `::` enums, `3/5`, `cm/s`, `a:b`, URLs, `12:30:01`, dotted test paths, `/Game/...`, `e=1/g=2` |
| BO-15 | `redaction.py`, `Scripts/Tools/evidence_summary.py` | (1) **A real leak found and fixed:** the evidence_summary parser cuts `profile=` at the first space, so a fragment such as `C:\Users\<first name>` matched no root, and the fallback printed the first name as `<external>/<first name>`. Now any fallback path that is a prefix of the project, temp or home root is labelled as that root. (2) Under `--redact`, the CSV `run` column keeps run identity as `<evidence>/run1/editor_raw.log`, where before every outside-root run collapsed to `<external>/editor_raw.log`. (3) The parsed `map` and `profile` values pass through `redact_text`. The token samples manifest already redacted `path` and `sample` (BO-05) and is now covered |

**New test file:** `Scripts/Tools/test_bo_redaction_boundaries.py`, 12 tests.

**Generated-artifact checks (BO-15):**
- Under `--redact`, the manifest and the CSV contain no absolute form of the temp root.
- The token list and order, the source/line values, and the map, date, outcome, validator, schema, semantic and sha256 columns match the default run.
- **Default files** are identical across two no-flag runs and still contain the absolute path (control).

## Tests run

**Red check:** in a temp copy, I reverted each piece: write-through stream, no unwrap, old root list, no prefix rule, old `run` value. The suite then fails **5 tests**, at least one each for BO-11, BO-12, BO-13 and BO-15. BO-14 is a characterization matrix, green before and after. One test was strengthened during the red check: the BO-13 test first iterated the module's own list, which passed vacuously, so it now uses an explicit expected list.

| Command | Result |
|---|---|
| `python -m unittest test_bo_redaction_boundaries` (from `Scripts/Tools`) | Ran 12, OK |
| `test_bo_redaction_matrix`, `test_bo_tool_hardening` and the 22 other related suites | all OK |
| `python -m unittest Scripts.Tools.test_summarize_framework_log` (from the repo root) | OK |
| `python -m py_compile Scripts/Tools/*.py` | OK |

**Total: 26 suites, 178 tests, 0 failures.**

## Limits and the spaces decision (asked for in X-2241)

- **Paths with spaces:**
  - Under the project, temp or home roots: masked whole (exact root match), and a space-cut prefix of those roots is labelled as the root (BO-15).
  - Elsewhere (for example `D:\My Files\x.log`): only the part before the first space is masked, so `x.log`'s parent fragment `Files\x.log` can remain.
  - **Decision: not safely addressable in free text.** Extending a match across spaces would swallow ordinary words after a path. Documented as a remaining limit; outside the user profile the exposed text does not include the profile name.
- **Over-masking:** a bare `C:\Users` (a prefix of home) is printed as `<home>/`. This is safe, but loses information.
- **POSIX:** an unlisted first segment (for example `/data2/...`) is not masked; this is pinned by a test.
- **Buffering:** a tool that writes a partial line and then crashes hard (killed, not exiting normally) can lose the held tail. A normal exit, an exception exit or `flush()` writes it.
- Redaction remains a sharing aid, not a security boundary.
