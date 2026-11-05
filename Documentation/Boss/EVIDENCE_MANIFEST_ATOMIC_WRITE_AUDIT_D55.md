# Evidence manifest atomic-write failure audit (Queue D D55)

## Failure injection and temp ownership

`Scripts/Tools/atomic_io.py:9-35` creates a unique `.<target>.*.tmp` sibling with `tempfile.mkstemp`, writes/flushes/fsyncs the complete bytes, and only then publishes with same-directory `os.replace`. On an exception it attempts to unlink only that exact temporary path and re-raises; it does not remove the existing target. The helper therefore gives per-file replace atomicity on the same filesystem, subject to platform/filesystem guarantees for `os.replace`.

`Scripts/Tools/test_atomic_io_s171.py:12-26` injects failure specifically at `os.replace`, then asserts the old manifest bytes are unchanged and no matching temp remains in the fixture directory. The test uses a temporary directory with spaces/Unicode. `:28-38` separately checks `atomic_create_text` refuses to replace an existing file and cleans its temp after the `os.link` collision. These are authored fixtures; the S171 audit explicitly says they were not run by Codex and requests Lead execution.

`Scripts/Tools/evidence_pack.py:63-68` publishes copied evidence files and the text hash list with no-overwrite atomic-create helpers, then writes `evidence_manifest.json` last as the bundle completion marker. The atomic guarantee is per file, not a transaction across the whole output directory: if a later file/link fails, earlier newly created pack members may remain. The output path is validated by `safe_output_path`; temp creation is in each validated destination's parent. No rollback removes already-published pack members.

## Bounded conclusions

| Claim | Supported? | Boundary |
|---|---|---|
| Failed replacement preserves old manifest | Yes, source order and injected replace-failure assertion support it. | The specific test is not executed in this audit. |
| Failed publication removes its own temp | Yes, exception handler targets the exact `mkstemp` path; fixture checks the target-specific temp glob. | Other unrelated temp files are not deleted. |
| Temp cleanup is scoped to a tool-owned path | Yes, exact temporary sibling created by this call. | No recursive directory cleanup. |
| Whole evidence pack is all-or-nothing | No. | Earlier atomic-created pack files can remain if a later item or manifest publication fails; manifest-last means no completion marker. |
| Partial-write/fsync fault injection coverage | Not established. | Fixture injects `os.replace` failure and create collision, not mid-stream write/fsync or `os.link` system failure independent of collision. |

Static source/test inspection only; the failure-injection tests, evidence pack, build, and Unreal were not run.
