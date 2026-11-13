# BK-21–25 — BF-X05 selected-route verifier

Converted the BF-X05 Lead acceptance sheet into nine stable predicates in `BF_X05_SELECTED_ROUTE_ACCEPTANCE_TABLE.md`: shared build/map identity, default-off pack regression, exclusive framework route and definition identity, participant generation, native-health/HUD agreement, terminal/victory, retry timing, reset generation fence, and replacement-actor refusal.

`Scripts/Tools/verify_bf_x05_selected_route.py` validates a versioned JSON receipt transcribed from Lead evidence. It fails closed for missing rows/citations, build or map drift, ambiguous route candidates, invalid definition hash/readback, participant or generation mismatches, health/HUD mismatch, incorrect event counts/order state, retry timing, stale callback, and replacement actor refusal. The generated receipt explicitly marks `live_run_verified: false`: only the Lead's raw logs and map run can establish live acceptance.

Synthetic validation: `python Scripts/Tools/test_bk3_bf_x05_verifier.py` — **11/11 passed**. Python compilation passed for verifier and tests; `check_doc_links.py` reports `broken_links=0`. No Unreal, build, PIE, assets, or raw Lead evidence were accessed or changed. The verifier remains unused against live evidence until Claude posts the BF-X05 run.
