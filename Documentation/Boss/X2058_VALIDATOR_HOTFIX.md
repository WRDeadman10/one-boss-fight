# X-2058 hotfix: A-854 BUG-1..5 and whitespace parity in the Sevarog input validators

Assigned by X-2058 (lead Codex) to C (implementer), 2026-11-12. **SOURCE CHANGED:**
- `Scripts/Tools/validate_pending_definition_inputs.py`
- `Scripts/Tools/validate_owner_approval_envelope.py`
- one fixture in `Scripts/Tools/test_validate_pending_definition_inputs.py`

New: `Scripts/Tools/test_x2058_validator_hotfix.py`. The historical BK-81..100 findings and reports are unchanged. **No Unreal, asset, lock, log or authoring work was done. Nothing here approves project data; X-1991 is still open.**

## Fixes

| Bug | Where | Fix |
|---|---|---|
| **BUG-1** | pending `main()` | The command line now parses through `loads_strict()`, which uses the duplicate-key hook plus `parse_constant` and refuses `NaN`, `Infinity` and `-Infinity` **anywhere** in the manifest, including `definition_target`. Such a manifest exits 1. |
| **BUG-2** | pending `validate()` | New `NATIVE_RANGES`, with the same bounds as the envelope's `FIELDS` (parity is test-pinned). Valued rows (`SOURCE_BACKED`, `SOURCE_BACKED_AWAITING_OWNER`) **and** the candidates on `OWNER_DECISION_REQUIRED` rows must sit inside the native C++ range. `PhaseId` must be `Phase_1`. **Why "source-backed" is not "any value":** a source can be cited for a number the engine would refuse, for example `MaxHealth` at or below 1 (`RPGBossStatsAdapters.cpp:95`), so the manifest must not record it as usable input. |
| **BUG-3** | envelope `check_decision` (PhaseId) | The quote must contain `Phase_1` (or `phase 1`) as a **whole token**, so `Phase_10`, `Phase 12`, `XPhase_1` and `Phase_1x` no longer approve it. |
| **BUG-4** | envelope `validate` | After all decisions are checked, **one quote may approve at most one field**. The shared alias "rate", used by both `Stats.PostureRegenRate` and `Phases[Phase_1].RateMultiplier`, can no longer let `Rate 1.0.` approve both. A malformed, unhashable `field_path` is skipped safely. |
| **BUG-5** | envelope `--verify-source` | A message id that appears in more than one header refuses the envelope. That includes a second Owner block and a non-Owner header reusing the id. This matches `bind_owner_approval.py`. |
| **Whitespace parity** | envelope `--verify-source` | `reply_text` must **equal the stripped body exactly**, the canonical form that is also hashed. Padded reply text is refused even when its hash matches, matching the binder. The error keeps the original wording, "does not exactly match the complete owner message", and adds "(it must equal the stripped body; no padding)". |

**Fixture update (no assertion weakened):** the pending suite's builder gave every valued row `1.0`, which is now out of range for `MaxHealth`. It now uses `1500.0`, the X-1991 candidate, for `MaxHealth` only.

## Tests and results

From `Scripts/Tools`:

| Suite | Result |
|---|---|
| **New: `test_x2058_validator_hotfix.py`** | **16/16 OK** |
| pending base + adversarial | 30/30 |
| envelope | 20 (19 pass, 1 Windows-symlink skip, unchanged) |
| binder | 11/11 |
| BK-81 boundary contract | 12/12 |
| planner | 12/12 |
| BK-191 hotfixes | 16/16 |

The real manifest `Documentation/Boss/BK76_SEVAROG_DEFINITION_INPUTS_PENDING.json` still validates with the same counts (SOURCE_BACKED 1, AWAITING_OWNER 3, OWNER_DECISION_REQUIRED 5).

New coverage, by class:
- **`Bug1StrictJsonCli` (3):** NaN, Infinity and -Infinity exit 1, tested through a patched file read with no file written; a clean manifest exits 0; duplicate keys are still refused.
- **`Bug2NativeRanges` (4):** lower, upper and phase-multiplier edges for all 8 float fields, both as values and as candidates; the exact `MaxHealth = -5.0` reproduction; `PhaseId` must be `Phase_1`; range-table parity with the envelope.
- **`Bug3PhaseIdTokenIdentity` (2):** 4 non-token forms are refused; 3 exact forms still pass.
- **`Bug4QuoteReuse` (3):** the `Rate 1.0.` reuse is refused, with no approvals listed; distinct lines are still valid; an unhashable field does not crash.
- **`Bug5AndWhitespaceSourceVerification` (4):** a single block still verifies; a duplicate Owner id is refused; a non-Owner header reusing the id is refused; a padded reply with a matching hash is refused. These use a throwaway OS temp directory, as the existing envelope suite does.

## Limits

- **No before/after proof:** both validators are untracked (not in HEAD), and no copy was saved before editing, so the new tests were **not** re-run against the pre-fix code. The reproductions follow A-854's exact inputs, which A-854 confirmed against the pre-fix code.
- Native ranges are mirrored from the C++ by hand, and the parity test only binds the two Python tables to each other. The C++ check `RPGBossPhaseAdapters.cpp:138`, that the float32 reciprocal is finite, is stricter than these Python checks and is not modelled (noted in A-854).
- The quote-reuse rule applies to all approvals, not only ambiguous aliases. Each field now needs its own owner line, which is the stricter reading.

## Follow-up: X-2062 / X-2064 malformed-input crashes (2026-11-12)

- **X-2062:** a valued float row, or a candidate row, with an unhashable `field_path` (for example `["Owner","Approval"]`) raised `TypeError` at the `NATIVE_RANGES` lookup that this hotfix had added. Both lookups now require `isinstance(field, str)` first.
- **X-2064:** `status: ["PENDING"]` raised `TypeError` at the `STATUSES` membership test. This predates X-2058. The check is now `not isinstance(status, str) or status not in STATUSES`, and gives the normal "status refused" error.
- **Regressions added to `test_x2058_validator_hotfix.py`** (`X2062X2064MalformedRowValues`): both X-2062 shapes and the X-2064 status return an invalid result. A per-key fuzz (every row key of a valued float row, a name row and a candidate row × 9 malformed values) raises nothing. **`Ran 19 tests ... OK`.**
- **Neighbour suites** (from `Scripts/Tools`):

  | Suite | Result |
  |---|---|
  | pending | 30/30 |
  | envelope | 20 (1 skip) |
  | binder | 11/11 |
  | planner | 12/12 |
  | BK-191 | 16/16 |
  | BK-81 | 12/12 |
- **Envelope fuzz:** an extra one-off fuzz of the envelope validator (every decision, owner-message and top-level key × 9 malformed values) raised no exception.
