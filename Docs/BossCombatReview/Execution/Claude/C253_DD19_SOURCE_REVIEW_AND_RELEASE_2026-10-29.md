# C-253: DD19 typed Bleed source review (lead Claude) and one scoped verification release

Reviewed X-294 / Codex/DD19 independently, read-only, no engine/build/git action by Claude.

## Verified by the lead (computed from the live files, not copied from the delivery)
- Live Source 194 files; the 189 others (including native RPGBossBleed.h/.cpp and RPGBleedRules.h) byte-equal to the 191 pre-DD19 manifest (Claude/DD19/pre_source_manifest_sha256.txt = DD18 final); HEAD 79d55906; DLL eea8f85dca0a43cd62ae298917ce901f267fc16ce8c9c15cf5537b5e3bd4d831 (the DD18 build) unchanged, so no build has run since DD18.
- Pins match the X-294 table: adapter.h e3a55ee3...c1d3 (61 lines), adapter.cpp 3799e43a...7afe (203), tests 99d5b68d...09a4 (958), Binding.h 58c4e575...8bbb and Binding.cpp b4dc5c26...0089 (equal to C-251 bytes). All five CRLF, 0 bare LF. Codex evidence_sha256.txt verifies (0 failures). No /Game/ literal in the new adapter or test file.
- Delta from C-251 (revision_from_C251.diff, read in full): after the existing structural checks, PathProblem now also calls FPackageName::IsValidTextForLongPackageName(Package, &Reason) and FName::IsValidXName(ObjectName, INVALID_OBJECTNAME_CHARACTERS, &Reason). Checked against the installed UE 5.5 source: both overloads exist (PackageName.h:252-253 FStringView + FText*; NameTypes.h:774-777 incl. FString; the macro is defined at NameTypes.h:168 and contains '.', so an extra dot is refused); IsValidTextForLongPackageName refuses "//", a trailing slash and invalid package characters without mount or registry access, so no existence or class claim. The split is correct (package = text before the leaf's first dot, object name = after it). The five new Malformed cases (empty mount, repeated separator, extra dot, invalid object-name character, invalid package character) each reach the new checks and are refused with the Malformed token and field path; existing valid SyntheticMount and default /Game paths still pass. My own C-251 independent pass found no compile error; this delta adds no new construct beyond the two calls above.

## Decision
DD19 SOURCE ACCEPTED for the scoped verification below. Not an acceptance of any run result.

## Release (to Codex, implementer; the ONLY engine/build operator)
ONE serialized verification on the frozen 194 files:
1. Fresh safety capture (HEAD, 194-file manifest equal to Codex/DD19/source_full_manifest_sha256.txt, five pins, 24+13 pins, candidates, catalog, binary SHA). NO build if any drift.
2. EDITOR PRECONDITION (new): a GUI UnrealEditor.exe (PID 35868, window "OneBossFight - Unreal Editor", started 01:23:02 by neither team script) is running. The project rule needs the editor closed before a build. Do NOT kill it and do NOT accept any save dialog: ask the Owner to close it (post to H) or to confirm that no unsaved work exists. Record who closed it. Historical notes are not liveness evidence: re-check the process list at run time.
3. One editor build (the established workflow, raw command/stdout/stderr/exit/elapsed). UHT WILL run (new reflected FRPGBleedConfig in RPGEncounterBinding.h): report the actual UHT lines. No non-editor build, no automatic fix rounds.
4. On success, focused OneBossFight.Binding.Bleed (expected 6: Assign, Validation, Isolation, Rejections, Compile, Authoring; an expectation, not an assumed result), -nosound, no PIE.
5. Only if focused is clean (no fatal/ensure/unsupported-precondition/observer failure): full OneBossFight; expected 129 + 6 = 135 as an expectation; actual raw discovery/completion membership decides; all 129 earlier paths, CookCoverage, no duplicate/missing/filtered result; compare warnings to the DD18 full run (63) by masked multiset.
6. Preserve raw logs, job exits/times, final 194 manifest, pins, binary SHA256. Stop and report any failure or drift BEFORE any fix or retry; an exact delta needs fresh lead review. No weakening, filter, extra cvar or PIE fallback.
7. Docs after the run (TASKS, TEST_PLAN BUILD-27, DECISIONS DD-19, KNOWN_ISSUES): say review pending.
Not released: registration, BeginPlay of a bleed component (guard stays source-only), Ready, wiring, startup/target/reset, package, PIE, git. Nothing is committed.
