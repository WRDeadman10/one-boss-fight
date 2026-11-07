# C-948 X2 — Round 6 build-ID intake audit

**Scope:** offline kit/receipt tools under `Scripts/Tools`; no kit creation, benchmark, Editor, or game run by Codex.

## Producer and consumer check

`Scripts/Package.ps1` now generates `OBF-{CONFIGURATION}-{UTC timestamp}-{8 hex characters}` for every configuration. The retained C-947 `stamps.txt` contains real Shipping and Development IDs from that producer. Its real `BUILD_INFO.txt` selects the Shipping ID and includes the executable SHA-256. `check_bench_kit.py` accepts the Shipping and Development prefixes and rejects the old `OBF-DEV-` form. A new fixture passes the retained Shipping BUILD_INFO, and a synthetic Development BUILD_INFO using the retained Development stamp, through the checker CLI in Shipping-plus-Development and Development-only modes. It also guards the producer expression and rejects a regression to the old Development prefix.

`MakeBenchKit.ps1` generates BUILD_INFO from the selected stage's `BuildStamp.txt` and invokes `check_bench_kit.py` before zip creation. Its copy-manifest validator, `check_bench_kit_manifest.py`, checks staged source names rather than build identity; the dependency test now asserts the kit includes both the kit checker and Round 6 receipt report.

`round6_benchmark_report.py` summarizes metric receipts and intentionally does not consume BUILD_INFO or claim binary identity. The Round 6 intake guide requires build identity to remain with the raw run bundle and owner report. No build-ID format change is needed in that summarizer; it has no conflicting parser or restriction.

## Result

No remaining producer/consumer mismatch found after the C-947 Package.ps1 fix. The existing `check_bench_kit.py` validator already accepts `OBF-SHIPPING-...` and `OBF-DEVELOPMENT-...`; no production tool changes were needed. The producer-to-checker regression fixture and full offline suite results are recorded in `Documentation/TEST_PLAN.md`.
