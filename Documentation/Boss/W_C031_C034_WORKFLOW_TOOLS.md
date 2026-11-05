# Queue W-C031–W-C034 — review, resume, evidence, and mailbox tools

## W-C031 — one Lead gate command

Added `Scripts/FullReviewGate.ps1`. It defaults to dry-run, prints Gate.ps1's ordered build/native/offline checks, then the five BUILD-232 Tier 2/A2-off pair IDs (phase reset, boss death, authored close clips, Legend, iframes) using the retained `B_C835_PARITY/run_parity.ps1`, followed by a fail-closed comparator summary. `-Execute` is required to run the build and Editor pairs; `-BuildId` is mandatory so receipts cannot silently use an old identity.

## W-C032 — resumable 31-pair nightly

Extended `Scripts/RunA5ParityNightly.ps1` with `-Resume` and an atomic `resume.json` checkpoint after each completed pair. A resume checks the registered driver list, skips checkpointed PASS rows, and stores a retry in a new `_attemptNN` folder if a prior interrupted/failed attempt already made that driver's folder. Existing evidence is preserved. Dry-run reports completed and pending counts; `-Resume` requires an existing valid checkpoint. Pair runs remain fresh Editor processes owned by the Lead.

## W-C033 — evidence hash packer

Added `Scripts/Tools/evidence_pack_hashes.py` to write a relative-path SHA-256 manifest inside each requested build/parity evidence folder. It refuses pre-existing manifests, duplicate roots, symlinks, and out-of-root paths, and never hashes its own output. Tests verify hashes across separate roots and no-overwrite behavior.

## W-C034 — last-200 mailbox open-state digest

Added `Scripts/Tools/mailbox_open_items.py`. It reads the last 200 message blocks and emits compact excerpts only for explicit status-word mentions (`OPEN`, `WAITING`, `PENDING`, `BLOCKED`, `PARTIAL`, `REVIEW REQUESTED`, `DECISION NEEDED`). It is a mention index, not task deduplication or a verdict that an item remains open. The current file scan covers 200 message blocks and finds 81 explicit mentions.

## Review correction from C-933

Claude's BUILD-234 review correctly changed the case-only optional montage assertion: Unreal `FString ==` is case-insensitive, matching the helper's own comparison. The test now expects a lowercase-only path to match, and `W_C016_C019_TEST_AUDIT.md` states that rule. BUILD-234 is GREEN 478/478 in Claude's C-933; that build included the correction and previous batch source. No game/build launched by Codex for this batch.
