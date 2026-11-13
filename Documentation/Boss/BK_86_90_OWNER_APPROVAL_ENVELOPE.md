# BK-86..90: owner approval envelope (synthetic review path)

Assigned by X-1999 (lead Codex) to C (implementer), 2026-11-11. New files only; no existing author, runner, driver, helper or validator edited; no Unreal, build, PIE, assets or locks.

**No owner answer to X-1991 exists. This work approves nothing, authors nothing, and does not unblock C-1155.** It prepares a safe path for reviewing the owner's reply once it arrives.

## BK-86: envelope schema (`onebossfight.owner-approval-envelope/v1`)

The full schema is in the docstring of `Scripts/Tools/validate_owner_approval_envelope.py`. In summary:

- **Top level.** Exactly these keys: `schema`, `envelope_state="OWNER_DECISION_RECORD"`, `production_manifest=false`, `authoring_authorized=false`, `request_reference="X-1991"`, `owner_message`, `decisions`.
- **`owner_message`.**
  - `message_id`: an owner mailbox id, `O-<n>` or `H-<n>`; agent ids `X-`, `C-` and `A-` are refused.
  - `sender`: exactly `Owner`.
  - `path`: repo-relative.
  - `reply_text`: the exact reply.
  - `reply_sha256`: SHA-256 of `reply_text`.
- **`decisions`.** Exactly one entry for each of the 9 fields (the 4 Stats plus the 5 `Phases[Phase_1]` fields), each `{field_path, decision, value, quote}`.

The four decisions:
- **`APPROVE_CANDIDATE`:** the value equals the X-1991 candidate (1500, 100, 6, 13, `Phase_1`, 0.6, and 1.0 for each multiplier).
- **`APPROVE_VALUE`:** the owner's alternative, which must differ from the candidate.
- **`REJECT`:** value `null`; the quote carries a rejection word.
- **`UNRESOLVED`:** value `null` and quote `null`. This is required for anything the owner did not answer explicitly; the validator never infers.

## BK-87/89: validator (`Scripts/Tools/validate_owner_approval_envelope.py`, read-only)

**Envelope-level checks:**
- Strict JSON (CLI): duplicate keys and `NaN`/`Infinity` constants are refused.
- Exact key sets and flags; unknown top-level keys are refused, approval claims included.
- The sender must be `Owner` with an owner id; the request reference must be X-1991.
- The reply hash must equal the reply text.

**Per-decision checks:**
- Every quote must occur verbatim in the reply and must name its field (alias list).
- An `APPROVE_*` value must be finite and inside the native range:
  - MaxHealth > 1 (`RPGBossStatsAdapters.cpp:74`, `NativeHealthOverrideFloor = 1` at `RPGBossStatsAdapters.h:38`).
  - MaxPosture > 0.
  - Regen delay and rate >= 0 (`RPGBossStatsAdapters.cpp:84`).
  - Threshold in (0, 1] (`RPGBossPhaseAdapters.cpp:122`).
  - Multipliers > 0 (`RPGBossPhaseAdapters.cpp:131`).
- The approved value must appear as the only number in its quote, with no ambiguity marker (or, either, maybe, `?`, not sure) and no rejection word.

**Envelope completeness:** partial, duplicate and extra decisions are refused.

**`--verify-source`:** `reply_text` must occur verbatim inside the body of the `### [<id>] Owner -> ...` message in the cited file.

**Output (BK-89):** only `{valid, errors, approved_for_review, rejected, unresolved}`. `approved_for_review` is emptied whenever the envelope is invalid. The tool writes nothing and emits no manifest; a static test bans write, open, dump, subprocess, unreal, unlink and mkdir.

## BK-88: initial test suite (`Scripts/Tools/test_validate_owner_approval_envelope.py`, 17 tests, synthetic replies and temp files; pre-hotfix)

**Valid:** full explicit decisions (9 approved for review); an unanswered field kept `UNRESOLVED` and not inferred; a rejected candidate recorded; a zero regen delay (inside the native range).

**Refused:**
- Partial, duplicate and extra decisions.
- `UNRESOLVED` carrying a value or quote.
- Ambiguous quotes (`4 or 6`, `0.6?`) and multi-number quotes.
- Conflicting approvals (`1500 no`), candidate/alternative mislabels, a value missing from its quote, and a quote that names the wrong field.
- REJECT with a value, or without a rejection word.
- A tampered reply hash, and a quote that is not in the reply.
- A wrong sender, agent ids, a malformed id, and a wrong request reference.
- Out-of-range values (threshold 1.2 and 0, health 1, negative delay, zero multiplier) and non-finite or ill-typed values (NaN, Inf, bool, string).
- A manifest or authorization claim, a wrong state or schema, and an unknown top-level key.
- Duplicate JSON keys and a `NaN` constant through the CLI (exit 1; the good case exits 0).
- `--verify-source` with a missing header, or with the reply under another message.

Also covered: the output-contract and read-only checks.

## BK-90: validation (exact)

- From `Scripts/Tools`: `python -I -m unittest discover -s . -p "test_validate_owner_approval_envelope.py"` → `Ran 17 tests ... OK` (Claude's original suite).
- `python -I -m py_compile Scripts/Tools/validate_owner_approval_envelope.py Scripts/Tools/test_validate_owner_approval_envelope.py` → OK.
- `git diff --check` on both files → clean.
- Source citations re-checked by grep: `RPGBossStatsAdapters.cpp:74`, `:84`; `RPGBossStatsAdapters.h:38`; `RPGBossPhaseAdapters.cpp:122`, `:131`.

## Limits

- Numbers are matched literally: `60%` is not read as 0.6, and `1,500` splits into two numbers. The owner's reply must use the plain numeric form, or the field stays `UNRESOLVED` and gets a follow-up question.
- The field aliases are heuristic: the check confirms the quote mentions the field, not that the owner meant it. A human or the lead still reviews `approved_for_review`; nothing is applied automatically.
- The envelope is assembled by an agent from the owner's reply; the validator checks that it is faithful to the cited text, not that the agent captured every nuance. Anything the owner did not state plainly must stay `UNRESOLVED`.
- After a valid envelope, the remaining gaps from BK-81..85 still apply: no non-destructive repair path for the existing invalid Phase_1 row, and no Stats writer.

## Lead review and hotfix

Lead review found fail-open cases: malformed unhashable decision fields could raise; `reply_text` could be a cherry-picked substring of a longer Owner reply; quotes could be cherry-picked fragments of a reply line; arbitrary repository files could be cited instead of the mailbox; symbolic links could escape the chosen root; and aliases such as `health` matched inside words like `unhealthy`. Very large integers could also overflow numeric validation, and conditional wording such as `if`/`unless` was not treated as ambiguity.

The validator now rejects all of these. Source verification requires exactly `Documentation/TEAM_MAILBOX.md`, resolves and confines it beneath the selected root, and compares the normalized whole message body to `reply_text`. A decision quote must equal a complete non-empty reply line; field aliases use token boundaries; conditional phrases are refused. Malformed fields and huge numbers fail closed. Synthetic suite now runs 20 tests: 19 pass, with one symlink escape test skipped because this Windows environment cannot create the symlink. Compilation and scoped diff-check pass. No real Owner reply, project values, asset, or authoring action was used.
