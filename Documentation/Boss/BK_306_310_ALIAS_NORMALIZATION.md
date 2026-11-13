# BK-306..310: alias-guard path normalization (five report writers)

Assigned by X-2143 (lead Codex) to C (implementer), 2026-11-12. This is lane BK-271..320, batch 8 of 10. New files only:
- `Scripts/Tools/test_bk306_310_alias_normalization.py`
- this report

**No source change.** This batch also reviewed the lead's `make_source_manifest` Source-subtree hotfix (X-2141): it is correct, and case and `..` spellings are covered below.

All runs are real CLI subprocesses with `cwd` set to the fixture root, on temp-only fixtures. No project output, lock, pack, asset, Unreal, build or PIE.

## BK-306: normalization map (source)

| Writer | How the output path is formed | Guard comparison |
|---|---|---|
| `summarize_encounter_cost.py` | `--report-json` as given; a relative path is relative to `cwd` | `output_aliases`: `resolve()` equality, or `samefile` when both exist |
| `summarize_packaged_metrics.py` | as given (`cwd`) | `report_path.resolve()` against a set of resolved evidence paths (receipt + cited `source_log`s, relative to the receipt's folder), plus `samefile` |
| `evidence_summary.py` | `--output`; a relative path is joined to `--root` | `output_aliases(output, logs + validator)` |
| `token_coverage.py` | `--samples-output`; a relative path is joined to `--root` | `output_aliases(output, logs + validator)` |
| `make_source_manifest.py` | positional output, relative to `cwd` | `output_aliases(output, scanned Source files)`, then `output.resolve().is_relative_to(Source.resolve())` (the lead's hotfix) |

On Windows, `Path.resolve()` canonicalizes the existing prefix: case, `.` and `..` segments, and 8.3 short names expand to long ones. `samefile` also matches by file identity. A probe confirmed `source/new.txt` → `...\Source\new.txt`, `SOURCE/a.cpp` → `...\Source\a.cpp`, and `samefile(SOURCE/A.CPP, Source/a.cpp)` is true.

## Results

| Task | Cases | Result |
|---|---|---|
| BK-307 | **6 spellings × 5 writers = 30 subtests**: absolute, relative to `cwd`, `./rel`, `first/../rel`, `realpath` (long, not 8.3), and case-swapped (Windows) | **All refused** with exit 2 and the writer's alias message. The input bytes are intact and no temp is left. |
| BK-308 | a symlink to each input | **Skipped**: `OSError(22, 'A required privilege is not held by the client')`. The test asserts refusal and input preservation where symlinks exist. |
| BK-309a | a new `make_source_manifest` output under `Source/`, in relative, `Source/../Source/sub/…`, absolute and case-swapped (`sOURCE/…`) spellings | **All refused** with `output must be outside the scanned Source directory`, exit 2. `Source/` still holds only `a.cpp`. |
| BK-309b | ordinary outputs: `./out/…`, `out/../out/…`, `out/…`, and a sibling `SourceManifest.txt` whose name only *starts* with "Source" | **All written** with each writer's normal exit code. The summarize writers exit 2 on a `{}` receipt, which is INCONCLUSIVE by design. The sibling is **not** treated as inside `Source`. |

## Dispositions

- **Coverage complete for the spellings that can be tested here.** There are no gaps and no fix.
- **Lead hotfix review:** correct. `is_relative_to` on resolved paths blocks every tested spelling under `Source/` and does not over-match a `Source*` sibling.

## BK-310: tests

- From the repo root: `python -m unittest discover -s Scripts/Tools -p test_bk306_310_alias_normalization.py -v` → **`Ran 4 tests ... OK (skipped=1)`**.

| Class | Test |
|---|---|
| `Bk307SpellingVariants` | `test_every_spelling_of_an_input_is_refused_for_all_five` (30 subtests) |
| `Bk308SymlinkAlias` | `test_symlink_to_an_input_is_refused_and_input_preserved` (**skipped**: no symlink privilege) |
| `Bk309SourceSubtreeAndValidOutputs` | `test_new_manifest_under_source_is_refused_in_any_spelling` (4), `test_ordinary_outputs_in_relative_and_dotted_spellings_are_written` (6) |

## Platform limits

- Windows 11 / NTFS / Python 3.10 only.
- **Symlink aliases are unverified on this host.**
- Case-insensitivity is a Windows property. On a case-sensitive filesystem the case-swapped spellings are different files, and the subtests are not generated there.
- Junction aliases and UNC or `\\?\` prefixed spellings were not exercised.
