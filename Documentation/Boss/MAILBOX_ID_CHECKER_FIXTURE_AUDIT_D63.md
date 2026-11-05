# Mailbox ID checker fixture audit (D63)

Date: 2026-11-03. Read-only audit of `Scripts/Tools/check_mailbox_ids.py`, `Scripts/MailboxPost.ps1`, `Scripts/MailboxNext.ps1`, and the current mailbox.

## Behavior

- The checker recognizes only header prefixes matching `### [C|X|A-<digits>]`; valid IDs are grouped by party.
- Duplicate detection is numeric, so e.g. `X-01` and `X-1` collide.
- Gap detection sorts distinct numeric IDs and reports missing interior values. It does not flag a missing prefix before the smallest ID or a missing tail after the largest ID.
- Input order is not checked: IDs may move backward in the file with no finding as long as the set is gap-free and unique.
- Malformed or unsupported headers are silently ignored, including a recognized valid prefix followed by malformed trailing header text. An otherwise empty/unrecognized file returns no issues and exit 0.
- It checks C/X/A only. This matches the mailbox post script's sender validation, which permits only those three parties.
- The checker is read-only and returns 1 for duplicate/gap findings; missing mailbox file is argparse error 2.

`MailboxPost.ps1` serializes appends under the named mutex and chooses `max(existing IDs for sender)+1`; this means the checker’s full-history gap rule intentionally detects historical missing IDs, not merely corruption at the tail. The actual append contract is per-sender monotonically increasing and append-only. The audit records order/malformed-validation gaps without changing this tool.

## Current mailbox run

`python Scripts/Tools/check_mailbox_ids.py` reported `message_headers=2049 issues=3`: X skipped IDs 21–50; A skipped ID 215 and IDs 236–237. It did not report any duplicate IDs. These are historical sequence gaps; this run does not determine whether the missing messages were intentionally removed or lost.

## Acceptance boundary

The checker detects numeric duplicates and interior sequence gaps but does not enforce chronological monotonic order, complete header syntax, party-specific prefix/suffix completeness, or mailbox write integrity. Those behaviors are absent from the inspected fixtures; no test suite or mailbox mutation was performed.
