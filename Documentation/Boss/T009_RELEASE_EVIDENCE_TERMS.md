# Release evidence terms

These terms answer different questions and must remain separate in project reports.

| Term | What it establishes | What it does not establish | Project evidence |
|---|---|---|---|
| A5 parity | Registered legacy/data driver pairs behave within the accepted exact, typed, and explicitly declared WARN rules | Shipping package activation, target-hardware speed, visual recovery, or content cook completeness | `Documentation/Boss/S36_A5_PARITY_OPERATOR_RUNBOOK.md`; BUILD-221 pairs |
| Package smoke | A particular staged package starts and passes the listed startup/selection/log checks | Full combat parity, stable target performance, or owner visual approval | `Scripts/PackagedSmoke.ps1`, `Documentation/Boss/S06_S10_SHIPPING_PACKAGE_GATES.md` |
| Cook evidence | Required package roots and closure references appear in the package's authoritative cook manifest, subject to the documented editor-only allowlist | Runtime correctness or save/content compatibility by itself | `Scripts/Tools/check_g044_cook_manifest.py`, `Documentation/Boss/H2_G044_CONTENT_COOK_CENSUS_EXPECTED.md` |
| Performance evidence | Retained measured runs on identified hardware meet the selected metrics under comparable setup | Input feel, visual clarity, or selector recovery | `Scripts/RunBenchmark.ps1`, `Documentation/BENCHKIT_README.md` |
| Release readiness | Lead/owner disposition of all release gates using their required package, performance, compatibility, and recovery evidence | A single automated test count or parity percentage | `Documentation/Boss/P15_A7_PARITY_SUMMARY_DRAFT.md` |

When an evidence type is absent, report the gap explicitly. Do not infer a package result from source inspection, or a runtime result from an offline comparator.
