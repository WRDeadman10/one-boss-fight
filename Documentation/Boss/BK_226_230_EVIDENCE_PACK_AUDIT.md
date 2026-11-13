# BK-226..230: audit of evidence_pack.py and its compatibility with verify_evidence_manifest

Assigned by X-2072 (lead Codex) to C (implementer), 2026-11-12. This is batch 12 of 20. New files only:
- `Scripts/Tools/test_bk226_230_evidence_pack_audit.py`
- this report

`Scripts/Tools/evidence_pack.py` is **not modified**; it is byte-identical to the copy saved before the audit. It was exercised only through `main()` on throwaway OS temp fixtures. No project evidence pack was read, created or overwritten, and there was no Unreal, build or PIE.

## Five-area matrix

| Task | Area | Holds | Gap |
|---|---|---|---|
| BK-226 | Inputs and label/duplicate selection | Missing sources exit 2 and write nothing (`:38-39`). An exact-name destination collision, for example raw `pre_x.log` against pre `x.log` → `pre_x.log`, is refused before any copy (`:53-54`). The reserved names `evidence_manifest.json` and `evidence_sha256.txt` are refused. | **P3 (Windows):** the collision and reserved-name checks compare exact strings, so case variants (`Pre_x.log` vs `pre_x.log`, or `EVIDENCE_MANIFEST.JSON`) pass planning and fail **during publishing**, with an `os.link` FileExistsError and a traceback, after earlier copies were already published. |
| BK-227 | Output-root confinement, symlinks, overwrite | Every destination is a direct child of the resolved output root (`:16-18`). An existing destination or manifest is never overwritten (`:19-20`), and the original bytes are kept. Publishing uses `os.link` from a temp sibling, which is exclusive (`atomic_io.py:47,67`). A symlinked destination is refused (`:19`); that test is skipped on this host because symlinks are unavailable. | **P2:** `out.mkdir(exist_ok=True)` (`:41`) publishes into an existing, non-empty folder. Unrelated files then sit next to the pack and fail `verify(strict_membership=True)` later. |
| BK-228 | Copy, readback, hash, bytes, cleanup | `bytes` and `sha256` are read back from the **published copy** (`:64-65`) and match it; `evidence_sha256.txt` lines match the manifest. The temp sibling is removed on failure (`atomic_io.py:48-53,68-73`). The manifest is written last as the **commit marker** (`:67-68`): a failure before it leaves no manifest, so `verify()` refuses the partial pack. | **P1:** nothing compares a copy with its **source**. A copy that differs from the source (a faulty copy, or a concurrent writer) is recorded as-is and the run exits 0. |
| BK-229 | Schema, order, verifier compatibility | Top level `{"schema": 1, "files": [...]}`. Every entry has exactly `label`, `file`, `bytes`, `sha256`. The order is stable: raw, pre, post. The output passes `verify(require_bytes=True, strict_membership=True)`, including the optional text `label` allowed by the X-2070/X-2074 patch. | — |
| BK-230 | CLI exit behavior | Success → 0. Argument and validation errors → 2 (argparse). | An exception during publishing propagates as exit 1 with a traceback. That is a fail-closed design property, recorded here and not counted as a gap. |

## Confirmed gaps (pinned as `expectedFailure`; each confirmed to fail on its own assertion)

| Id | Where | Fix rule |
|---|---|---|
| **P1** | `:63-65` | Hash the source before copying, and refuse (non-zero exit, no manifest) when the source and copy hashes differ. |
| **P2** | `:40-41` | Require the output root to be new or empty, refusing before any copy, or at least list pre-existing members. |
| **P3** | `:44-55` (Windows only) | Compare `os.path.normcase` names, including the reserved set, during planning, and exit 2 before any copy. |

## Design properties (documented, not gaps)

- **Partial output on publish failure:** copies already published before a failure stay on disk, with no manifest, so `verify()` refuses the folder. Cleaning those copies up automatically would be a design change; it is left to the lead.
- **Exit code for unexpected I/O errors:** these propagate as exit 1 with a traceback, which is still a failure.

## Tests and results

From `Scripts/Tools`: `python -I -m unittest discover -s . -p "test_bk226_230_evidence_pack_audit.py" -v` → **`Ran 13 tests ... OK (skipped=1, expected failures=3)`**. The skip is the symlink test, because this host cannot create symlinks.

