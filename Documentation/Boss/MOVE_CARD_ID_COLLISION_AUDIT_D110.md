# Boss MoveCard ID collision audit — D110

**Scope:** duplicate-checker normalization and same-file/cross-file behavior, including available fixtures. Static review only; the CLI was not run.

`Scripts/Tools/check_move_card_ids.py` accepts one or more JSON exports, deduplicates repeated input paths after `Path.resolve()`, and reads either a top-level list or an object's `cards` list. For each card it uses `MoveId` or, when falsey, `moveId`; truthy identifiers are grouped by their exact JSON value and reported when the accumulated row count exceeds one (`check_move_card_ids.py:12-28`).

The checker performs no string trimming, case folding, Unicode normalization, type conversion, or other identifier canonicalization. Thus `"A1"` and `"a1"`, or `" A1"` and `"A1"`, are distinct; exact same-string IDs collide both within one export and across separate exports. Passing the same resolved file path more than once does not itself create a duplicate, but repeated card entries inside that file do. Output reports each exact duplicate key and the source paths; exit status is 1 if any duplicate key exists and 0 otherwise.

No dedicated fixture or test file referencing this tool was found in the searched `Scripts` paths or the docs index. Therefore normalization behavior is source-derived, not fixture-proven. Additional unvalidated input shapes include malformed JSON, non-object card rows, non-string/hashable IDs, and an object whose `cards` member is not a list; these may raise exceptions rather than produce a controlled refusal. The script is read-only.

**Acceptance result:** exact-string and cross-file collision semantics are explicit from source, and duplicate rows in the same file also collide. There are no discovered fixtures proving these cases, so acceptance is only source-audited; no normalization or test behavior should be assumed beyond the exact lookup above.
