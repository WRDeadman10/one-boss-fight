# AR-C31–C35 — KI-192 repeated R2 boundary run

Status: offline run schedule, receipt identity wrapper, contracts, and Lead return checklist complete. Claude's C-1095 run (BUILD-269, five fresh processes per route) is Lead-owned and must be checked in the mailbox before any run files are read or reprocessed. Codex will not launch or mutate the Editor.

## C31 — Repeated boundary matrix

| Route | Trial IDs | Per-process sample order | Process count |
|---|---|---|---:|
| legacy | `legacy-R01` … `legacy-R05` | 0.34 s, 0.35 s boundary, 0.36 s, 0.70 s | 5 |
| data | `data-R01` … `data-R05` | 0.34 s, 0.35 s boundary, 0.36 s, 0.70 s | 5 |

This gives 40 samples, five independent fresh-process observations for each hold duration on each route. Use the same approved Lead probe and same machine/settings as the baseline; do not edit input mapping, threshold, driver timing, or process conditions to force an outcome. Record actual editor FPS/tick values as run metadata rather than treating them as physical controller latency.

## C32 — Explicit per-run identity and batch receipt

`Scripts/Tools/ar_charge_repeat_receipt.py` wraps the existing single-run parser without changing the probe's timing calls or sample payload. The `stamp` command requires the exact run route, Lead Build ID, and trial index 1–5. It verifies `draw_ready=True`, `input_context_active=True`, the exact normal completion summary, and route agreement, then emits stable trial IDs, raw-log SHA-256, and the four original observations. Route identity comes from the same-run `[EncounterActivation] route=...` witness; filtered rows alone are insufficient and a disagreeing probe label fails closed. `draw_ready=True` is required so trials taken while still sheathed cannot be misreported as charge-boundary samples. The `aggregate` command accepts exactly ten receipts, requires BUILD ID consistency, exactly the five trial IDs on both routes, one copy of every canonical case per receipt, and records receipt hashes. It preserves per-trial montage/delay/tick observations and produces a descriptive median only; it makes no device-latency or causal claim.

Example per-run receipt (repeat for each log, changing route/index):

```powershell
python Scripts/Tools/ar_charge_repeat_receipt.py stamp `
  Docs/BossCombatReview/Execution/Claude/P_C1095_KI192REPEAT/probe_legacy_R01.log `
  --build-id BUILD-269 --route legacy --trial-index 1 `
  --output Docs/BossCombatReview/Execution/Claude/P_C1095_KI192REPEAT/legacy_R01.json
```

Aggregate after all ten receipts exist:

```powershell
python Scripts/Tools/ar_charge_repeat_receipt.py aggregate --build-id BUILD-269 `
  --run <legacy-R01.json> --run <legacy-R02.json> --run <legacy-R03.json> --run <legacy-R04.json> --run <legacy-R05.json> `
  --run <data-R01.json> --run <data-R02.json> --run <data-R03.json> --run <data-R04.json> --run <data-R05.json>
```

Do not use a placeholder Build ID for a real run. Keep Claude's existing `ar_charge_receipt.py` output unchanged; this wrapper can be used later against the retained raw logs.

## C33 — Contract and measurement semantics

The offline contract fixes route/trial cardinality, exact five-run schedule, four canonical case identities/order, matching Build ID, input-context/completion stop signals, raw and receipt hashes, and the game-tick-bounded label. The wrapper delegates sample extraction to `ar_charge_receipt.py`, preserving requested hold values, montage positions, observed delays and tick durations. It does not alter `pie_er_control_latency.py`, its input timing, or route mapping while the current Lead run is in progress.

## C34 — Stop and return rules

Stop/flag a trial if route differs, `draw_ready=True` or active input context is absent, the exact completion summary is missing, a required montage/tick/time sample is missing or malformed, or build/run identity is unavailable. The shared finish helper emits `[ERControlLatency] SUMMARY finished: all control samples recorded`; log watchers must match `SUMMARY finished:`. Matching the older `] finished:` pattern misses this marker and waits until timeout. Retain each failed raw log and failure output; do not substitute a different trial or silently omit it. If any one trial fails, report the batch incomplete and run a replacement only as a newly identified process, retaining both failed and replacement artifacts. Return all ten raw logs, ten single-run JSON receipts, aggregate JSON, exact commands, route/build/trial manifest, FPS/tick environment, and SHA-256 hashes.

## C35 — Interpretation boundary

### C-1100 Lead result (2026-11-08)

Lead returned 15 valid fresh-process receipts. DATA x10: tap/0.34/0.35 s selected Ability_E 10/10; 0.36 s selected Ability_E 9/10 and ChargedAttack 1/10; 0.70 s selected ChargedAttack 10/10. Confirmed LEGACY x5 (`RPG_LEGACY_STARTUP=1`, same-run `route=legacy`): tap/0.34/0.35 s selected Ability_E 5/5; 0.36 s selected ChargedAttack 3/5; 0.70 s selected ChargedAttack 5/5. Lead concludes the boundary is tick-quantised near 0.36 s on both routes; the small selection-rate difference is descriptive, not actionable. C-971's apparent route split was DATA vs DATA. No threshold change. KI-192 is CLOSED for PIE; package remains open. Codex did not read/process these receipts or raw logs.

No threshold adjustment is made or recommended; retain the current input mapping and treat the ~0.36 s variation as a game-tick boundary observation.

The offline wrapper's prospective schedule remains five fresh processes per route. C-1100's DATA x10/LEGACY x5 set has separate cardinality and must not be passed to the ten-run aggregate command above.

### Future packaged gate (separate from C-1100 PIE closure)

KI-192 package status remains OPEN. A Lead package receipt must identify the exact Shipping Build ID from `BuildStamp.txt`, configuration, stage root, executable SHA-256, both manifest hashes, packaged-smoke result, and the same-run `[EncounterActivation] route=...` witness. Keep true legacy explicit (`RPG_LEGACY_STARTUP=1`) and DATA activation evidenced in each run log. Capture the four existing holds (0.34, 0.35, 0.36, 0.70 s), individual selected action/montage, game tick, and completion marker. Lead sets the repetition count and environment before running; this offline gate adds no new count or threshold. Reject any label-only route, mixed-build receipt, missing witness, or incomplete hold set. This does not upgrade PIE to package evidence.

Compare future route observations against adjacent hold controls and report counts plus individual results. Game-tick sampling does not establish physical latency or additional causality.

## Validation

`python -m unittest Scripts.Tools.test_ar_charge_repeat_receipt -v`: seven offline contracts passed at the C-1098 follow-through. `test_ar_charge_rerun_contract.py` also checks the vector `.length()` API, draw-ready three-attempt warmup guards and canonical summary marker. These synthetic contracts do not read or upgrade C-1100 run evidence.
