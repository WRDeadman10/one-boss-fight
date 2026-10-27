import re

D = r"C:\UnrealProject\OneBossFight\Documentation"


def lf(b):
    return len(re.findall(rb"(?<!\r)\n", b))


# 1. TEST_PLAN BUILD-17
p = D + r"\TEST_PLAN.md"
b = open(p, "rb").read()
n0 = lf(b)
assert b.endswith(b"\r\n")
row = ("| BUILD-17 | DD-8 package 01: typed phase flow policy (Codex X-253 to X-254; NEW `Player/RPGBossPhaseFlowAdapters.h/.cpp`, `Tests/RPGBossPhaseFlowAdaptersTests.cpp`; EDITED only `Player/RPGEncounterBinding.h/.cpp`, 21 added lines, a reflected 6-field struct, one Data Asset field, one config copy, one shared validator call) | "
       "Five sources at the Codex-accepted hashes (adapter h 82c3eb4d...d2f5, cpp 166b05c9...b445b4, tests 2d75769f...1eee, Binding h 6e2f3ae0...609d, Binding cpp fafabe7b...6650; preimages dc43f3b8... and 247ef9c4... preserved), no change after acceptance. "
       "Editor build, Rebuild.ps1 command shape run directly: exit 0, 12 s. UHT ran: raw lines `Parsing headers for OneBossFightEditor`, `Running Internal UnrealHeaderTool`, `Total of 3 written`, `Reflection code generated for OneBossFightEditor in 1.5160783 seconds`; then 19 compile and link actions. "
       "Build diagnostics, exactly: 0 `warning C` lines, 0 error lines, 3 UBT `Warning:` lines (the UnrealClaude plugin's Niagara dependency twice, Visual Studio compiler not a preferred version). DLL e3addf3e...ca1584fa2 (build log sha256 a93b4c10...cca2). "
       "Focused `OneBossFight.Binding.PhaseFlow`: 6 found, 6 Success with six distinct paths (Assign, Authoring, Compile, Isolation, Rejections, Validation), exit 0, 21 s, no ensure, fatal, error-severity or unsupported-precondition line; the begun-component guard ran with a real `DispatchBeginPlay` on a plain actor with the three soft pointers cleared (log sha256 edb93234...ceab9). "
       "Full `OneBossFight` (run only because the focused run was clean): 81 found, 81 completed, 81 Success, 81 distinct, exit 0, 24 s (log sha256 0a6bbf56...61ee); the 75 paths of the DD7 full run are all present (0 missing), the only new paths are the six PhaseFlow tests; the families that depend on the changed shared compiler remain: 35 Binding paths (6 EncounterPolicy, 6 Preflight, 6 StaggerPolicy, 5 Stats adapters, 5 Phase adapters, 6 PhaseFlow, the draft world isolation). "
       "Automation diagnostics, exactly: 0 Error-severity lines, 0 ensures or fatals, 60 Warning-severity lines identical to the DD7 run after masking only per-run epoch GUIDs and the trace-server sponsor PID; 7 of those Warning lines contain the text 'error' and are the same non-failure lines as before (trace-server `Access is denied, Error: 0x5`, six `LoadErrors` lines about a dependent package of a demo material), none new. "
       "After: Source manifest identical before and after the build (165 files); against the preimage manifest exactly 3 added and 2 changed files; 22 of 24 dependency pins unchanged (the other two are the authorized edits); exe 5495fb88... NOT rebuilt; HEAD 04037c91; 0 pack changes; no engine process left. Evidence `Docs/BossCombatReview/Execution/Claude/DD8/build_2026-10-27/`. "
       "No failure in this package. NOT proved: a serialized asset value or anything in the Details panel (reflection and defaults only), a production compile with a real skeleton (only its early rejection), a real phase transition, roar, montage, immunity or leap lock, that any ability matches the prefix or that the leap tag is registered, any wiring, the 40-row gate on this binary, Shipping, the non-editor target. | "
       "PASS typed phase flow policy (6 fields), shared validation, compiler copy and typed assignment, headless; flow authoring fields only, not the phase presentation dependencies |")
b2 = b + row.encode("utf-8") + b"\r\n"
assert lf(b2) == n0
open(p, "wb").write(b2)
print("TEST_PLAN BUILD-17 appended")

# 2. TASKS.md clause
p = D + r"\TASKS.md"
b = open(p, "rb").read()
n0 = lf(b)
old = b"scalar policy only, not the stagger clip, effect and mode profile, not a serialized or Details proof, not wired, not in the gate)"
new = (b"scalar policy only, not the stagger clip, effect and mode profile, not a serialized or Details proof, not wired, not in the gate; "
       b"DD-8 typed phase flow policy (reflected 6-field FRPGPhaseFlowConfig on the boss definition, shared validator, typed assignment, unwired fragment): built with UHT, focused 6/6 and full automation 81/81 on 2026-10-27, no failure (TEST_PLAN BUILD-17), flow authoring fields only, not the phase presentation dependencies, not an ability or tag resolution, not a serialized or Details proof, not wired, not in the gate)")
