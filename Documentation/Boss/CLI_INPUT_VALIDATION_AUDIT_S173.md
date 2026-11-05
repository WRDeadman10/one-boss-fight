# CLI input validation audit (S173)

Static review of maintained `Scripts/Tools` command-line inputs, malformed-file handling, and write ordering. No CLI, fixture, test, build, or Unreal Editor was run in this audit.

## Findings

| File:lines | Finding |
|---|---|
| `Scripts/Tools/token_coverage.py:35-39,56-71` | A missing explicit log prints `MISSING` and continues; the final status only considers unknown tokens. With no unknown tokens, the CLI can return 0, and `--samples-output` can still write a manifest. A missing required input therefore is not reliably a nonzero error and can produce output. |
| `Scripts/Tools/evidence_pack.py:40-61` | The output directory is created before destination collision/reserved-name validation completes. A bad source/output-name combination can therefore leave a newly created directory even though argparse rejects the invocation. Source-file existence is checked before this mutation. |
| `Scripts/Tools/make_source_manifest.py:17-24` | A mistyped `--root` with no `Source` directory yields an empty manifest and exit 0 instead of identifying the invalid root; the output parent and manifest are then written. |
| `Scripts/Tools/profile_dump.py:24-31`; `card_table.py:11-25`; `validate_baked_cards.py:11-35`; `plugin_dependencies.py:14-23` | JSON decoding and shape errors are not caught with a path-specific diagnostic. Decode tracebacks are nonzero but the JSON API receives text rather than a filename, so the bad input path is not included in the parser's own error message. `validate_baked_cards.py` also assumes an object with `cards` and nested mapping/list shapes. These are read-only tools, so malformed input does not mutate project files. |
| `Scripts/Tools/audit_pie_command.py:70-86`; `verify_evidence_manifest.py:12-54` | Better examples: `audit_pie_command` checks both files, catches parse/read errors, and returns 2; `verify_evidence_manifest` returns path-qualified issues and its CLI returns 1. |
| `Scripts/Tools/evidence_summary.py:69-83`; `new_rule_scaffold.py:73-111` | These validate required evidence directory / scaffold arguments before producing content. `evidence_summary` prepares CSV in memory before atomic publication; the scaffold rejects invalid identifiers and known existing targets before creating files. Static ordering review only. |

Argparse enforces declared required positionals/options, but `type=Path` alone does not establish that a file or directory exists. The S154 CLI author guide says uncaught parse/I/O exceptions can be nonzero, but this audit found that a nonzero traceback does not always name the bad file, and that a few tools continue after missing inputs.

## Disposition

Acceptance is **not met**. Lead recorded the missing-log, late-directory, and empty-manifest cases as KI-163–KI-165, and path-qualified JSON diagnostics as KI-166. This audit applies no runtime changes. No tests/build/Editor/runtime were run.
