# Queue W W-C011–W-C014 — dead code, warnings, and asset custody

Date: 2026-11-06. Source changes are authored but await Claude's native build/automation run. No Unreal, Editor, packaging, commit, push, or content-asset change was made by Codex.

## W-C011 — safe dead-code candidates

Removed two private helpers whose workspace scan showed only declaration and definition: `RPGPackTrace::FTarget::RefreshPrevious` and `URPGBuildSelect::Toggle`. The retained input path calls `NoteBKeyDown`; the removed wrapper had no source caller. Two public native APIs, `FRPGBossPreparationRegistry::GetQuarantineDiagnostics` and `URPGCombatContextSubsystem::ResolveEncounter`, remain because the older audit explicitly says external module/content use has not been cleared. A test guards both removals and their public API retention. Lead build remains required.

## W-C012 — BUILD-232 deprecation warnings

Reviewed `Docs/BossCombatReview/Execution/Claude/B_C928_TESTS/build.log`. The only warning match is `Visual Studio 2022 compiler is not a preferred version`; there are no project-owned C++ deprecation warnings to fix in that retained build log. No speculative edits made.

## W-C013 — 14 proof-asset candidates

Reviewed `V_A039_UNREFERENCED_ASSET_CLEANUP_LIST.md`: it lists 14 packages (8 maps and 6 data assets) with reported zero referencers and explicitly says WAITING ON OWNER AUTHORIZATION. The assets remain untouched. V-A067's broader folder proposal is not new deletion authorization.

## W-C014 — regression checks

`Scripts/Tools/test_w011_dead_code_safety.py` passes 2/2: the private candidates are absent and both public APIs remain declared/defined. This checks source/API shape; it does not replace the Lead's C++ build/native suite. No runtime behavior was intentionally changed by removing the unreferenced wrappers.

## Status and next

W-C011 is partial until Lead compile and external-use disposition for public APIs. W-C012–W-C014 are complete within the evidence boundary. Continue W-C016–W-C020 without waiting.
