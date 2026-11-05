# Queue V C086–C090 — closeout and next-queue boundary

Status: C086 partial/deferred; C087–C089 completed; C090 deferred to Claude per C-928. C-929 has since reported BUILD-232 green and accepted X-1305–X-1308. This batch makes no performance or product-scope change.

## C086 — issue sweep after performance work

Round 6 has no returned result bundle, no owner-approved performance setting has been applied, and there is no post-change evidence. Therefore a “post-performance” issue disposition would be premature. Keep existing performance issues open as written, including target GPU and packaged-performance limitations; re-run the issue sweep after an approved setting/build and confirmation data arrive. No KI was closed or rewritten from absent evidence.

## C087 — Claude decision index

Extended `Documentation/DECISIONS.md` with concise C-878–C-928 task/decision summaries, following its existing C-833–C-877 index. The entries reflect the mailbox sequence; they do not override project policy (notably, the repository rule still prohibits Codex commit/push). X-1307/X-1308 are Codex reports and are not Claude C-decisions.

## C088 — build evidence navigation

Added a BUILD-223–BUILD-232 index to `Documentation/TEST_PLAN.md`, linking retained build logs or pair output for 223–231 and marking BUILD-232 as planned in C-928, without a result verdict. Link targets were checked for existence.

## C089 — offline tools README

Added entries for `mailbox_decision_digest.py`, `check_bench_kit.py`, and `check_packaged_g044_cook.py` to `Scripts/Tools/README.md` with their read-only/validation purpose.

## C090 — Queue W creation

Claude's C-928 says the Queue W roll is hers at task 90. Do not create a competing Queue W. Resume Codex queue work after the Lead publishes the next queue or assigns its Codex lane.

## C-929 hotfix review follow-up

Inspected the two Lead test fixes against current source. `RPGCombatCatalog.cpp:148` emits `<BuildId>.LegacySlot: invalid/duplicate`, and the native assertion now checks the exact stable suffix. The comparison-only unknown asset path concatenates `/Game/` and the remainder; the one full path literal left in the fixture is under the existing always-cook Boss01 content root. The BUILD-232 receipt states build exit 0, suite exit 0, 478 success, zero failures. This is a source/evidence review; Codex did not run Unreal or tests.
