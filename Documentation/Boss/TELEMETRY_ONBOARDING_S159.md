# Telemetry onboarding example (S159)

This example follows `parry_stamina` from native emission to one retained run. It demonstrates how the source token, the two glossary indexes, the validator schema, the expected sheet, and the raw log connect. A format-valid event is still only one input to evaluating the scenario.

1. **Emitter:** `URPGPlayerParry` emits `[FrameworkProof] parry_stamina before=... after=... parried=...` on the refusal/rollback paths and after the resolved cost (`RPGPlayerParry.cpp:86,91,175`).
2. **Schema:** `Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py:202` accepts exactly the `before`, `after`, and boolean `parried` fields in that order.
3. **Semantic index:** `Documentation/Boss/LOG_TOKENS.md:71` summarizes the token fields as `before, after, parried` and explains the intended payload meaning.
4. **Emitter index:** `Documentation/Boss/LOG_TOKENS.md:170` links the schema line to all three literal emission sites; the source-only emitter listing also records `RPGPlayerParry.cpp` at line 374.
5. **Expected sheet:** `Docs/BossCombatReview/Execution/Codex/Proofs/PARRY_STAMINA_EXPECTED.md:17-18` describes the bounded live measurements and says a paid whiff (`parried=0`) is not a refusal or rollback. It separately marks low-stamina refusal as not yet live-proven.
6. **Retained log:** `Docs/BossCombatReview/Execution/Claude/B_PARRY_STAMINA/pie_stamina_overlay_run1/editor_raw.log:1771` records `before=100 after=80 parried=0`; line 2155 records `before=80 after=70 parried=1`.

## Check the links mechanically

`Scripts/Tools/check_validator_tokens.py:110-132` compares literal source emissions with the validator schema and both token tables in `LOG_TOKENS.md`; it is an index/schema consistency check, not a behavioral grader. The log values above agree with the expected sheet's cost-20 example, but this one token does not establish the entire setup, timing, overlay state, or the unexercised low-stamina refusal branch.

## Source references

`RPGPlayerParry.cpp:86,91,175`; `Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py:202`; `LOG_TOKENS.md:71,170,374`; `Scripts/Tools/check_validator_tokens.py:110-132`; `PARRY_STAMINA_EXPECTED.md:17-18`; `pie_stamina_overlay_run1/editor_raw.log:1771,2155`.
