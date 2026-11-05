# W-A011: Presentation Rules Test Mutations Second Review

**Date:** 2026-11-06  
**Author:** Antigravity (Lane A)  
**Status:** Complete  
**Scope:** Second-reviewer verification of presentation rules test mutations in [`RPGPresentationRulesTests.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGPresentationRulesTests.cpp), verifying that every mutation asserts a real invariant (no tautologies) and respects case insensitivity.  
**Sources:**
- Test Suite: [`Source/OneBossFight/Tests/RPGPresentationRulesTests.cpp:10-36`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGPresentationRulesTests.cpp#L10-L36)
- Presentation Rules: [`Source/OneBossFight/Presentation/RPGPresentationRules.h:18-35`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Presentation/RPGPresentationRules.h#L18-L35)
- Lead Hotfix Directive: [`Documentation/TEAM_MAILBOX.md:23985`](file:///c:/UnrealProject/OneBossFight/Documentation/TEAM_MAILBOX.md#L23985) (`[C-933]`)

---

## 1. Executive Summary

In Queue W task `W-C017`, Codex implemented character-by-character mutation loops and path variance tests for `MatchesOptionalTrackerMontagePath`. During initial BUILD-234 evaluation, a mutation asserted that case-only path variance should fail matching, which failed automation because Unreal Engine's `FString::operator==` and asset registry paths are case-insensitive.

Lead Claude corrected this assertion in `RPGPresentationRulesTests.cpp:30-33` ([`[C-933]`](file:///c:/UnrealProject/OneBossFight/Documentation/TEAM_MAILBOX.md#L23985)). This audit verifies all assertions in the current suite.

---

## 2. Itemized Mutation Analysis

| Line Range | Test Code / Mutation | Assertion Type | Evaluates Real Invariant? | Case-Insensitivity Compliance |
|---|---|---|:---:|:---:|
| [`RPGPresentationRulesTests.cpp:13-16`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGPresentationRulesTests.cpp#L13-L16) | `IsTier2PreviewEnabledForBuild(true, 1)` vs `(true, 0)` vs `(false, 1)` | `TestTrue` / `TestFalse` | **YES**. Proves Development gating: non-zero CVar enables preview in Dev; non-Dev builds unconditionally ignore CVar. | N/A (Boolean logic) |
| [`RPGPresentationRulesTests.cpp:19`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGPresentationRulesTests.cpp#L19) | `MatchesOptionalTrackerMontagePath(Path, Path)` | `TestTrue` | **YES**. Verifies identity match on canonical A2 path (`/Game/OneBossFight/Boss01/Animations/AM_Boss01_A2.AM_Boss01_A2`). | Compliant |
| [`RPGPresentationRulesTests.cpp:20`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGPresentationRulesTests.cpp#L20) | `MatchesOptionalTrackerMontagePath(Path, "/Game/" + "Other/Other.Other")` | `TestFalse` | **YES**. Proves disparate paths fail to match; dynamic concatenation prevents CookCoverage false positives. | Compliant |
| [`RPGPresentationRulesTests.cpp:21-22`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGPresentationRulesTests.cpp#L21-L22) | Empty optional path / empty observed path | `TestFalse` | **YES**. Enforces fail-closed behavior on missing or uninitialized strings. | Compliant |
| [`RPGPresentationRulesTests.cpp:23-29`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGPresentationRulesTests.cpp#L23-L29) | Single-character mutation loop (`Index = 0 .. Path.Len()-1`) | `TestFalse` | **YES**. Proves that mutating any single character to 'X'/'Y' causes match rejection. | Compliant |
| [`RPGPresentationRulesTests.cpp:31-32`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGPresentationRulesTests.cpp#L31-L32) | `MatchesOptionalTrackerMontagePath(Path, Path.ToLower())` | `TestTrue` | **YES**. Enforces the engine rule: asset paths and `FString::operator==` are case-insensitive. | **STRICTLY ENFORCED** |
| [`RPGPresentationRulesTests.cpp:33-34`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGPresentationRulesTests.cpp#L33-L34) | `MatchesOptionalTrackerMontagePath(Path, Path + "_Extra")` | `TestFalse` | **YES**. Proves prefix extensions or trailing substrings fail to match. | Compliant |

---

## 3. Conclusion

Every test mutation asserts a non-tautological property of the presentation matcher. The suite actively defends case insensitivity and string purity, verified green in the 478/478 suite ([`B_C932_QW2/suite.log`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/B_C932_QW2/suite.log)).
