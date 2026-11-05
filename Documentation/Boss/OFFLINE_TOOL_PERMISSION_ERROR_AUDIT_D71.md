# Offline tool permission/error fixture audit (D71)

Date: 2026-11-03. Source review traced denied-write and locked-destination behavior through `atomic_io.py` and the five output-producing CLIs. Added two deterministic `PermissionError` injection fixtures to `test_atomic_io_s171.py` and ran `python -m unittest test_atomic_io_s171 test_queue_c_tools` from `Scripts/Tools`: 26 passed, 1 host-dependent symlink skip.

| Failure boundary | Result supported by source/fixture |
|---|---|
| `os.replace` denied while replacing an existing file | Exception propagates; old bytes survive; owned temp is removed. New injected fixture passes. |
| `os.link` denied while publishing a create-only file | Exception propagates; destination is absent; owned temp is removed. New injected fixture passes. |
| Parent directory cannot be created / `mkstemp` fails | Exception occurs before publishing and is not converted to success by atomic helper. No OS ACL denial was exercised. |
| `evidence_pack.py` copy or later manifest publication fails | Underlying error propagates and process does not return success, but earlier output files and the created output directory can remain; no pack-wide rollback. |
| `make_source_manifest.py`, `evidence_summary.py`, `token_coverage.py` output failure | Atomic write errors propagate through `main`; no success status/summary follows. Parent directories can remain. |
| `new_rule_scaffold.py` later-file failure | Each new file is exclusive and atomic, but previously created siblings can remain; no three-file rollback. |

The tests inject filesystem API failures rather than manipulating Windows ACLs or creating real locked files, so they prove helper exception/cleanup behavior, not platform-specific denial semantics. No project outputs were targeted.