| Class | Tests |
|---|---|
| `Bk226InputsAndSelection` (3) | Missing sources; exact-name collision before any copy; reserved name. |
| `Bk227OutputConfinement` (3) | No overwrite of a destination or the manifest; symlinked destination (skipped here). |
| `Bk228IntegrityAndCleanup` (3) | Hashes, bytes and `evidence_sha256.txt` parity; the manifest as commit marker, with a synthetic publish failure leaving no manifest; **P1**. |
| `Bk229SchemaAndCompatibility` (1) | Schema, exact entry keys, stable order, labels; `verify()` round trip in strict mode with byte counts required. |
| `Bk227Gaps` (2) | **P2**; **P3**, which runs on Windows only and is confirmed on this host. |
| `Bk230Cli` (1) | Exit 0 on success, 2 on an argparse error. |

Also checked:
- `py_compile` OK; no trailing whitespace.
- The existing `test_evidence_pack_hashes.py` passes, but it covers the separate `evidence_pack_hashes` module, not `evidence_pack.py`.

## Limits

- The faults in P1 and the commit-marker test are injected by patching (`atomic_create_copy`, `atomic_create_text`); no real disk fault was produced.
- P3 is Windows-specific; the test is skipped on case-sensitive filesystems.

## BK-231..235: P1-P3 fixed (lead patch X-2082, completed by C, 2026-11-12)

**SOURCE CHANGED** by the lead: `Scripts/Tools/evidence_pack.py`, kept as is.

| Gap | Fix (`evidence_pack.py`) |
|---|---|
| P1 | `file_identity(source)` reads the source size and hash before the copy (`:84`); the published copy is re-read (`:86`). A mismatch exits 2 (`:87-88`) **before** the hash file or manifest is written (`:90`, `:92`). |
| P2 | An existing output root must be a directory and empty (`:53-60`). Otherwise the run exits 2 before any copy or output-file write. |
| P3 | Reserved names use `os.path.normcase` (`:64`); each planned target uses it before duplicate/reserved comparison (`:73-76`), so case variants exit 2 at preflight. |

**My review of the patch:**
- A P1 mismatch leaves the mismatched copy on disk but **never a manifest**, so `verify()` refuses the folder; that is safe.
- The empty check counts every entry, including hidden files.
- A valid pack's CLI behavior is unchanged: exit 0, the same schema and the same order.
- The existence check runs before `mkdir`; a race between them is theoretically possible, and the per-file exclusive publishing still prevents overwrites.

**New:** `Scripts/Tools/test_bk231_235_evidence_pack_failure_paths.py`, **9/9**:
- **`ValidPacksUnchanged` (1):** new and empty existing output roots still produce a pack that passes strict `verify()`.
- **`FailureInjection` (4):** each publishing step is failed in turn: the copy (second file), a corrupted copy, a same-size corruption, and publishing the hash file or the manifest. Every case leaves **no manifest**, and `verify()` refuses the folder (no false PASS).
- **`OutputRootAndPreflight` (3):** a non-empty root is refused before any write; a root that is a file is refused; the Windows case variants (`EVIDENCE_MANIFEST.JSON`, `Evidence_Sha256.TXT`, `Pre_x.log` against `x.log`) are refused before any write.
- **`ProducerVerifierParity` (1):** every produced entry fits the verifier's key, type and hash contract.

**Before and after:** run against the copy of `evidence_pack.py` saved before BK-226, the 7 fix cases fail (both P1 corruption tests, the two P2 root checks, and the three P3 case variants). The publish-failure and valid-pack cases pass on both versions, because they cover existing design behavior.

**Reruns** (`python -m unittest`):

| Suite | Result |
|---|---|
| BK-231 failure paths | 9/9 |
| BK-226 audit (P1-P3 now ordinary regressions) | 13 (1 symlink skip) |
| BK-221 compatibility | 6/6 |
| BK-216 audit | 14/14 |
| `evidence_pack_hashes` | 2/2 |
| verifier | 5 (1 skip) |
| path normalization | 1/1 |
| Queue C S36-S40 | 7/7 |
| Queue C tools | 24 (1 skip) |
| BI-A19 | 1/1 |
