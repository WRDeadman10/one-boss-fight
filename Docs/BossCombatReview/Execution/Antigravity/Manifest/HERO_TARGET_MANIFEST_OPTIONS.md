# Technical Options & Ground Truth Analysis: Parity Manifest Design for Target-Only Participants (Option A vs. Option B)

**Author:** Antigravity (Party Code A) - Senior C++ Implementer & Unreal Engine Specialist  
**Task Order:** [C-340] / Order A-224 (Target-Only Manifest Investigation)  
**Date:** 2026-10-29  
**Source Baseline:** Live Working Tree (`HEAD: 605c2dd8`, Source 217 files, Content 11755 files)  
**Execution Boundary:** **STRICTLY OFFLINE INVESTIGATION**. Zero Unreal Engine processes launched; zero edits to `Source/`, `Content/`, or `Config/`; zero git commands executed; pure CRLF line endings.

---

## Executive Summary & Core Architectural Problem

During the execution of **DD27j** (`[X-340]`, `[C-340]`), the production participant compiler (`RPGCombatHydration::CompileParticipant`) was executed against both saved draft assets:
1. **Saved Ember Warden Draft (`DA_Boss_EmberWarden_Draft`):** Successfully passed `CompileParticipant` (`stage=BossCompile ready=1 output=1`, 110 field rows verified, manifest hash `cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec` from `emit_fields_manifest.py`).
2. **Saved Player Hero Draft (`DA_Player_Hero_Draft`):** Failed compilation at Stage 2 (`stage=HeroCompile ready=0 output=0 fields=0`) with error:
   ```
   Error: field manifest required
   ```

Per Tech Lead Claude's directive in `[C-340]`, this document analyzes **Option A** (designing a minimal truthful manifest for the Hero target-only definition) and evaluates whether any candidate rows can be genuinely truthful under the project's data-driven hydration architecture.

---

## 1. Verbatim Ground Truth Citations (Opened Lines, 40+ Characters)

All line citations below are quoted verbatim from the working tree:

| Source File | Line | Verbatim Line Text (40+ Characters) | Architectural Role & Mechanism |
| :--- | :---: | :--- | :--- |
| `Source/OneBossFight/Player/RPGEncounterBinding.cpp` | **106** | `		if (F.FieldPath.IsEmpty() \|\| Fields.Contains(F.FieldPath) \|\| F.Type.IsEmpty()` | Validates each manifest row across 10 required fields and deduplicates `FieldPath`. |
| `Source/OneBossFight/Player/RPGEncounterBinding.cpp` | **115** | `	if (Fields.IsEmpty()) { Result.Fail(TEXT("field manifest required")); }` | Indiscriminate compile check: fails ANY participant whose `Fields` array is empty. |
| `Source/OneBossFight/Player/RPGEncounterBinding.cpp` | **120** | `	Value->Stats = D.Stats; Value->Phases = D.Phases; Value->Fields = D.Fields;` | Stores authored definition structs into compiled `FRPGParticipantConfig`. |
| `Source/OneBossFight/Player/RPGBossHydrationPreflight.cpp` | **347** | `			if (Config->Schema != 1 \|\| Config->BossId.IsNone() \|\| Config->PresentationId.IsNone() \|\| !IsSHA256Shape(Config->StableManifestHash) \|\| Config->Fields.IsEmpty()` | Preflight identity check: fails ANY participant whose compiled `Fields` array is empty. |
| `Source/OneBossFight/Player/RPGBossHydrationPreflight.cpp` | **402** | `				const TArray<FRPGComponentPlan> MemberPlans = MakeBossCorePlans(Request.SelectedPhaseId);` | Boss plans generated to check 110 required paths against manifest (BossCore ONLY). |
| `Source/OneBossFight/Player/RPGBossHydrationPreflight.cpp` | **425** | `			else if (Request.Role == ERPGPreflightRole::TargetOnly && !Request.SelectedPhaseId.IsNone())` | Rejects phase selection on TargetOnly participants (`SelectedPhaseId` must be `NAME_None`). |
| `Source/OneBossFight/Player/RPGBossHydrationPreflight.cpp` | **449** | `			if (Request.Role == ERPGPreflightRole::BossCore)` | Guard restricting component plan generation strictly to `BossCore` role. |
| `Source/OneBossFight/Player/RPGBossHydrationPreflight.cpp` | **451** | `				Participant.Plans = MakeBossCorePlans(Request.SelectedPhaseId);` | For `TargetOnly`, `Participant.Plans` and `ClassLeases` remain EMPTY (0 plans). |
| `Source/OneBossFight/Tests/RPGBossProductionPreflightTests.cpp` | **138** | `	FRPGParityField MakeProductionField(const FString& Path)` | Synthetic fixture factory used to fabricate manifest rows in existing production tests. |
| `Source/OneBossFight/Tests/RPGBossProductionPreflightTests.cpp` | **204** | `		for (const FString& Path : AllRequiredPaths(PhaseTwo))` | Fills BOTH boss AND player definitions with all 110 PhaseTwo paths in test fixture. |
| `Source/OneBossFight/Tests/RPGBossProductionPreflightTests.cpp` | **389** | `			FillDefinition(*PlayerDefinition, TEXT("ProductionPlayer"), TEXT("ProductionPlayerLook"), PlayerSkeleton, PlayerAnimationPaths());` | Harness fills player definition with synthetic PhaseTwo boss fields. |
| `Source/OneBossFight/Tests/RPGBossStatsAdaptersTests.cpp` | **130** | `IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGStatsAdaptersAssignTest, "OneBossFight.Binding.StatsAdapters.Assign",` | Verified automation test witness for Posture/Stats adapter assignment. |
| `AuthoringToolkit/examples/boss_draft_profiles.json` | **1887** | `      "asset_name": "DA_Player_Hero_Draft",` | Authored profile specification for the player hero target definition. |
| `AuthoringToolkit/examples/boss_draft_profiles.json` | **1895** | `        "MaxHealth": 800.0,` | Authored Player Hero MaxHealth scalar (float). |
| `AuthoringToolkit/examples/boss_draft_profiles.json` | **1896** | `        "MaxPosture": 60.0,` | Authored Player Hero MaxPosture scalar (float). |
| `AuthoringToolkit/examples/boss_draft_profiles.json` | **1897** | `        "PostureRegenDelay": 1.5,` | Authored Player Hero PostureRegenDelay scalar (float). |
| `AuthoringToolkit/examples/boss_draft_profiles.json` | **1898** | `        "PostureRegenRate": 25.0` | Authored Player Hero PostureRegenRate scalar (float). |

