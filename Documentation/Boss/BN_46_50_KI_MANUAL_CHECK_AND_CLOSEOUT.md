# BN-46..50: last manual checks and the cumulative lane BN result (batch 10 of 10, per X-2213)

C (implementer), 2026-11-12. Running count entering this batch, per X-2233: 5 O out of 44 (KI-110 excluded per X-2231).

**Not done:** no code, asset, engine, build, PIE or test work. No KNOWN_ISSUES status changes and no commits.

## BN-46..50

| Task | KI | Row | Evidence checked | Manual class | Offline follow-up? |
|---|---|---|---|---|---|
| BN-46 | KI-166 | `KNOWN_ISSUES.md:340`: `profile_dump.py:28`, `card_table.py:14`, `validate_baked_cards.py:15` and `plugin_dependencies.py:18,22` do not catch malformed JSON with a diagnostic naming the file | Pure-Python tools. BM-16..20 characterized `profile_dump` (exits 0 on a wrong shape) and `card_table` (partial output, then a crash) in real subprocess runs | **O** | **Yes:** a JSON-load wrapper that names the file and exits nonzero, plus temp-file unit tests (lead approval; it changes tool behaviour) |
| BN-47 | KI-167 | `:341`: local report tools can expose absolute input paths or echo source lines (7 tools cited). The action is "Review/redact … before sharing" | Pure-Python. An opt-in `--redact` mode, or repo-relative paths, is offline-implementable and testable without an engine | **O** (tool hardening) + L (the current procedure is a manual review) | **Yes:** optional repo-relative or redacted output, plus unit tests (lead approval). Note: the row's sharing procedure stays valid in the meantime |
| BN-48 | KI-174 | `:348`: the leash returns from `Tick`, but the absolute `ComboPauseUntil` deadline keeps running. "Intended timing is unspecified." The action is a leash-during-pause test plus the lead's intent | BM-36..40 re-verified the current lines (`:542, 897, 1100`) and pinned them statically. The proposed test is a runtime test (engine), and the intent is the lead's call | **E** (runtime test) + D (lead intent) | No: the static pin already exists; the next step needs engine work or a decision |
| BN-49 | KI-176 | `:350`: the parry half-refund is uncapped if the max-stamina read fails. "Add an actual-path fixture only when the pack attribute can be made to fail … No production change without that red" | The row explicitly forbids a change without an engine-side red, and no injectable fixture exists | **E** (fixture needs pack/engine) + L | No |
| BN-50 | KI-181 | `:355`: a subnormal weight times a subnormal factor can underflow to a zero score; no authored or gameplay reachability. The action is to keep it out of profiles and define semantics before altering the math | BM-31..35 pinned the double-to-float narrowing point. Changing it needs a design decision first | **L** (accepted boundary) + D (semantics) | No |

**Batch 10 result:** 2 new O (KI-166, KI-167).

## Cumulative lane BN result (BN-01..50)

**BN-01:** the 49 candidate IDs were reconstructed independently and match the BM table order exactly.

**Final manual classes for the 49 heuristic-O candidates.** These include the lead's hotfixes: KI-067 changed to O, and KI-110 changed to L.

| Result | Count | KIs |
|---|---|---|
| **True O** (a concrete offline follow-up exists) | **7** | KI-026 (retire the stale smoke driver), KI-067 (the G2-11 A4 selection weight), KI-163, KI-164, KI-165, KI-166, KI-167 (Python tool hardening) |
| **Not O** (E, D or L, or partly resolved) | **42** | all the others. Dominant gates: PIE or playtest, asset or art work (art is parked), owner scope or perf decisions, and accepted limits with procedures |

**So the BM-46 keyword heuristic over-counted O by 42 of 49 (86%).** Most misses were rows whose engine, owner or art gates are implied rather than spelled out.

**Follow-ups, all needing lead approval, none implemented:**
- **5 Python tool fixes:** KI-163..167. Engine-free, and testable in `Scripts/Tools`.
- **1 driver retirement:** KI-026.
- **1 gameplay source change:** KI-067. It needs a later hand test.

**Lead corrections during the lane:**
- X-2217: KI-004 wording.
- X-2219: KI-009, the Greystone route is opt-in.
- X-2221: KI-026 references.
- KI-067 changed to O.
- X-2231: KI-110 changed to L.

All are reflected in the batch files.

**Batch files:** `BN_01_05`, `BN_06_10`, `BN_11_15`, `BN_16_20`, `BN_21_25`, `BN_26_30`, `BN_31_35`, `BN_36_40`, `BN_41_45` (`*_KI_MANUAL_CHECK.md`) and this file.

**Checks actually performed:**
- KNOWN_ISSUES row reads.
- Targeted greps of config, source and scripts. The only source re-reads were KI-110 and the KI-004/005 config lines.
- File-existence checks.

**Not performed:** any code, asset, engine, build, PIE or test run; any KI status change; any commit or push.
