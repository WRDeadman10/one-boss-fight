# BK-121..125: binding executor receipts to their owner mailbox source

Assigned by X-2012 (lead Codex; X-2013 early findings folded in) to C (implementer), 2026-11-11. New files only (`Scripts/Tools/bind_receipt_source.py`, `Scripts/Tools/test_bind_receipt_source.py`). The validator, binder, contract, author and runner are unchanged; no filesystem, Unreal, process, network, assets or locks.

**This proves text binding only: that a receipt names an owner message present exactly once, unaltered, in the given text. It does not prove the text is the real mailbox file, that any runtime event happened, or that a write was authorized. Owner gate X-1991 is still open.**

## BK-121: rule anchors

| Rule | Binder (`bind_owner_approval.py`) | Envelope validator (`validate_owner_approval_envelope.py`) | Receipt validator (`validate_sevarog_executor_receipt.py`) |
|---|---|---|---|
| Owner id `O-<n>` / `H-<n>` | `:38` (`OWNER_ID`), checked at `:87` | `:53` | `_source`, `:61-74` |
| Header form `### [<id>] <sender> -> …` | `:39` (`HEADER`) | `:235` (requires `Owner -> `) | — |
| Exactly one block; sender Owner | duplicates refused `:96`; non-owner `:100` | header search `:235-237` | sender must be Owner (`_source`) |
| Truncation and empty body | unterminated final block `:106`; empty body `:110` | — | — |
| Mailbox path | `:40` | `:59` | `:6` |
| Body equality | `reply != body`, stripped body, `:130` | `body.strip() != reply.strip()` `:241` | — |
| Hash form | `sha256(stripped body)`, `:132` and `:141` | `sha256(reply_text)` `:222` | `source.sha256` 64-hex |
| Source required for every outcome | — | — | `source_required = True`, `:156` (all 6 outcomes after X-2012) |

The two hash forms agree whenever `reply_text` equals the stripped body, which the binder enforces. This adapter uses the binder's form.

## BK-122/123: adapter

`bind_receipt_source(raw_text, receipt, validate_receipt, extract_owner_block)` returns `{bound, errors, receipt_result, derived_source, proves: "text-binding-only"}`:
0. **Dependency boundary (X-2013):** the module imports only `hashlib`, never resolves `__file__` or loads sibling files, and has no default loader. The caller injects the receipt validator's `validate_receipt` and the binder's `extract_owner_block`, so the rules stay theirs and cannot drift. Missing or non-callable rule functions are refused.
1. `validate_receipt(receipt)` must be valid. A malformed receipt is refused before any source check, and `derived_source` stays `None`.
2. The injected `extract_owner_block(raw_text, receipt.source.message_id, errors)` refuses missing, duplicate, non-Owner and empty blocks, and a final block whose text does not end in a newline. It cannot detect a final block cut cleanly at a line end (see Limits).
3. It derives `{message_id, sender: Owner, path: Documentation/TEAM_MAILBOX.md, sha256: sha256(stripped body)}` and requires it to equal `receipt.source` field for field.

The adapter never mutates its inputs, never reads files, and never authorizes anything.

**Invocation (future executor):** read `Documentation/TEAM_MAILBOX.md` once, and pass that exact text, the run's receipt object, `validate_sevarog_executor_receipt.validate_receipt` and `bind_owner_approval.extract_owner_block` to `bind_receipt_source`. Treat `bound=False` as an evidence failure.

## BK-124: tests (11, synthetic)

- **Every outcome binds:** `DRY_RUN_ONLY`, `WRITTEN_AND_VERIFIED`, `FAILED_RESTORED`, `FAILED_RESTORE_NEEDS_OPERATOR`, `REFUSED_AFTER_LOCKS` and `LOCK_RETAINED_NEEDS_OPERATOR` each bind to a matching owner block, and each derived source equals the receipt's.
- **Altered text or hash:** an altered block body, a padded receipt hash, or a receipt that hashed only part of the message is refused.
- **Ids:** a wrong id (not in the text) or a repeated id (duplicate block) is refused.
- **Truncated or empty:** a truncated final block, an empty body, or empty text is refused.
- **Agent-authored source:** a block whose sender is not Owner, or a receipt naming an agent id, is refused.
- **Malformed receipt** (unhashable outcome, missing or string source, wrong path, non-dict receipt): refused with no derived source.
- **Inputs:** neither the receipt nor the text is mutated.
- **Injection required:** missing or non-callable rule functions are refused, and calling without them raises `TypeError` (no hidden loader).
- **Clean cut limit:** a final block cut at a line end binds only to a receipt that hashed the cut text, never to the full message's hash.
- **No I/O at import (AST):** the only import is `hashlib`; no `__file__`, `open`, `importlib`, `Path`, `exec`, `eval` or `__import__`; the module top level holds only the docstring, the import, constants and the function.
- **No I/O at runtime:** with `open`, `io.open`, `os.open/stat/listdir/scandir` and `Path.open/read_text/read_bytes/exists` patched to raise, a binding and a refusal both complete.

## BK-125: validation (exact)

- From `Scripts/Tools`:
  - `python -I -m unittest discover -s . -p "test_bind_receipt_source.py"` → `Ran 12 tests ... OK` (lead added malformed injected-validator-result regressions).
  - Neighbors, unchanged: `test_validate_sevarog_executor_receipt.py`, `test_validate_sevarog_executor_receipt_adversarial.py` and `test_bind_owner_approval.py` all pass: 12/12, 12/12 and 11/11.
- `python -I -m py_compile Scripts/Tools/bind_receipt_source.py Scripts/Tools/test_bind_receipt_source.py` → OK.
- `git diff --check` on both files → clean.

## Limits

- The adapter checks what it is given. Proving the text is the real mailbox is the executor's job: it must read the file itself and should record the file hash it read.
- A final block that was truncated cleanly, ending on a full line with a newline, cannot be detected. Pass the whole mailbox so the block is followed by the next header or by the file end.
- The adapter trusts the injected functions to be the real validator and binder; wiring them is the executor's job, and the tests use the real ones.

## Lead review/hotfix

Review found that a malformed injected validator result such as a list raised while formatting its errors. The adapter now rejects non-object validator results, malformed error collections, and a claimed-valid result without an object `source` record. Regression coverage added. Adapter suite 12/12; receipt 12/12; receipt adversarial 12/12; binder 11/11; py_compile passes. This does not change the documented trust boundary: the caller must inject the canonical validator and binder functions.