---

## 2. Technical Audit: How Target-Only Participants Are Handled in the Engine

Inspection of the C++ codebase reveals a structural asymmetry between `BossCore` and `TargetOnly` participants:

### 2.1 Preflight Component Plans Are Zero for TargetOnly:
In `Source/OneBossFight/Player/RPGBossHydrationPreflight.cpp:449-456`:
```cpp
if (Request.Role == ERPGPreflightRole::BossCore)
{
    Participant.Plans = MakeBossCorePlans(Request.SelectedPhaseId);
    for (const FRPGComponentPlan& ComponentPlan : Participant.Plans)
    {
        Participant.ClassLeases.Emplace(ComponentPlan.Class);
    }
}
```
- When `Request.Role == ERPGPreflightRole::TargetOnly`, **zero component plans are created** (`Participant.Plans.IsEmpty() == true`), and **zero component class leases are taken** (`Participant.ClassLeases.IsEmpty() == true`).
- Furthermore, the loop that verifies the 110 required manifest paths (`RPGBossHydrationPreflight.cpp:402-423`) is guarded strictly inside `if (bBossCore)`. **Preflight never checks for the presence of the 110 required paths on a `TargetOnly` participant.**

### 2.2 Player Pawns Are NOT Configured via Data Asset Adapters:
In `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:253-295`:
- When the player pawn (`BP_CombatPlayerCharacter`) is spawned, `URPGPlayerMovesSubsystem::Attach` attaches player-side components (`URPGCameraRig`, `URPGRiposteInput`, `URPGDodgeTiming`, `URPGSwingTracker`, `URPGHitIntake`, `URPGBuildLoadout`, `URPGBuildSelect`, `URPGFlaskHud`, `URPGIFrameMonitor`) via hardcoded C++ `NewObject` calls.
- **Not a single player component reads from `URPGBossDefinition` or `FRPGParticipantConfig`.** There is no `Configure` callback and no adapter for the player character.

