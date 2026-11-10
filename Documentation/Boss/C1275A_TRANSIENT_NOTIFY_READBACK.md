# C-1275a — transient montage notify readback

## Result

READY for Claude's saved-asset authoring and post-save readback. The Editor-only C++ wrapper now exposes deterministic notify rows with class, trigger time, duration, notify track index, montage slot(s), and segment animation path/length. Passing an empty destination to `URPGMontageWrapperLibrary::CreateRetargetWrapper` creates the same retarget copy in `/Engine/Transient`; it does not register or save a content asset. The Python readback driver imports its sibling `Scripts/Editor` module and compares source rows to transient target rows.

## Verification

- Python AST parse: PASS.
- Focused offline contracts: 5/5 PASS.
- C-1155 locked Editor Development build: exit 0.
- C-1155 full `OneBossFight` suite: 506/506 PASS; DD27j manifest hash `cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec`.
- Non-saving Editor readback: all four source montages produced transient wrappers; every row matched on notify identity/timing/duration/track/slot, and every target segment matched the selected retarget sequence path and length. Receipt ends `RESULT=PASS wrappers=4 transient=1 saves=0`.
- Both C-1155 locks released; no UnrealEditor process remains. No PIE, asset save, package save, or content mutation was performed.

Evidence: `Docs/BossCombatReview/Execution/Codex/C1275A_TRANSIENT_NOTIFY_READBACK/Run_20261110_160407/` (`status.txt`, `lock_result.txt`, `build.log`, `suite.log`, `transient_readback.log`).

## Scope boundary

This validates the wrapper-copy/readback path in memory. It is not saved-package verification and does not authorize asset authoring. Claude still owns `author_greystone_player.py --write` and the post-save readback.
