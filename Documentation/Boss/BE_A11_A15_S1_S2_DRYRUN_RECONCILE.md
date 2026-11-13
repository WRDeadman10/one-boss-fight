# BE-A11..A15: Queue BE_AG Batch 3 — `S1`/`S2` `90–120 cm` Dry-Run Reconciliation

**Authority:** [`QUEUE_BE_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BE_AG.md), `[X-1878]` (`0` commits, `0` pushes, `0` editor/build calls)

---

## 1. Batch 3 Task Disposition (`BE-A11..BE-A15`)

| ID | Task | Status | Evidence / Missing Input |
|---|---|---|---|
| `BE-A11` | Frame-cite Lead live PIE visual captures for `S6`, `S7`, `S8` | **`BLOCKED`** | Live `S6–S8` PIE capture sheets not yet generated (pending `[C-1286]`). |
| `BE-A12` | Draft post-PIE tuning delta table across `S1..S8` | **`BLOCKED`** | Depends on `BE-A11` live PIE results. |
| `BE-A13` | Reconcile `S1`/`S2` `90–120 cm` dry-run & punish margin against `BC-A06` trace | **COMPLETE (Transient Verified; Live Save/Reach Open)** | [`test_be_a13_s1_s2_dryrun_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_be_a13_s1_s2_dryrun_contract.py) verifies `BE_X26_X30_S1_S2_RANGE/Run_20261110_182845/status.txt` (`S1_RANGE=True`, `S2_RANGE=True`, `0.352996 s` margin); live saved cards & exact `S2` reach remain pending Lead `[C-1286]`. |
| `BE-A14` | Update `S1–S8` contracts for Lead-approved post-PIE deltas | **`BLOCKED`** | Awaits Lead post-PIE tuning deltas (`BE-A12`). |
| `BE-A15` | Prepare Batch 3 Owner-ready manifest (`0` commits) | **COMPLETE** | `BE_A11_A15_S1_S2_DRYRUN_RECONCILE.md`, `Scripts/Tools/test_be_a13_s1_s2_dryrun_contract.py`. |

---

## 2. `BE-A13` Reconciliation Summary (`BE_X26_X30` vs `BC-A06`)

- **Approved Range Alignment:** `Move_Sevarog_Swing1_Medium` (`S1`) and `Move_Sevarog_Swing2_Medium` (`S2`) both enforce `[90.0, 120.0] cm` in transient authoring dry-run (`S1_RANGE=True`, `S2_RANGE=True`, `NO_SAVES=True`, `PASSED=509`); `S3` remains `[90.0, 180.0] cm`.
- **Punish Margin Verification:** `recovery 0.703333 s - light_startup 0.350337 s - walk_in 0.000000 s = 0.352996 s` (`+0.353 s`, `+0.053 s` above `0.300 s` required).
- **Open Boundary Retained (`C-1269`/`BE-X26`):** `Swing2_Medium`'s `BC-A06` single-tick trace nearest distance was `37.022 cm` @ `0.229 s` inside `0.200–0.400 s` — Lead must verify live saved `S1`/`S2` reach after `author_sevarog_draft_cards.py` saves updated assets.