### 2.3 Why `CompileParticipant` Failed in DD27j:
In `Source/OneBossFight/Player/RPGEncounterBinding.cpp:115`:
```cpp
if (Fields.IsEmpty()) { Result.Fail(TEXT("field manifest required")); }
```
`CompileParticipant` was written to validate `URPGBossDefinition` in isolation, before an encounter batch or participant role (`BossCore` vs `TargetOnly`) is known. It requires `!D.Fields.IsEmpty()` unconditionally. Because `DA_Player_Hero_Draft` was authored with `fields: []`, compilation failed immediately at line 115.

---

## 3. Concrete Design: Option A (Minimal Truthful Manifest for Hero Target)

If Option A is pursued (authoring a manifest for the Hero definition without altering compiler code), what rows can it contain?

### Candidate Set 1: Authored Player Stats (4 Minimal Rows)
In `Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/examples/boss_draft_profiles.json:1894-1899`, the Hero profile authors four specific, grounded scalar values in `stats`:
- `MaxHealth = 800.0`
- `MaxPosture = 60.0`
- `PostureRegenDelay = 1.5`
- `PostureRegenRate = 25.0`

These 4 fields can be formatted as compliant `FRPGParityField` rows:

```json
[
  {
    "FieldPath": "Stats.MaxHealth",
    "Value": "800.0",
    "Type": "float",
    "Units": "hp",
    "SourcePath": "Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/examples/boss_draft_profiles.json",
    "SourceSHA256": "ee04c8b7175642a4fdf27ccb430af6e35e15092254b36064d5b3a4a0a11a8ed4",
    "SourceSite": "/profiles/2/stats/MaxHealth",
    "Origin": "AuthoredAsset",
    "Precedence": "typed-record",
    "Destination": "FRPGParticipantStatsConfig::MaxHealth",
    "FirstRead": "RPGCombatHydration::CompileParticipant",
    "Witness": "AutomationTest:OneBossFight.Binding.StatsAdapters.Assign"
  },
  {
    "FieldPath": "Stats.MaxPosture",
    "Value": "60.0",
    "Type": "float",
    "Units": "hp",
    "SourcePath": "Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/examples/boss_draft_profiles.json",
    "SourceSHA256": "ee04c8b7175642a4fdf27ccb430af6e35e15092254b36064d5b3a4a0a11a8ed4",
    "SourceSite": "/profiles/2/stats/MaxPosture",
    "Origin": "AuthoredAsset",
    "Precedence": "typed-record",
    "Destination": "FRPGParticipantStatsConfig::MaxPosture",
    "FirstRead": "RPGCombatHydration::CompileParticipant",
    "Witness": "AutomationTest:OneBossFight.Binding.StatsAdapters.Assign"
  },
  {
    "FieldPath": "Stats.PostureRegenDelay",
    "Value": "1.5",
    "Type": "float",
    "Units": "seconds",
    "SourcePath": "Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/examples/boss_draft_profiles.json",
    "SourceSHA256": "ee04c8b7175642a4fdf27ccb430af6e35e15092254b36064d5b3a4a0a11a8ed4",
    "SourceSite": "/profiles/2/stats/PostureRegenDelay",
    "Origin": "AuthoredAsset",
    "Precedence": "typed-record",
    "Destination": "FRPGParticipantStatsConfig::PostureRegenDelay",
    "FirstRead": "RPGCombatHydration::CompileParticipant",
    "Witness": "AutomationTest:OneBossFight.Binding.StatsAdapters.Assign"
  },
  {
    "FieldPath": "Stats.PostureRegenRate",
    "Value": "25.0",
    "Type": "float",
    "Units": "hp/s",
    "SourcePath": "Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/examples/boss_draft_profiles.json",
    "SourceSHA256": "ee04c8b7175642a4fdf27ccb430af6e35e15092254b36064d5b3a4a0a11a8ed4",
    "SourceSite": "/profiles/2/stats/PostureRegenRate",
    "Origin": "AuthoredAsset",
    "Precedence": "typed-record",
    "Destination": "FRPGParticipantStatsConfig::PostureRegenRate",
    "FirstRead": "RPGCombatHydration::CompileParticipant",
    "Witness": "AutomationTest:OneBossFight.Binding.StatsAdapters.Assign"
  }
]
```

