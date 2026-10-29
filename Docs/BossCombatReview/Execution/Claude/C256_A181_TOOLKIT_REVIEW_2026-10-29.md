# C-256: A-181 frozen toolkit revision, lead review (Claude), 2026-10-29

Read-only, offline. No engine, no asset, no git. The lead ran the AG unit tests themself (python -B, no bytecode written).

## Verified
- Receipts: AuthoringToolkit/evidence_sha256.txt 19/19 and BuildAuthoringHelper/evidence_sha256.txt 13/13 verify (0 failures). All 32 + 18 files are pure CRLF (0 bare LF/CR). A-180 bytes preserved in original_A180/ in both folders (A-181 current files differ from them, as intended). Real A180-era hashes differ from the pins quoted in A-180 (authoring_core 0378285c, draft c84408d0, inspect 1c00aadf, test 2a0fd758 in original_A180) and match what Codex found in X-288: noted, not a new defect.
- Unit tests: `python -B test_authoring_core.py` -> Ran 59 tests, OK, exit 0 (matches A-181).
- No Bleed/FRPGBleedConfig in any code file (one README mention only): DD19 scope kept out, as ordered.
- Domain table matches the accepted native validators I re-read: PhaseFlow TransitionSeconds finite and >= 0; Fireball cooldown pair and ranges finite, >= 0, ordered; stagger/stats/phases as stated in A-181 and as in RPGBossStaggerPolicyAdapters/RPGBossStatsAdapters.
- Name mapping checked against the installed UE 5.5 PyGenUtil.cpp (PythonizePropertyName/PythonizeName) and CamelCaseBreakIterator.cpp: all 64 mapped field names (10 structs) come out right, including bool prefix stripping and SourceSHA256 -> source_sha256 (digits stay with the preceding upper-case run in the engine's break rule).

## Defects found (A-181 is returned, bounded)
1. FLOAT32 (blocking; X-291 required it): every readback compares Python float64 with `canonical_dict != expected_native_dict` (draft_boss_profiles.py:572; phases/fields the same). An Unreal float property stores float32, so a value such as 0.03, 0.35 or 0.6 reads back as 0.029999999552965164 and the exact comparison would FAIL on a correct write, while the offline fake stores float64 and cannot show it. Required: compare the expected value after a float32 round trip (struct 'f'), refuse a requested value that is finite in float64 but overflows float32, make the fake store float32 so a regression test fails on the old comparison, and state in README/tests that offline float64 checks do NOT certify native float32 conversion or input-mode parity (the qualification Codex asked for is absent: grep float32 finds nothing).
2. PROPERTY-NAME RULE: the engine strips a leading `b` + upper-case and `In` + upper-case from ANY property type (PyGenUtil.cpp:1833-1855, repeated); pythonize_property_name does it only for booleans. No current field is affected, but the docstring claims it mirrors the engine. Required: implement the engine rule (type-independent, repeated, `self` -> `_self`) or narrow the claim, plus tests with a non-bool `bX...` and an `InX...` name; add a pinned test for SourceSHA256 -> source_sha256 and say the regex only approximates the engine's break iterator beyond the 64 checked names.
3. READBACK FALLBACK: extract_canonical_primitives falls back to the native CamelCase attribute/dict key when the generated Python name is missing (authoring_core.py:281, 287). A real wrapper exposes only generated names, so the fallback can only hide default-loss in a fake. Required: read ONLY the generated Python names for wrappers; keep a dict path only for struct-init dictionaries that already use generated keys; add a test that a CamelCase-only fake fails readback.

## Not required now
Nothing about assets, engine, Bleed, git. The toolkit stays offline.

## Next
Deliver A-182 (frozen, identified revision; keep A-181 under original_A181/ in both folders; new test log and receipts). A01 stays unreleased until A-181/A-182 is accepted.
