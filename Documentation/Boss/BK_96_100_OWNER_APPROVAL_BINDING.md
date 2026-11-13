# BK-96..100: binding a raw owner message to the approval envelope and the repair planner

Assigned by X-2003 (lead Codex) to C (implementer), 2026-11-11. New files only; no existing author, runner, driver, helper or validator edited; no Unreal, build, PIE, assets or locks; no project values.

**This does not authorize data authoring or a C-1155 run. No owner answer to X-1991 exists.**

## BK-96: current handoff, and the gap it leaves

The two existing interfaces:
- `validate_owner_approval_envelope.validate(envelope, root, verify_source)` returns only `{valid, errors, approved_for_review, rejected, unresolved}`. With `verify_source` it reads `Documentation/TEAM_MAILBOX.md` and requires the complete owner block body to equal `reply_text`. The CLI prints that JSON (exit 0 when valid, 1 otherwise).
- `plan_sevarog_definition_repair.plan_repair(envelope_result, snapshot, context, owner_source)` (with the lead's X-2003 hotfix) accepts an `envelope_result` dict and a caller-built `owner_source` (sender, message_id, reply_sha256, path).

The gap (X-2003): nothing ties the `envelope_result` and `owner_source` passed to the planner to the same raw owner message. A caller could pair a valid result with any source object.

## BK-97: binding adapter (`Scripts/Tools/bind_owner_approval.py`, pure Python)

`bind_owner_approval(raw_text, message_id, envelope)` takes no caller-supplied source:
1. In the raw text (a single block or a mailbox excerpt), finds **exactly one** `### [<id>] Owner -> ...` block. It refuses:
   - a missing id, or a non-owner id;
   - duplicate blocks with the same id;
   - a block from a sender other than Owner;
   - an empty body;
   - a final block without a trailing newline (possibly truncated).
2. Requires `envelope.owner_message.message_id == <id>`, `path == Documentation/TEAM_MAILBOX.md`, `reply_text ==` the stripped block body (exactly: altered, partial or padded text is refused), and `reply_sha256 ==` SHA-256 of that body.
3. Runs `validate(envelope)` in memory; the raw text replaces the file read.
4. Derives `owner_source = {sender: Owner, message_id, reply_sha256: sha256(body), path}` internally.
5. Returns `{bound, errors, approval_complete, write_permitted=False, envelope_result, owner_source}`. `approval_complete` is true only when the envelope is valid, with all 9 fields approved and nothing unresolved or rejected. A refused binding carries no `owner_source`.

`plan_from_bound(binding, snapshot, context, allow_write=False)` is the only handoff to `plan_repair()`:
- It refuses unbound or forged bindings.
- It defaults to `mode=dry_run`.
- It refuses `mode=write` unless `approval_complete` and `allow_write=True`.
- It always passes the internally derived `owner_source`, so the planner's provenance records cite the bound message.

## BK-98: tests (`Scripts/Tools/test_bind_owner_approval.py`, 11 synthetic tests)

**Positive cases:**
- A complete message binds, with the internally derived source matching the body hash.
- A single-block input binds, and so does a final block that ends with a newline.

**Refusals:**
- Mismatched ids: the envelope names a different message, the id is absent, or it is an agent id.
- Altered body (text changed in the mailbox), truncated `reply_text`, a wrong hash, or `reply_text` with extra padding.
- Duplicate blocks, a truncated final block, a non-owner sender, an empty body, and empty raw text.
- Malformed metadata: wrong path, `owner_message` not an object, an envelope claiming authorization.

**Approval completeness:**
- A partial or unresolved approval binds, but is not complete.
- A missing decision is refused.

**Planner handoff:**
- It is dry-run by default (no save step; provenance cites `O-77`).
- Write is refused without `allow_write`, accepted with it plus a complete approval, and refused when the approval is incomplete.
- Unbound or forged bindings are refused.

**Contract:** no Unreal, no file or lock access in the adapter; the signatures accept no caller-supplied `owner_source`.

## BK-99: how a later editor executor should use it

1. Read `Documentation/TEAM_MAILBOX.md` once, and pass that same text to `bind_owner_approval` together with the owner message id and the envelope built from that message. Do not use any separately supplied validator result or source object.
2. If `bound` is false, stop. If `approval_complete` is false, stop: X-1991 is still unresolved, and only a dry run may be shown.
3. Take a locked readback snapshot of `DA_Boss_Sevarog_Draft` (asset path, file SHA-256, stats, phases, fields), then call `plan_from_bound(binding, snapshot, {"operation": "in_place_update"})`, which is a dry run. Show the diffs to the lead.
4. Only after explicit lead and owner go-ahead: take both C-1155 locks under one token, make the file backup, confirm its hash equals the before-hash, then call `plan_from_bound(..., context with mode=write, explicit_write=True, locks, backup, allow_write=True)`.
5. Execute exactly the returned steps. Run `verify_readback(plan, after_snapshot)`; on failure, restore the backup. Release the locks in `finally` on every path.
6. Then run the encounter readback and the pinned suite, and only then the BK-59 deferred PIE.

The executor needs its own source contract (the BK-82 style) and a locked dry run first; it is not implemented here.

## BK-100: validation (exact)

- From `Scripts/Tools`:
  - `python -I -m unittest discover -s . -p "test_bind_owner_approval.py"` → `Ran 11 ... OK`.
  - Neighbors unchanged: `test_validate_owner_approval_envelope.py` → `OK (skipped=1)` (the lead's Windows symlink skip); `test_plan_sevarog_definition_repair.py` → `OK`.
- `python -I -m py_compile Scripts/Tools/bind_owner_approval.py Scripts/Tools/test_bind_owner_approval.py` → OK.
- `git diff --check` on both files → clean.

## Limits

- Truncation is detected only for a final block without a trailing newline. A block cut cleanly at a line boundary with a newline is indistinguishable from a complete one. The executor should pass the whole mailbox file, so the block is followed by the next header or by the file end.
- Body equality is on stripped text; leading or trailing whitespace differences are ignored, but interior whitespace must match exactly.
- The adapter trusts its own copy of the validator and planner modules (loaded from `Scripts/Tools`); an executor must load the same files.
- Owner choices for X-1991 are unchanged: MaxHealth/MaxPosture (and the poise mapping), regen delay/rate, threshold, and the three multipliers.

## Lead review / hotfix (2026-11-11)

Review found that `plan_from_bound()` treated any caller-built dictionary with `bound=True` as authentic; the existing forged-binding test only covered `bound=False`. A caller could therefore forge an approval result/source pair and reach a write plan. Fixed by issuing read-only, process-local binding capabilities registered by the adapter; planner handoff now requires the exact issued object and uses a private deep-copied payload. Added tests for a forged `bound=True` dictionary, an unissued capability object, altered returned copies, and accepted bound provenance staying intact. Focused binding tests pass 11/11, planner tests 12/12, Python compilation and scoped diff-check pass.

Remaining source trust boundary: the adapter is deliberately in-memory and cannot itself prove that a caller-provided `raw_text` was read from the real mailbox file. Any future executor must load the complete mailbox directly from `Documentation/TEAM_MAILBOX.md` and pass that exact text to the binder; body/hash agreement alone does not authenticate arbitrary text. No owner reply to X-1991 is present; no authoring or C-1155 is authorized.
