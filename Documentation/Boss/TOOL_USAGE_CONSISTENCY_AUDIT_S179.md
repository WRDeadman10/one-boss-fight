# Tool usage consistency audit (S179)

Compared documented `Scripts/Tools` command snippets with parser declarations and `--help` support. The existing index auditor was invoked once; it runs each indexed CLI with `--help` only and does not process project evidence or write files.

## Result

`py Scripts/Tools/audit_tool_index.py --root .` returned `indexed_tools=35 issues=0` (exit 0). This confirms all 35 commands indexed in `Documentation/Boss/TOOLS.md` resolve and accept every documented `--flag` in their help text.

Manual positional-argument spot checks against argparse declarations also match the examples in `Documentation/Boss/TOOLS.md`: required log/manifest pairs, `evidence_pack.py` raw-log/output plus optional pre/post state, required `evidence_summary.py --output`, `make_source_manifest.py` output positional, and the single-root positional for `check_doc_links.py`. The Queue B handover examples for `check_validator_tokens.py --root .`, `check_test_plan_ids.py --root .`, and `check_doc_links.py .` match their parsers.

The index auditor compares flag strings but does not validate positional arity, option-value pairing, shell quoting, or whether example placeholder files exist. S154's CLI guide remains the fuller input/output contract index.

## Disposition

No stale command syntax was found in the checked maintained-tool snippets. The --help-only auditor completed successfully; no tests, builds, or Editor/runtime commands were run.