assert b.count(old) == 1, b.count(old)
b = b.replace(old, new)
assert lf(b) == n0
open(p, "wb").write(b)
print("TASKS clause extended")

# 3. DECISIONS.md section before ## Open
p = D + r"\DECISIONS.md"
b = open(p, "rb").read()
n0 = lf(b)
marker = b"\r\n## Open\r\n"
assert b.count(marker) == 1
text = ("## DD-8 typed phase flow policy (2026-10-27, Codex lead X-253 to X-254, accepted)\r\n\r\n"
        "- The phase flow authoring fields are a typed record: reflected `FRPGPhaseFlowConfig` with six fields named exactly as the native `URPGBossPhases` fields (`TransitionSeconds` 1.8, `bUseRoarClip` true, `bPausePostureInTransition` true, `bLockLeapUntilPhaseTwo` true, `AttackAbilityPrefix` \"GA_GS_Boss_\", `LeapAbilityTag` \"Ability.Melee.LeapAttack\"), exposed as `PhaseFlow` on `URPGBossDefinition` and copied into the immutable `FRPGParticipantConfig` by the one shared `CompileParticipantImpl`. The defaults are authoring defaults of the new field, never a fallback: an invalid value fails the compile by name and clears the previous output.\r\n"
        "- One typed validator serves the compiler and the assignment: the duration finite, then not negative (zero is valid, no invented editor floor such as the native ClampMin 0.2 and no ceiling), the prefix neither empty nor only whitespace, the tag not None. Authored values are never trimmed, normalized or replaced and no gameplay tag is requested or registered. The prefix and the tag state an explicit identity only; that an ability matches the prefix or that the tag is registered is an unresolved integration check before activation, and a zero duration is structurally valid, not an approval of zero-tell combat.\r\n"
        "- `ConfigurePhaseFlow` follows the shared lifecycle rule of the typed adapters and assigns exactly the six fields after the whole record is validated; it never touches the selected phase record owned by the phase adapter, the fireball fields, the soft asset references, the loaded objects or any runtime state. The plan is an UNWIRED fragment with the legacy instance name and is not combinable with the phase adapter's plan; a later combined Phases plan must validate the selected phase, this record and the dependency record in full and write once. The roar, transition montage and immunity dependencies are still open for a later reviewed package (`KNOWN_ISSUES.md` KI-114, `TEST_PLAN.md` BUILD-17).\r\n\r\n")
b = b.replace(marker, b"\r\n" + text.encode("utf-8") + marker.lstrip(b"\r\n"), 1)
assert lf(b) == n0
open(p, "wb").write(b)
print("DECISIONS section added")

# 4. KNOWN_ISSUES.md KI-114
p = D + r"\KNOWN_ISSUES.md"
b = open(p, "rb").read()
n0 = lf(b)
assert b.endswith(b"\r\n")
row = ("| KI-114 | Test | The typed phase flow policy (`FRPGPhaseFlowConfig`, `PhaseFlow` on `URPGBossDefinition`, `RPGBossPhaseFlowAdapters`, `TEST_PLAN.md` BUILD-17) has limits its green tests do not close: (1) it covers the six flow fields only: the roar clip, the transition montage and the immunity effect (soft asset references), the fireball fields and the selected phase record are not part of this typed record, so the phase cluster is not complete; (2) the Data Asset exposure is proven by reflection only, not by a serialized asset or the Details panel; (3) the defaults are authoring defaults that match the native declarations, not evidence of a live or serialized value; (4) `AttackAbilityPrefix` and `LeapAbilityTag` are accepted as explicit identity only: a non-empty prefix does not prove that any ability matches it, an unregistered or whitespace-padded value is accepted unchanged, and the tag is never registered, so a later capability resolution has to check them before activation; (5) a zero or very short transition duration is structurally valid and is not an approval of the combat feel, and no bound is derived from the roar or montage length; (6) a real phase transition, roar, posture pause or leap lock with these values was never run, and the production compile is exercised only through its early rejection; (7) the flow plan is an unwired fragment that is not in the DD5 preflight and cannot be combined with the phase adapter's plan (two plans for one class are refused) | A reviewed dependency profile for the roar, montage and immunity references, a combined one-component Phases plan, capability resolution for the prefix and the tag, and a serialized definition checked in the Details panel, as separate packages | Open (limits recorded, no failure observed) |\r\n")
b2 = b + row.encode("utf-8")
assert lf(b2) == n0
open(p, "wb").write(b2)
print("KNOWN_ISSUES KI-114 appended")
