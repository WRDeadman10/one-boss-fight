# Gate error inventory for implementation triage

Codex-owned offline work while X237 Claude2b diff is pending. No new AG/operator work or engine operation.

`gate_error_inventory.py` reads only the saved C181 engine slice. Output `GATE_ERROR_INVENTORY_2026-10-27.json`, SHA256 `8c72e2a0d25d7611151b9d113fc1db86c2f1410ce3f7a3c8337191fbceef8081`, preserves all raw error lines and line numbers, neighboring final markers, and normalized signature groups. Source pinned to SHA `a4ff5f054c851d9707966c303358fa120ada590bca2d7666223a8f71943dffdf`.

Result: 1,181 errors in 42 signature groups, channels PIE1,127 / CommonUI51 / Catalog1 / LogUtils2. The largest group is 396 pending-kill CameraModeComponent errors at slice lines11854–12595. Other recurring groups include None AbilitySystemComponent accesses (84 and83). Exact semantic text/asset identity retained; only generated instance numbers/TRASH prefixes normalized. Full line receipts remain available for unambiguous review.

Independent receipt checks: raw log hash matches; 1,181 distinct recorded line numbers each equal the exact raw source line; group counts sum to1,181. These are offline data-integrity checks, not Unreal tests or semantic error acceptance.

Triage routing: Catalog's deliberately invalid startup fixture must be correlated with its scenario before expected-error designation; CommonUI concerns real input acceptance and cannot be waived by programmatic selection; LogUtils in-play-mode calls need finish/cleanup context; PIE errors need lifecycle/event correlation and comparison with a pinned prior baseline. The nearest previous/next final is only a navigation interval: it does not establish the emitting actor, active driver or teardown causality. No package is declared error-free and no live fix is included in this inventory.

Use this artifact to pick a minimal reproducible issue after the current behavior-preserving extraction review. Do not mix error fixes into2b or re-run the full gate solely to count unchanged messages.
