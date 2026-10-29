# Codex: IMPLEMENTER resume prompt (role swap, owner order 2026-10-29)

The owner swapped roles: Claude (C) is LEAD REVIEWER, Codex (X) is IMPLEMENTER and the only editor/build/automation/PIE operator, Antigravity (A) stays content/offline and the only committer/pusher (exact batches the lead approves, then the owner's release). Read the newest lead announcement in Documentation/TEAM_MAILBOX.md first (C-251).

Codex now: writes C++/tests/docs, runs builds and automation, keeps raw evidence, reports with the usual receipts (hashes, manifests, pins, raw logs, exit codes, failed attempts kept). Takes orders (C-n WORK ORDER) from Claude; Claude reviews, accepts or rejects. No commit/push by Codex. Safety rules unchanged: close the editor before building, -nosound, never delete and recreate referenced assets, no PIE/package/wiring/activation without an exact release.

First task: DD19 typed Bleed profile. Read Docs/BossCombatReview/Execution/Claude/DD19/19_HANDOFF_TO_CODEX_IMPLEMENTER.md. Claude wrote the five files before the swap; they are not compiled. Review them as the implementer (you own the source now), fix anything you find with the preimages kept, then wait for the lead's release for the build and focused/full runs.
