# AG08 — owner-requested mailbox UI improvements

Codex lead,2026-10-27. Direct authority: owner mailbox O2 requests displayed time, latest-first message index and improved mobile detail reading. This is a narrow exception to the older AG07 prohibition on live Scripts edits: AG may claim/edit **Scripts/MailboxViewer.py only for mailbox parser/composer/presentation behavior**, plus AG-owned reports/offline UI tests. Codex remains reviewer and does not acquire general live-file authority. No Source/Config/game assets/pack/engine/build/PIE, combat behavior or new thresholds. Reviewed-batch commit permission remains; no unreviewed UI batch released.

## Priority and sequencing

Take O2 UI first. Preserve current AG07 partial work; resume X181 final source-contract consistency corrections afterward. No acknowledgment wait and no Claude request. Claim MailboxViewer.py in mailbox before editing, inspect actual current bytes/concurrent changes and preserve them. Lead observed SHA5f88c0921096de8be6da96a230ce2625a940a47fe6d08c1f83827a2b846badeb at00:25IST; recheck actual file before editing, not a license to restore old bytes.

## Required behavior

1. Show date AND recorded time with clear timezone where timestamp exists, in list and detail. Old date-only entries must say time not recorded or show date alone with an explicit unknown indicator; never derive per-message time from mailbox mtime or fabricate midnight/order. New composer posts include actual date/time/timezone. Agents will start timestamping new headers too. Preserve raw historical messages.
2. Latest appended message first in index; do not sort by inaccurate historical timestamp or numeric ID. Preserve selected message by stable identity across polling/search/filter updates. Ensure the display identifies newest rather than silently reselection/scroll-jumping away from a message being read. Storage remains append-only and existing IDs/body content remain intact.
3. Mobile: give the selected message a practical reading area (single-pane/detail view or equivalent), readable text/wrapping, simple back navigation, restrained fixed headers/actions and no trapped tiny nested scroll panel. Preserve desktop list/detail usefulness, filtering, live updates and composer. Long unbroken hashes/paths and lengthy owner/agent messages should remain readable without horizontal overflow; full text still accessible, not silently truncated.

## Verification and delivery

Use fake mailboxes/parser fixtures covering date-only headers, timestamp+timezone headers, out-of-order dates/IDs, append order, duplicate display strings and stable selection. Verify composer append preservation and escaping; don't send fake messages to real team mailbox. Smoke-check existing actual message count/body fidelity read-only. Exercise narrow mobile and desktop layouts with honest screenshots if tools permit; if visual testing unavailable report it explicitly, no invented screenshot/interaction claims. Label any AST/static check versus browser evidence separately.

If a UI-server restart is necessary to show the change, first identify ONLY actual MailboxViewer.py process/service and its port/command; preserve URL/mobile access and report the operation. No broad process matching/killing, no engine/job interference. Launch any helper hidden. No need to wait for Claude; this server is unrelated to Unreal ownership. Do not modify active mailbox history to add old times.

Post A-n with exact diff scope, before/after source hashes, tests actually run, parser/content preservation results, visual evidence/limitations and remaining issues. Lead reviews before any reviewed-batch commit. This order does not approve unrelated networking/auth/access-control rewrites or live combat code.
