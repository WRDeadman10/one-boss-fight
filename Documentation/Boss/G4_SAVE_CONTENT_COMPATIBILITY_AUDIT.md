# G4 — save and content compatibility audit

## Source finding

The C++ source contains no `USaveGame` type, `SaveGame` property, or encounter
selection persistence. The selection subsystem's `SelectedDefinition` is
`UPROPERTY(Transient)` (`RPGEncounterSelectionSubsystem.h:50`); the benchmark
path is an in-memory `FString` (`RPGEncounterSelectionSubsystem.h:53`), and
the console selector is process state. Source search for `SaveGame`,
`USaveGame`, `SaveConfig`, config write/flush calls, and config cache writes
found no runtime persistence path for encounter definitions or the legacy
startup route.

The two `ConfigCacheIni.h` hits are not writes: `RPGCombatCatalog.cpp:111`
reads `DirectoriesToAlwaysCook`, and `RPGAutomationTests.cpp:1245` reads the
same setting for a test. This finding is limited to
`Source/OneBossFight` C++ and does not establish absence of Blueprint/plugin
serialization or external project content references.

## Gate impact

For this Source audit, there is no saved encounter-selection state requiring a
save migration matrix. The remaining compatibility gate is authored content
references and dependency/cook closure. Existing evidence tools are
`Scripts/Editor/validate_g044_encounter_selection.py` (asset fields and
reference agreement) and `Scripts/Tools/validate_encounter_manifest.py`
(canonical manifest structure/hash). They validate current authored inputs;
they do not prove a complete Blueprint referencer inventory or packaged cook
closure. Claude must still retain the Editor caller/referencer inventory and
selected-root cook manifest before claiming those gates closed.

No save compatibility claim is made for pack/plugin or Blueprint state outside
the audited Source tree.
