# BK-231..235: evidence-pack integrity and destination hotfix

Assigned in X-2079 after the BK-226..230 audit found P1-P3. Lead applied the bounded hotfix in the shared tree; Claude and Antigravity were asked to preserve/review it. All checks below use synthetic files in OS temp directories only. No project evidence packs, Unreal, build, or PIE were touched.

## Findings and fixes

| Finding | Change | Regression |
|---|---|---|
| P1: a corrupted copy could be hashed and reported as successful without comparison to the source (`evidence_pack.py` copy/readback block). | Capture source size and SHA-256 before copy; compare both against the published copy before adding a manifest row. A mismatch exits nonzero and never publishes the commit-marker manifest. | `test_gap_p1_copy_is_not_compared_with_its_source` injects a corrupt copy and verifies nonzero exit with no manifest. |
| P2: an existing non-empty destination could accept a pack that later fails strict-membership verification (`mkdir(exist_ok=True)`). | Accept only a new or empty output root; reject a non-empty directory before copying and preserve its existing members. | `test_gap_p2_output_root_must_be_new_or_empty`. |
| P3: planned and reserved destination checks were case-sensitive on Windows, allowing name aliases to fail mid-publish. | Normalize reserved and planned names with `os.path.normcase` before any copy. | `test_gap_p3_case_variant_collisions_are_caught_before_copying` checks both colliding planned names and `EVIDENCE_MANIFEST.JSON`. |

## Verification

- Evidence-pack audit and hotfix regressions: 13 tests passed; one symlink test skipped because this host cannot create symlinks. The former P1-P3 expected failures now pass.
- `test_evidence_pack_hashes.py`: 2/2.
- Existing evidence-manifest verifier suite: 5 tests, one symlink skip.
- Verifier family: 71 tests, one skip.
- Queue C tools: 24 tests, one symlink skip; Queue C S36-S40: 7/7.
- Python compilation of the producer and audit test passed.

Partial output may remain after a copy mismatch, but it has no manifest commit marker and is rejected by the verifier. No existing output file is overwritten.
