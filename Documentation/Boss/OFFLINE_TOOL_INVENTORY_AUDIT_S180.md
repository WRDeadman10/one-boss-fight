# Offline tool inventory audit (S180)

Compared top-level `Scripts/Tools/*.py` files with `Documentation/Boss/TOOLS.md` command snippets. The inventory classified test modules and the shared atomic-I/O helper separately from user-facing CLIs.

## Result

- 51 Python files are present in `Scripts/Tools`.
- 43 are maintained command-line utilities.
- Seven `test_*.py` files are test modules, and `atomic_io.py` is an imported helper; neither category is a standalone CLI.
- The initial index had 35 CLI entries. Added examples for the eight missing utilities: `audit_framework_schemas.py`, `check_doc_links.py`, `check_evidence_sha256.py`, `check_mailbox_ids.py`, `check_validator_tokens.py`, `compare_parry_runs.py`, `new_profile_field_scaffold.py`, and `new_rule_scaffold.py`.
- Re-ran `py Scripts/Tools/audit_tool_index.py --root .`: `indexed_tools=43 issues=0` (exit 0). All indexed script paths exist and all indexed flags appear in each command's `--help` output.

## Disposition

Every maintained CLI is now indexed. The profile-field example is stdout-only; the rule-scaffold example explicitly directs users to an empty temporary root because it creates files. Seven fixture modules and `atomic_io.py` are explicitly excluded from the CLI inventory by role. The auditor does not validate positional argument counts or shell quoting. No test suite/build/Editor/runtime was run; the only executions were CLI `--help` checks through the index auditor.
