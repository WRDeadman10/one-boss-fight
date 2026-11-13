# BM-16..20: KI-165 / KI-166 characterization (lane BM, batch 4 of 10)

C (implementer), 2026-11-12.

New file: `Scripts/Tools/test_ki165_166_characterization.py`. The tools ran as **real subprocesses on throwaway temp inputs**. They only read their input, and the manifest tool writes only the given output inside the temp folder. **No source change:** the fixes stay owner-gated (`OWNER_DECISIONS_PENDING`, row KI-163–KI-168).

## Observed behavior (pinned)

| KI | Tool and input | Exit | Output |
|---|---|---|---|
| KI-166 | `profile_dump.py`, `card_table.py`, `validate_baked_cards.py` with `{not json` | 1 | a traceback ending `json.decoder.JSONDecodeError: …`; **the input file is not named** in the diagnostic; stdout is empty |
| KI-166 | `profile_dump.py` with a top-level array `[1, 2]` | **0** | prints `[0]\t1`, `[1]\t2` as if they were fields: **a wrong-shape success** |
| KI-166 | `card_table.py` with `[1, 2]` | 1 | `AttributeError`, **after printing the table header** (partial stdout) |
| KI-166 | `validate_baked_cards.py` with `[1, 2]` | 1 | `AttributeError` |
| KI-166 | `plugin_dependencies.py` with a malformed `.uproject` | 1 | `JSONDecodeError` traceback |
| KI-165 | `make_source_manifest.py` on a root without `Source/` | **0** | `files=0 manifest=…`, and an **empty** manifest file is written |
| control | `make_source_manifest.py` on a root with `Source/a.cpp` | 0 | `files=1`; the manifest lists `Source/a.cpp` |

**New detail beyond the KI text:**
- `profile_dump.py` silently **succeeds** on a wrong-shaped top-level value.
- `card_table.py` leaves **partial output** before crashing.

Both belong in the KI-166 row.

## Tests

`python -m unittest discover -s Scripts/Tools -p test_ki165_166_characterization.py -v` → **`Ran 5 tests ... OK`**.

| Class | Tests |
|---|---|
| `Ki166MalformedJson` | `test_syntax_error_is_an_unnamed_traceback` (3 tools), `test_wrong_shape_behaviour_per_tool`, `test_plugin_dependencies_malformed_uproject` |
| `Ki165RootWithoutSource` | `test_missing_source_directory_writes_an_empty_successful_manifest`, `test_control_root_with_source_lists_files` |

## Proposal for the owner row (no change made)

- Wrap each `json.loads` in a named diagnostic (`<file>: <reason>`, exit 2) and validate the top-level shape.
- In `make_source_manifest.py`, refuse a root that has no `Source/` (exit 2).

**These tests are written to fail when a fix lands, which would signal that the expectations need updating deliberately.**

## Limits

- Only these malformed shapes were tried: a syntax error and a top-level array. Other shapes, such as `null` or a wrong field type, were not.
- `plugin_dependencies.py` was only tested with a malformed `.uproject`; malformed `.uplugin` files were not tested.
