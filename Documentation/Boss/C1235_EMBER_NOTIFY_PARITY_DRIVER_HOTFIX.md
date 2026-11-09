# C-1235b Ember notify parity driver hotfix

Updated the Lead-only parity driver for the three issues Claude reported from P_C1235_EMBERPARITY3:

- A3a may now finish through its known pack-chain `montage stopped` terminal while still in Active. The per-arm check accepts that specific outcome; the off/on comparison verifies its terminal times within the existing 0.08 s tolerance.
- Complete is compared only when both timing arms ended with the same non-empty reason. Missing, interrupted, or mismatched terminal outcomes are logged as INFO and do not create a false timing failure. Matching terminal reasons still require Complete within tolerance.
- The PARRY arm now mirrors `pie_full_fight.py`'s 115–125 cm distance band, 130 cm hard clamp, face-to-boss setup, and exact `parry.press()` call. It presses only when the measured separation is inside the band. Contact remains sourced exclusively from the shared `GetParriedCount()` counter incremented by `NotifyParried`.

The C-1132 montage-origin press targets and the selected `-abslog` source/warm-up behavior are retained. Codex did not run PIE; Claude owns the Editor rerun.

## Verification

- Offline parity-driver contracts: PASS, 10/10, including Active-phase A3a stop parsing, terminal comparison pass/fail/INFO outcomes, and parry distance/press/counter contracts.
- `python -m py_compile Scripts/Editor/pie_ember_notify_timing_parity.py Scripts/Editor/test_ember_notify_timing_parity_contract.py`: PASS.
- `python Scripts/Tools/check_doc_links.py`: `broken_links=0`.
- Scoped `git diff --check`: PASS (only existing LF-to-CRLF notices).
- No C++ changes, build, native suite, Editor run, or PIE run.
