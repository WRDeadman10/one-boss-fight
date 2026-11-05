# Queue J J031–J035 — cook graph and selector boundary

## J031 authored selection graph contract

`Scripts/Tools/normalize_encounter_selection_graph.py` accepts only an explicit `onebossfight.encounter-selection-graph-export/v1` JSON export. The export carries the selected root package, exact build/configuration identity, every traversed package, and each edge as `{source_path, target_package}`. Output is `onebossfight.encounter-package-graph/v2`; it retains the mount-qualified package names and source property/reference path on each edge. The tool does not query Unreal, resolve missing assets, or infer links from C++ defaults. Its output must resolve to a distinct file from the input so raw exports are preserved. No real export is available because the selection asset is not authored.

## J032 authored cook manifest contract

`Scripts/Tools/normalize_cook_package_manifest.py` accepts explicit captured `onebossfight.cook-package-manifest-export/v1` JSON and emits `onebossfight.cook-package-manifest/v2`, preserving build ID, configuration, mount-point/filesystem-root pairs, and unique package names. It refuses output paths that alias the raw export. This is a normalizer for a future authoritative Editor/cook export; it does not itself establish which cook-manifest source is authoritative. No cook export or target package identity is currently available, so conversion has not been witnessed.

## J033 graph verification contract

`Scripts/Tools/verify_encounter_package_graph.py` remains backward-compatible with graph/manifest v1 and accepts graph v2 plus cook manifest v2. It verifies reachable transitive packages only, prints a path chain with the originating reference path for graph v2, rejects duplicate manifest entries, checks v2 build/configuration equality, and validates that mount roots are retained. Invalid non-object graph inputs are reported as validation issues, including when paired with a v2 manifest. Unrelated cooked packages do not repair a missing reachable package. No actual selection graph or cook manifest is available, so no PASS is claimed.

## J034–J035 evidence and decision boundary

Packaged selected activation is BLOCKED pending the typed definitions, manifest, selection asset, authoritative cook/package evidence, and a Claude-owned packaged run that loads the root and emits a truthful receipt. The Shipping selector remains explicitly unapproved. Current development selection is opt-in through the nonshipping CVar/automation path; no Shipping selector or implicit default asset/map is introduced here. The owner must approve any production default or Shipping selection policy before such a change. See `Documentation/Boss/I049_OWNER_DECISION_PACKET.md` and `Documentation/Boss/I050_QUEUE_HANDOVER.md`.
