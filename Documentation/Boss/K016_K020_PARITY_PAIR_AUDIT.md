# Queue K K016–K020 — paired parity contract and current run state

## K016 — identity contract (already documented)

`J026_J030_PARITY_CAPTURE_POLICY.md` defines paired runs with the same map, build/binary, content/settings digests, seed, registered driver/ordered args and exact input digest, plus distinct run IDs and explicit trial IDs. Deterministic fields compare exactly; stochastic timing/outcomes need a declared repeat method and raw per-trial values. Missing or unmatched evidence is INCONCLUSIVE. `ENCOUNTER_PARITY_RECEIPTS_H006_H010.md` gives the v2 field contract and says the receipt builder validates supplied facts but does not prove caller truthfulness.

## K017–K018 — run arms

There is no usable paired run to reuse. Existing standalone A4 evidence does not include the complete current v2 runtime envelope or a selected-data arm with matching build/content/settings/input identity. K017 requires a fresh eligible legacy capture; K018 requires selected-data capture with matching declared inputs and an independent run ID. Both are Lead-run; K018 is additionally blocked on G044 typed definitions/manifest/selection and K013's trusted capture bridge.

## K019 — comparator (already implemented)

`Scripts/Tools/compare_encounter_parity.py` validates both receipts, compares declared identity, final marker, terminal result, selection/participants and per-observable values/trial IDs, and writes a deterministic report with receipt hashes and both source-log citations. `--verify-source-logs` verifies cited log bytes. Input/report collisions are refused. A valid value mismatch is FAIL; unmatched trial evidence is INCONCLUSIVE. No code change is needed before real receipts exist.

## K020 — disposition

No paired receipts exist, so there are no real mismatches to disposition. Do not treat synthetic fixtures or standalone legacy evidence as a pair. Revisit after K017–K018 provide complete run envelopes; preserve any actual mismatch rather than averaging or dropping a trial.

This is a static policy/tool audit only; no receipt was created, no tests were run, and no Editor/build/PIE work was performed.
