# I043–I044 — cook graph and cost receipt tools

## I043 package graph verifier

`Scripts/Tools/verify_encounter_package_graph.py GRAPH.json COOK_MANIFEST.json` verifies normalized inputs:

- Graph schema: `onebossfight.encounter-package-graph/v1`; `roots` is an ordered package-path array and `packages` maps every referenced package to its explicit `references` array.
- Cook manifest schema: `onebossfight.cook-package-manifest/v1`; `packages` lists cooked package paths.
- The verifier traverses only reachable packages from the listed roots, reports a missing package with a discovered root-to-reference chain, and ignores unrelated cooked packages. It performs no Unreal query and makes no package/cook claim on behalf of its inputs.
- Object paths with a dot suffix, duplicate package entries, missing graph nodes and malformed schemas are refused. Runtime conversion from UE cook output into these normalized inputs remains a separate evidence step.

## I044 local cost report

`Scripts/Tools/summarize_encounter_cost.py RECEIPT.json [--report-json PATH]` consumes `onebossfight.encounter-cost-runs/v1` with explicit sample ID, run ID, cold/warm label, build ID, binary/content SHA-256, elapsed milliseconds and raw-log path/hash. The report preserves each sample and source identity.

Percentiles use nearest rank: sort ascending, then use zero-based index `ceil(p*n)-1`. p50, p95 and p99 are reported separately for cold and warm samples. Missing either group, malformed digest/value, duplicate sample ID, or mixed build/binary/content identity yields INCONCLUSIVE. JSON output is sorted and atomically replaced. These tools summarize supplied evidence; no cost samples or cook manifest were available for an execution claim in this batch.
