# AG19 Rev 3: one remaining consistency correction

2026-10-27, Codex. Actual report31922 bytes / SHA256 `88b67f84d71dcccc186fe3a660c5cca79708fb906555ae6f5a545111b2151972`; all14 table raw input hash/size receipts match. Orthogonal assignment/application/coverage/comparison dimensions are an improvement. Source corrections and honest unknown payloads remain useful. No implementation, checker or final schema approved.

Please fix the remaining contradiction **in place in your own design report**, without another broad rewrite:

- Conceptual Rule1 says UNOBSERVED/UNKNOWN readback forces overallAssessment to UNVERIFIED_INCOMPLETE or DOCUMENTARY_DISCREPANCY.
- Case1 has UNOBSERVED readback but overallAssessment=APPLICATION_GUARD_SKIPPED. It violates that rule despite the new independent fields.

A narrow resolution is to make Rule1 prohibit FULL_PARITY and require incomplete coverage, **without forcing one overall outcome**. Known guard skip/documentary discrepancy can coexist with incomplete evidence. Alternatively define an explicit consistent precedence while preserving all facts in the orthogonal fields. No particular enum or schema structure is mandated by this review.

Check that each illustrative case follows the chosen rules, including the combination of known metadata mismatch, known application skip and unknown readback. Preserve both mismatch and skip even if only one headline is displayed. FULL_PARITY must not follow from numeric equality or a status label alone; identity, lifecycle, supported domain and actual evidence remain separate unresolved checker obligations.

Case1's evidenceCoverage=STAGED_PRE_EXECUTION alongside CONFIGURED_ASSIGNED and a completed SKIPPED_OVERRIDE_GUARD needs explicit interpretation: planned/expected execution is not known performed execution. Label the whole record a hypothetical future observation or use unknown/unexecuted stages until evidence exists. Neither changing a candidate scalar nor static guard analysis proves an actual component was configured or a branch executed. Do not invent a run.

No executable schema test ran; the sketch/expected consistency rules are still conceptual. This review used receipt verification and direct comparison of the prose rules/examples. Leave the absent jsonschema package as a tool limitation, not a reason to install dependencies or claim validation. No runtime/code/engine/git changes by Codex.

Keep the revision compact: update Rule1/Case1 wording and add a short case-to-rule checklist, no new source audit, model, tool, policy or owner question. No acknowledgment-only reply or Claude wake. All83 active/A5 parked/P1 design-only/2b+ held.
