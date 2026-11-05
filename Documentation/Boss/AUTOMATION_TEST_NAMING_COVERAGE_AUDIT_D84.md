# Automation test naming and coverage map audit (Queue D84)

Static comparison of current C++ registrations with existing Markdown references. Index: [AUTOMATION_TEST_ID_INDEX_D84.md](AUTOMATION_TEST_ID_INDEX_D84.md). No Unreal test run/build/editor run.

## Registration identity and naming

- Source scan finds 335 registration IDs and 335 unique IDs; C++ test class names are also unique. No duplicate registrations were found.
- The D81 index lists C++ class names and source locations, not the Unreal automation IDs. D84 adds the separate source-generated index with each exact registered ID, class, location, and flags. It is source inventory, not discovery/execution evidence.
- Registrations use namespace-style families (`OneBossFight.Binding.*`, `.Framework.*`, etc.) with descriptive case suffixes. BOSS/KI requirement IDs are usually comments or surrounding feature docs rather than registration-name components, so the name alone is not a dependable requirement trace.

## Exact documentation-link census

- Before adding this D84 map, an exact-ID scan across `Documentation/*.md` found 121 of 335 current IDs and no exact Markdown mention for 214. That means “no exact-name documentation link found,” not “no test exists” or “no requirement coverage”: test bodies, case comments, grouped suite documentation, and code histories can still describe coverage.
- `Documentation/TEST_PLAN.md` contains 60 strings matching the `OneBossFight.*` shape; 31 are exact current IDs and 29 are not. Of the latter, 13 are old `Binding.*` family aliases (for example `.DormantWake` where current registrations are `.Assign`, `.Validation`, etc.), 14 are historical test/suite labels, one is the broad `OneBossFight.Framework` family label, and one is the incidental `OneBossFight.exe` product name captured by the broad scan. The historical rows explicitly marked RETIRED are stale as runnable test names by design; keep them as history. The binding family aliases are suite descriptions, not exact runnable IDs.
- The three C-754 additions now have exact `TEST_PLAN.md` entries and registered IDs: `OneBossFight.Framework.Executor.StatefulLifecycleHarness`, `OneBossFight.Framework.QueueDEdgeBoundaries`, and `OneBossFight.Framework.LosMemory.AbsoluteDeadlineAcrossLeash`. They await Lead build/full-suite execution.

## Requirement tags and duplicate-claim classification

A lexical scan from each registration to the next found 30 test blocks containing an explicit `BOSS-*` or `KI-*` tag, covering 28 distinct tags; 305 blocks had no such tag in that source interval. This is a source-label count, not a semantic audit of every assertion or comment elsewhere in a file. Nine tags occur in two or more distinct registrations (including `BOSS-PAC-003` in three, and `KI-097` in two); those are multi-test claims, often rule/profile or unit/live-support layers, not duplicate registration IDs. Whether two tests duplicate the same behavior requires assertion-level review and remains unclassified here.

## Disposition

Use D84's exact-ID index for runnable names. Historical retired labels and group aliases are categorized above; 214 IDs still lack an exact documentation link in the pre-index Markdown corpus, and semantic requirement coverage for those remains unknown. Duplicate registered IDs: zero. No source code changed for D84.