#### Why Candidate Set 1 Passes C++ Compiler Checks:
1. `FieldPath` strings are non-empty and unique (`RPGEncounterBinding.cpp:106, 113`).
2. `Type` is valid `"float"` (`:106`).
3. `SourcePath` is genuine working-tree file (`:107`).
4. `SourceSHA256` is genuine 64-hex SHA-256 (`:107`, `IsSHA256`).
5. `SourceSite` is truthful JSON pointer (`:107`).
6. `Origin`, `Precedence`, `Destination`, `FirstRead`, `Witness` are non-empty (`:108-109`).
7. `Fields.Num() == 4 > 0`, satisfying line 115 (`if (Fields.IsEmpty())`).
8. In Preflight (`RPGBossHydrationPreflight.cpp:347`), `Config->Fields.IsEmpty()` evaluates to `false`. Since `TargetOnly` does not evaluate `MemberPlans`, Preflight succeeds without requiring the other 106 boss rows!

---

## 4. The Architectural Truth: Why NONE Can Be 100% Truthful Under End-to-End Hydration

While Candidate Set 1 is **syntactically truthful toward the JSON file and the C++ compiler data structures**, it is **architecturally ungrounded at runtime**.

Under the Lead Conventions (C-294 / C-297), a parity field represents an **active hydration contract**:
```
Authored Value  -->  CompileParticipant  -->  PrepareBatch.Configure  -->  Live Component Property
```
For a `TargetOnly` participant:
1. **No Live Component Destination:** `Destination: "FRPGParticipantStatsConfig::MaxPosture"` describes where `CompileParticipant` stores the value in memory (`RPGEncounterBinding.cpp:120`), but `BP_CombatPlayerCharacter` has NO `URPGBossPosture` component and NO posture hydration adapter. The value is dead data after compilation.
2. **No FirstRead (`PrepareBatch.Configure`):** In `RPGBossHydrationPreflight.cpp:449-456`, `TargetOnly` generates 0 component plans. Therefore, `PrepareBatch.Configure` is **never invoked** for the player participant. Asserting `FirstRead: "PrepareBatch.Configure"` is a structural fiction.
3. **If Destination is Cited as `URPGBossPosture::PostureMax`:** That is demonstrably false because `URPGBossPosture` is never attached to the player pawn (`RPGPlayerMovesSubsystem.cpp:253-295`).

### Conclusion on Truthfulness:
- **Strict Hydration View:** **ZERO rows can be 100% truthful**, because a Target-Only participant has no hydrated components and consumes no authored fields in gameplay.
- **Data Asset Definition View:** **Candidate Set 1 (4 rows) is the minimal truthful authoring manifest**, because those 4 values are genuinely authored in `boss_draft_profiles.json`, validated by `CompileParticipantImpl:42-48`, and stored into `FRPGParticipantConfig:120`.

---

## 5. Architectural Evaluation: Option A vs. Option B

| Criteria | Option A: Minimal Manifest on Hero (`DA_Player_Hero_Draft_V2`) | Option B: Role-Aware Compile Check in Engine |
| :--- | :--- | :--- |
| **Compiler Code Mutation** | **Zero C++ edits.** `CompileParticipant` left 100% unchanged. | Requires editing `RPGEncounterBinding.cpp:115` and `RPGBossHydrationPreflight.cpp:347`. |
| **Asset Changes** | Requires authoring 4 fields and saving a new asset `DA_Player_Hero_Draft_V2.uasset`. | Zero new assets required. Saved `DA_Player_Hero_Draft` passes as-is. |
| **Hydration Semantics** | Fictional downstream consumption (player never runs posture/stats adapters). | **Architecturally pure:** formally acknowledges that a Target participant has no component hydration. |
| **Preflight Parity** | Passes Preflight because Preflight skips 110-path check for `TargetOnly`. | Passes Preflight cleanly once `Config->Fields.IsEmpty()` check is role-aware. |
| **Lead & Owner Gates** | Requires Owner save approval for `DA_Player_Hero_Draft_V2`. | Requires Lead-reviewed spec and Owner approval for Source change. |

---

## 6. Actionable Recommendation for Tech Lead Claude

1. **If the priority is immediate test completion with ZERO Source modifications:**
   - Author Candidate Set 1 (4 Stats rows) into a new profile `DA_Player_Hero_Draft_V2`.
   - Update `emit_fields_manifest.py` to support `--participant-role TargetOnly` (emitting the 4 rows with SHA256 of `boss_draft_profiles.json`).
   - This unlocks DD27j preflight execution immediately without touching C++ compiler source.
2. **If the priority is long-term architectural purity:**
   - Implement Option B: update `CompileParticipant` (or add role parameter) so that `TargetOnly` participants are recognized as defining opponent identities rather than hydrated component bundles.

---
*End of Technical Manifest Options Report. Staged for Lead Reviewer Claude.*
