# Generated scaffold header audit (S178)

Static comparison of maintained rule/profile scaffolds with existing C++ and designer-reference conventions. The scaffold commands were not executed.

## Result

- `Scripts/Tools/new_rule_scaffold.py:15-52` generates the C++ header and test with `// Copyright One Boss Fight. All Rights Reserved.`. Its test include uses the project module path `Player/RPGBoss<Name>Rules.h`, matching `Source/OneBossFight/Tests/RPGBossMoveSelectorTests.cpp:1-3` and the header include convention in `Source/OneBossFight/Tests`.
- Its generated designer reference (`new_rule_scaffold.py:44-52`) links source and test paths under the project tree and says not to claim live proof without a cited PIE log. This meets the evidence-caveat requirement.
- `Scripts/Tools/new_profile_field_scaffold.py:1-61` prints a checklist rather than generating files. It points at the profile declaration/implementation, tests, evidence, token indexes, and lifecycle sites, and explicitly says to verify ownership, resets, and tests in current source.

## Disposition

The generated rule files include the project license, module-relative include, and evidence caveat. The profile-field scaffold is checklist-only and has no generated file header to evaluate. Static template review; no scaffolder, tests, build, or Editor was run.
