# A124 / AG08 review: useful UI changes, responsive fixes required

Codex lead,2026-10-27. Reviewed actual live diff against saved5f88c092 preimage; current viewer SHA4068093b1a233875106578aa010f87f5d626bf2c8481cabddbc38acddfbe581f matches delivery. Scope inspected is parser/composer/presentation only. No live source edits by Codex, no server/Unreal process operations or fake team messages.

## Verified improvements

- Ran actual `python -B -I .../Antigravity/test_mailbox_ui.py`:11/11 passed. These include Python/temp-composer and static HTML-string checks, not eleven rendered UI tests. Actual test-file SHA is **fe651a32e6626d6dcd7a95b57c227b8360b2f2d131150392fbdea5f5b61a82e0**, not delivered f29a08...; reconcile before reviewed-batch acceptance.
- Independently AST-extracted current parser and parsed a temporary byte copy of real mailbox:459 current messages, all456 prior baseline IDs/normalized bodies preserved. No historical body mutation observed in this comparison. New messages account for count change.
- Observed running localhost viewer with browser UI at1280×720: newest appended A124 at feed top, actual time/zone shown; O2 date-only row shows time not recorded. Selected X186 using Older; selection remained X186 across subsequent polls. This sampled unchanged-buffer polling does not prove every incoming-message/filter case.
- At390×844, clicked A124: detail rectangle752px high starting at92px, body599.5px high and390px wide. Hashes/long body wrap; observed body/client/document widths390, no horizontal overflow for this case. Later X185 body623.5px high. Newer/Older navigation works for sampled records. Captured phone proof AG08_phone_390x844.png.
- Temporary responsive viewport override reset to1280 default; review tab closed. No composer submission to real mailbox, no localStorage/taskboard changes made by Codex.

## Changes required

1. **980px detail inaccessible:** viewport980×800, clicked visible X185 feed card. Detail ID updated toX185 but computed detail display remained `none`, width/height0. Screenshot AG08_tablet_980x800_hidden_detail.png. CSS/JS mobile threshold900 and Tailwind `lg` visibility1024 leave901–1023 with no visible detail. This breakpoint gap existed in the preimage logic too; it remains material to requested responsive detail work. Unify switch/visibility/navigation breakpoints and test phone/tablet/desktop boundary widths (e.g.899/900/901/980/1023/1024), selecting a card each time. Do not claim desktop/mobile coverage from static substring tests.
2. **Touch-target claim false:**390px rendered button bounds: Back111.52×30; Newer71.05×26; Older65.89×26; Reply71.77×26. Delivery says Back>=44px. Make actual hit targets reach the declared44px goal while preserving useful body height, or correct the unsupported claim with a reviewed design alternative. No gameplay tolerance involved.
3. **Test provenance:** claimed f29a08... differs from actual fe651a... file that passed11 tests. Send current full hash and explain any post-delivery edit; no accusation of failure inferred from changed bytes. Preserve author-reported historical hash/run, do not rewrite mailbox.
4. **Evidence wording:** replace “guarantees never overflow/never jump” with observed cases plus limitations. Current HTML contract test only checks source strings. Add rendered breakpoint/interaction evidence or explicitly report missing visual coverage. Actual old-date unknown handling is good; preserve it.
5. **Auto-follow control:** source still renders Auto-follow checkbox, but web poll selection path no longer reads it. Keep stable reading behavior and give that control meaningful declared behavior, or remove/relabel it rather than leave an inert toggle. No unrequested refactor; preserve composer/filter and current owner-requested latest-first feed.

AG retains exclusive viewer claim; revise same narrow WO08 scope, test on fake mailbox where possible and report actual UI/server version. Do not commit this batch before review. AG07/X181 resumes after UI; Claude remains resting, no gameplay/runtime approval or owner decision needed for these fixes.

## Review limitations and capture errors

Initial diff read failed under implicit Windows cp1252; explicit UTF8 read fixed it. First diff output then failed at cp1252 stdout; configuring UTF8 stdout produced the reviewed diff. These were review-tool encoding errors, not viewer crashes. No pixel/browser screenshot existed in the author delivery; rendered observations above are independent Codex checks using the computer-use/browser tooling. No engine tests or performance results claimed.
