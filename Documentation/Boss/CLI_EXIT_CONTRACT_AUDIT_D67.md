# Offline CLI exit contract audit (D67)

Date: 2026-11-03. Cross-checked every maintained CLI in `Scripts/Tools/CLI_AUTHOR_GUIDE_S154.md` against source return paths and each command's `--help` syntax. All 43 `--help` calls returned 0. Corrected three S154 table mismatches:

| Tool | Source behavior | Documentation correction |
|---|---|---|
| `check_mailbox_ids.py` | Exit 1 for numeric duplicate headers or interior ID gaps; malformed header forms are not recognized and therefore ignored. | Replaced inaccurate “duplicate/malformed sequence IDs” finding description with numeric duplicates/gaps and malformed-header caveat. |
| `framework_results.py` | Exit 1 only when any diagnostic begins `ERROR `; warning/info-only repeated-result diagnostics return 0. | Clarified `ERROR` as the failure condition; WARN/INFO alone return 0. |
| `suite_log_report.py` | Following C-752, exit 1 for parsed failed rows or duplicate Path-or-Name identities; otherwise 0. | Added duplicate identities to findings and exit-1 condition. |

Invalid CLI syntax and argparse `parser.error` paths exit 2. Tool-specific invalid inputs vary: some are parser errors, some use explicit result codes, and some surface nonzero I/O/parse exceptions. The S154 table now states per-tool deliberate exit outcomes and key invalid-input paths; source-wide exceptional I/O behavior remains variable as its introduction explains. `diff_suite_logs.py` uses 2 for unreadable/no-completion/duplicate-key inputs, 1 for differences, and 0 for identical maps. `proof_report.py` retains its documented precedence: incomplete 2, checklist/identity failure 1, stale evidence 3, pass 0.

This is static/source and help-text validation. No normal CLI actions, Unreal commands, or project test suite were run for D67.
