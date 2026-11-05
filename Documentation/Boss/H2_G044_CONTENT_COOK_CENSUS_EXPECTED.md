# H2 — G044 content/cook closure census

**Lead-run, read-only.** Run `Scripts/Editor/report_g044_dependency_census.py`
in UE 5.5.4 Editor. It must not modify assets, maps, configs, manifests or
files. Retain the complete `[H2_G044_COOK_CENSUS]` JSON and summary.

## Current Lead census and cooked-tree review (C-876/C-878)

All three roots are present. Combined closures contain 215 packages for the
selection, 210 for the boss draft, and 210 for the player draft. The Lead
reports 49/48/44 external engine dependencies and approximately 150 `/Game`
packages per root outside explicit always-cook directories. All roots are
under `/Game/OneBossFight/Data`, which is listed in `DirectoriesToAlwaysCook`
in `DefaultGame.ini`. C-878 reports the Lead's BUILD-222 cooked-tree review
found all three roots present. Of 156 combined `/Game` closure paths, 78 were
not cooked; Lead classified all 78 as editor-only skeleton references:
28+28 Manny/Quinn Control Rig poses, 4 rigs, 12 Quinn textures, 2+2
Quinn/Mannequin meshes, and 2 Quinn material instances. Lead closed the S06
closure review on that basis. This classification is not a claim that each
reference is cooked or loaded at runtime; keep the category visible in any
future package audit. The generic comparator supports explicit, folder-scoped
editor-only exclusions, with no default allowlist (C-878; see
`Documentation/Boss/S06_S10_SHIPPING_PACKAGE_GATES.md`).

## Roots and report

The three roots are the G044 encounter selection, boss draft
`DA_Boss_EmberWarden_Draft`, and player draft
`DA_Player_Hero_Draft_V3`. For each, inspect root presence, direct hard and
soft package dependencies, and the combined transitive Asset Registry
dependency closure. The script reports `/Game` dependencies covered by
`DirectoriesToAlwaysCook` and those outside explicit always-cook directories,
along with the config file/line for each configured directory. Plugin content
mounts appear under `non_game_content_packages`; `/Engine` and `/Script` leaves
are listed separately as external module/engine dependencies.

## Lead review and closure rule

1. Refuse closure if any root is missing or the log contains scan errors.
2. Review every direct/transitive hard and soft dependency. For each `/Game`
   package, identify the reason it is cooked: explicit `DirectoriesToAlwaysCook`
   match or inclusion through the selected root's actual cook dependency graph.
   Review plugin and `/Script` references separately as code/module dependencies.
3. Compare the entire census against the authoritative Shipping cook manifest
   and package logs. Every required content dependency must appear in the cook
   proof; the Asset Registry traversal by itself cannot prove a package was
   cooked or loaded.
4. Record missing, excluded, unresolved, or out-of-root references with exact
   package paths and disposition. Do not edit assets or add directories to
   always-cook as part of this audit.

**Acceptance:** all three roots are present, the full reference closure is
reviewed, every required content package is accounted for in the authoritative
Shipping cook manifest, and no unresolved required dependency remains. This
closes H2's census only; packaged activation remains H1.

## R6 transfer-kit follow-up (Codex Y016–Y020, 2026-11-06)

The external R6 kit contains staged Shipping and Development UFS file manifests.
The Shipping manifest lists all three roots and 78 of the 156 unique `/Game`
paths in the retained H2 closure. Its 78 missing paths match C-878's prior
editor-only skeleton-reference categories (28 Manny poses, 28 Quinn poses, 4
rigs, 12 Quinn textures, 2 Quinn material instances, 4 meshes). This is a
category-level reconciliation, not independent proof of editor-only status.
BUILD_INFO does not bind the manifests to a package ID or executable hash, and
no UAT log or normalized schema manifest accompanied the kit. The package/cook
gate therefore remains open pending identity-bound evidence. Hashes and method:
`Documentation/Boss/Y016_Y020_A7_COOK_MANIFEST_RECONCILIATION.md`.
