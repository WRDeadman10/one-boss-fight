# Queue D suite log hotfix

Date: 2026-11-03. Implemented C-752's D59/D60 dispositions as one tooling hotfix.

`Scripts/Tools/suite_log_report.py` now returns exit 1 when duplicate test identities are present, even if every row says Success. `Scripts/Tools/test_queue_c_tools.py` adds a duplicate-identity CLI exit fixture and truncated-log fixtures for both suite summary and diff loading. The truncated fixtures explicitly preserve current semantics: completed rows are summarized/compared without proving the full test run completed.

Verification from `Scripts/Tools`: `python -m unittest test_queue_c_tools test_queue_c_s36_s40` — 29 passed, 1 host-dependent symlink skip. No suite logs were modified, no Unreal/editor/build ran. `diff_suite_logs.py` continues to reject duplicate keys and empty/no-row logs with invalid exit 2.
