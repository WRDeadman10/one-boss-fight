# BN-41..45: manual check of the heuristic-O KIs (lane BN, batch 9 of 10, per X-2213)

C (implementer), 2026-11-12. The running count entering this batch is 2 O out of 39 (the lead reclassified KI-110 as L, citing X-245 and DECISIONS.md:648).

**Not done:** no code, asset, engine, build, PIE or test work. No KNOWN_ISSUES status changes and no commits.

| Task | KI | Row | Evidence checked | Manual class | Offline follow-up? |
|---|---|---|---|---|---|
| BN-41 | KI-134 | `KNOWN_ISSUES.md:232`: DD26 source-only limits. Future authored definitions must carry all 110 required paths; serialized asset fields are uninspected; no production caller invokes preflight; the seven profiles have no load or timing proof; "no new UE run yet" | Closing it needs an authored asset inspection plus a UE run | **E** (asset/UE run) | No |
| BN-42 | KI-147 | `:321`: "RESOLVED for baked windows (C-426)". Unbaked windows keep the long-frame interpolation weakness, and a stale bake is not detected | Partly resolved. The residual is a documented procedure (bake every damaging window, re-bake on animation change). Detecting stale bakes would need the animation data, which is Editor-side | **L** (resolved for baked windows; procedure for the rest) + E | No |
| BN-43 | KI-163 | `:337`: `Scripts/Tools/token_coverage.py:35-39,56-71` prints missing logs but does not fail, and may return success | A pure-Python tool; the fix (a nonzero exit on `MISSING`, plus a unit test) needs no engine. BM-01..05 proposed line cites only | **O** | **Yes:** add a strict exit on missing logs, plus a `Scripts/Tools` unit test (lead approval; it changes tool behaviour) |
| BN-44 | KI-164 | `:338`: `Scripts/Tools/evidence_pack.py:40-61` creates the output directory before validating collisions | A pure-Python tool; validating before `mkdir`, plus a temp-dir unit test, is offline. BM-01..05 proposed a cite update | **O** | **Yes:** validate before creating the directory, plus a temp-dir test (lead approval) |
| BN-45 | KI-165 | `:339`: `Scripts/Tools/make_source_manifest.py:17-24` accepts a root with no `Source` folder and writes an empty manifest that reports success | BM-16..20 characterized this with a real subprocess run (`test_ki165_166_characterization.py`, which passes) | **O** | **Yes:** reject a root without `Source` (nonzero exit), then flip the characterization test to expect failure (lead approval) |

**Batch 9 result:** 3 new O (KI-163, 164, 165). Running total: 5 O (KI-026, 067, 163, 164, 165) out of 44.

**Limits:** row reads only. The cited tool line ranges were not re-read in this batch; BM-01..05 and BM-16..20 hold their earlier verification.
