# W-C004 — owner decision sheet after Round 6

**Status: awaiting Round 6 return and owner image-quality review. No setting is selected here.**

## Evidence already available

- Round 5, RTX 3060, Development kit: TSR 28.6 FPS / about 41.6 ms p99; DLSS Quality 32.6 / 36.5; Balanced 36.4 / 32.9; Performance 38.1 / 31.9. All missed the 60 FPS and 16.67 ms p99 targets. These are R5 figures, not Round 6 results.
- V-A021 predicts L1 4.0–5.5 ms, L2 5.5–6.5 ms, L3 7.0–8.5 ms GPU savings. These are estimates; measured columns are blank in `W_C003_PREDICTED_MEASURED_SAVINGS.md`.
- Round 6 acceptance requires 3 valid witnesses per DLSS mode, active upscaler/mode logs, anchor drift ≤5%, no p99 regression >5% versus TSR, then owner image-quality acceptance before Phase 2.
- Current R6 Development kit integrity check fails; see `V_C091_C095_HANDOVER_AND_REVIEW.md`. A valid, stamped kit and returned raw bundle are prerequisites to a decision.

## Three owner decisions (complete only after valid Round 6 intake)

1. **DLSS default mode:** ☐ TSR / ☐ DLSS Quality / ☐ DLSS Balanced / ☐ DLSS Performance / ☐ retain current setting. Round 6 measured values: avg FPS ___; p99 ___ ms; GPU avg ___ ms; valid trials ___/3; active-mode witness ☐ yes ☐ no.
2. **Image quality:** ☐ Accept selected mode / ☐ Reject selected mode / ☐ Need another comparison. Owner notes/capture reference: ____________________.
3. **Fire shadow profile:** ☐ Keep current / ☐ L1 / ☐ L2 / ☐ L3 / ☐ test a narrower option. Round 6 measured savings: ___ ms; visual review: ☐ accepted ☐ rejected ☐ pending.

Any approved change still requires a build-identified configuration and the five-driver parity spot-check. This sheet records decisions only; it does not apply settings or close release gates.
