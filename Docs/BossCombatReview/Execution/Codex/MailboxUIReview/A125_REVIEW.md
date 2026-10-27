# A125 / AG08 Rev2 independent review

Verdict: ACCEPTED for the bounded owner-requested timestamp, append-order and mobile/tablet reading changes. No gameplay or runtime gate acceptance. Reviewed 2026-10-27 local; supersedes A124's responsive/touch-target blockers, preserves that failed iteration.

## Actual artifacts and checks

- Viewer SHA256 `921e6eaa319cd30a73aba93f521daeb943a62d0ed20f2755e68ebcbdf44887b9` and test SHA256 `ece00a3c0720b3204f7965a78c2f6fcfd5dc7cb172e4bbc73ea74159ef7b71a9` match A125. AG explains prior test snapshots; historical snapshot provenance is author-reported, not independently recovered.
- `python -B -I Docs/BossCombatReview/Execution/Antigravity/test_mailbox_ui.py`: 12/12 pass. These are Python/temp-file/static-contract checks, including simulated width predicates; they are not browser layout tests.
- `python -B -I Docs/BossCombatReview/Execution/Codex/MailboxUIReview/check_parser_fidelity.py`: all461 ordered IDs/bodies equal independent raw protocol slicing; all456 pre-change baseline bodies retained, no duplicate IDs. Normalized text comparison, not pixel/byte-exact rendering.
- Actual running browser detail remains visible at390,899,900,901,980,1023,1024,1280 CSS-pixel widths. At widths below1024 feed is hidden while selected detail fills width; at1024/1280 both panes are flex-visible. Document scroll width equals viewport at every sampled width. Thus prior980px hidden-detail defect is resolved.
- At390x844 A125 body is579.5px high and all four navigation controls are50px high. At899 through1023 controls are44px high and body580px. Older navigation changes A125 to X187, with recorded timestamp and body rendered. No horizontal overflow in sampled state. Screenshots: `AG08_rev2_phone_390x844.png`, `AG08_rev2_tablet_980x800.png`.
- Auto-follow is unchecked by default. Source now reads its checked state on polling and selects new arrival only when checked. Real arrival behavior with checkbox checked has not been independently exercised; no fake message was posted to the real mailbox. Stable older-message reading during a legitimate subsequent review append is checked separately in the ledger.

## Remaining limits and queue

Desktop dashboard occupies much of800px height: at1024x800 selected A125 body is48px high; at1280x800 it is202.5px. Both panels are visible, but desktop reading remains cramped. This is outside the owner's mobile-detail fix; record it rather than claiming a universal layout overhaul. No additional live-file edit is assigned now. AG's blanket “without reducing reading viewport” wording should be narrowed to the measured mobile result, and its report should distinguish simulated/static checks from this independent rendered evidence.

After legitimate X188 review append, running browser displays new X188 card/count462 while selected X187 remains unchanged with Auto-follow unchecked. This verifies the default stable-reading path with a real incoming poll. Viewport reset and temporary tab closed afterward.

AG may close the narrowly reviewed UI batch under existing owner git authority, excluding unrelated dirty work, and resume AG07/X181 final corrections immediately. Codex does not commit, restart servers or operate Unreal. No live incoming checked-mode proof, real composer submission, engine test, performance or visual-gameplay proof is implied.
