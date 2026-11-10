# C-1253a Sevarog transient authoring dry-run

**Status: PASS, all validators passed; 0 assets saved.** Run under C-1155 locks on 2026-11-10. The tool constructs all five allowlisted move cards, the F5 profile, its four candidate rows and S4-to-S5 combo graph, and the draft definition as transient UE objects. It assigns the same authored values as the guarded creation path, then invokes the Editor C++ CompileResolved card validator for every card and ResolveProfile for the profile. It confirms every target asset path remains absent after validation.

## Changes

- URPGBossFrameworkProfile.Cards and .ComboNodes now expose BlueprintReadWrite, matching the other script-written reflected properties.
- The author script uses typed unreal.Array values for combo nodes, combo edges and profile candidates. UE 5.5 does not convert plain Python lists of reflected structs in these properties.
- Replaced the incomplete property-only preflight with --dry-run. It makes the full candidate/profile/definition objects via unreal.new_object, runs both production C++ validators, prints each verdict and returns without calling AssetTools or any save API.
- Added Python-friendly C++ report wrappers around the existing validators. UE 5.5 Python projected the bool/out-array call ambiguously (an empty diagnostics Array for successes and None on a false result); wrappers now return explicit PASS or FAIL|diagnostics strings.
- Exact clip readbacks revealed that contact-sheet end times are rounded and the profile requires a 0.03 s blend tail. The tool clamps a marked recovery end to resolved clip length minus BlendOutSeconds only when the correction is within the 15 Hz sampling interval (0.0667 s); it logs every clamp. Applied recovery ends: S1 1.103333 s, S2 1.103333 s, S3 1.670000 s, S4 1.236667 s. This preserves the contact marking as the visual source while satisfying the resolved profile tail constraint.

## Validator results

- All five validate_move_card_report calls: PASS, diagnostics empty.
- validate_framework_profile_report: PASS, diagnostics empty.
- C++ punish checks:
  - S1: recovery 0.703333 s, light startup 0.350337 s, travel 0.050000 s, margin 0.302996 s, required 0.300000 s, ok=1.
  - S2: same values as S1, ok=1.
  - S3: recovery 1.003000 s, light startup 0.350337 s, travel 0.050000 s, margin 0.602663 s, required 0.300000 s, ok=1.
  - S4 defensive counterplay: recovery after movement 0.436667 s, counterplay end distance 120 cm, counterplay margin 0.0863297 s, ok=1. The negative attack-punish margin is informational for this defensive card; C++ validation uses the defensive counterplay rule.
- Editor Development build exit 0; full Automation RunTests OneBossFight 498/498, 0 failed, DD27j hash cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec.
- Offline author contract 11/11, Python syntax pass. Target asset paths absent; no Sevarog content assets saved. Both locks released, project Editor closed.

## Evidence

Runner: Scripts/Editor/run_c1253a_locked_validation.ps1.

Logs and status: Docs/BossCombatReview/Execution/Codex/C1253A_TRANSIENT_DRYRUN/ (build.log, dry-run.log, suite.log, status.txt). Earlier failed dry-run logs are retained as dry-run-backup-*.log; they exposed the struct-array conversion and timeline/profile-tail constraints corrected above.

This proves the current transient values satisfy the validators and build/test gate. It does not author package assets or claim PIE/gameplay proof.
