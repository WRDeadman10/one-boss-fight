# AR-C06–C10 — KI-192 route receipt parser

`Scripts/Tools/ar_charge_receipt.py` reads one route's raw Unreal log or filtered `P_*` lines and prints JSON to stdout. It is standard-library-only and does not modify the input file. It locates the structured `sample case=R2_hold_...` payload independent of the timestamp or `LogPython` category. For route identity, `[EncounterActivation] route=...` in the same run is authoritative. The probe's `[ERControlLatency] route=...` (or retained C-971 `[Showcase] route=...`) row is only a request label and must agree with that witness; disagreement fails closed with both values. Generic startup prose is not a route witness. Unrelated `LogRPG*` output is ignored.

```text
python Scripts/Tools/ar_charge_receipt.py <one-route-log> --build-id <Lead-reported-build-id>
```

The parser requires exactly one distinct same-run activation route witness and a separate explicit build ID from the Lead's run metadata. If a probe route row exists, it must match activation. It does not derive build identity from a directory or filename. It hashes the input bytes and requires exactly one sample for each nominal 0.34, 0.35, 0.36, and 0.70 s R2 hold. Each record retains the montage, montage position, observed game-tick-bounded delay, and tick duration. It marks the result as not physical device latency. Contracts cover a same-run activation witness for filtered lines, route disagreement, full-editor startup prose, and timestamp/category-prefixed samples. C-971 nominal legacy lines conflict with their same-run `route=data` activation witness and are rejected; no historical route claim is upgraded by the parser.

The C-971 filtered line files include the route and four samples but do not include a build ID; its summary also does not identify one. They therefore cannot be emitted as fully identified receipts without a separately sourced build ID. Tests use a clearly marked `TEST-FIXTURE-ONLY` identity when exercising retained logs; never use that placeholder for an actual Lead run. Parsing does not fill the historical evidence gap or re-evaluate Claude's reported results.

Validation:

```text
python -m unittest Scripts.Tools.test_ar_charge_receipt
python -m py_compile Scripts/Tools/ar_charge_receipt.py Scripts/Tools/test_ar_charge_receipt.py
```

Result: see current mailbox batch receipt. No raw evidence was edited.

## Lead runner specification (not run by Codex)

- Run five fresh Editor processes for each route through `Scripts/RunLeadPie.ps1`. The legacy arm must set `RPG_LEGACY_STARTUP=1` (or launch with `-RPGLegacyStartup`); the data arm sets `/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter` before Editor startup. The runner fails closed unless the same raw log contains exactly the requested `[EncounterActivation] route=legacy` or `route=data` witness.
- In every process, use `L_SevarovArena`, the same Lead-controlled machine/configuration, `-nosound`, and the existing `Scripts/Editor/pie_er_control_latency.py` four-case order (0.34, 0.35, 0.36, 0.70 s). This yields five independent observations per hold and route; do not treat multiple cases in one process as independent process repetitions.
- Preserve one immutable raw log per route/repetition, with route, build ID, run label, environment, activation witness, and SHA-256 manifest. Confirm `input_context_active=True` and normal probe completion. Stop and report the full failed run if any required sample/montage/tick/identity is absent; do not drop outliers.
- Parse each file with `python Scripts/Tools/ar_charge_receipt.py <one-route-raw-log> --build-id <Lead-reported-build-id>` (raw logs contain the route witness); for filtered lines also pass `--route-witness-file <same-run-raw-log>`. Do not pass a placeholder identity for a real run. Return ten raw logs and ten JSON receipts to Claude. These are game-tick-bounded observations, not device latency and not a root-cause test.
