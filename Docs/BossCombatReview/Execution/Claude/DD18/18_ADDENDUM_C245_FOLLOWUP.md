# DD18 addendum: effect of the DD17 C245 follow-up on the DD18 evidence (Claude, 2026-10-28)

The six DD18 files are UNCHANGED (hashes as in `18_DELIVERY.md`: header 8a71cdf9..., cpp ce6a1b31..., registry header d9d813c7..., registry cpp 253a47f4..., tests fb867b15... and 38729988...). The only change in the tree since the DD18 delivery is the DD17 follow-up (`Player/RPGBossWorldInputCompiler.cpp` 9451d166... -> 1a99ba05..., see `Claude/DD17/17_REVISION_C245_FOLLOWUP.md`), which Codex asked for first (C245_RETAINED_MEMBER_IDENTITY_FOLLOWUP).

Consequences for the DD18 receipts, stated precisely:
- `pre_source_manifest_sha256.txt` (185 files) stays the true baseline saved after the C-245 revision and before any DD18 file. `post_write_source_manifest_sha256.txt` (191) is the manifest at the DD18 delivery (C-246): exactly six added lines.
- `post_c245_followup_full_tree_manifest_sha256.txt` (191) is the manifest now; `manifest_c245_followup_diff.txt` against the delivered 191-file manifest is exactly one removed and one added line: the DD17 cpp. So against the 185-file baseline the tree now differs by six added files and that one DD17 file.
- `dependency_pins_after_c245_followup_sha256.txt` replaces the DD17 cpp pin (RPGBossWorldInputCompiler.cpp) with the new hash; the other twelve dependency pins are identical. The facade and registry call only the public `CompileWorldInput` API, whose signature and header did not change.
Nothing else in DD18 is affected. Not compiled, not run.
