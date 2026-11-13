# QUEUE_BD_AG Batch 4 Receipt (`BD-A16`..`BD-A20`)

**Authority:** [`QUEUE_BD_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BD_AG.md), `[X-1872]` (`0` commits made, `0` pushes, `0` editor calls)

---

## 1. Batch 4 Status Matrix (`BD-A16..BD-A20`)

| ID | Task | Status | Disposition / Evidence |
|---|---|---|---|
| `BD-A16` | Append `DECISIONS.md` for Greystone RM4 gate verdict, `X26` card acceptance, & post-PIE tuning | **`BLOCKED`** | Awaits Lead `[C-1286]` verdicts on RM4 & `X26`/`BE` live runs (Claude out until `02:31` IST). |
| `BD-A17` | Sync `KNOWN_ISSUES.md` (close resolved `BB-A15` texture probe once Lead verifies) | **`BLOCKED`** | Holds until Lead formally closes `BB-A15` texture probe & `RM4`/`X26` verdicts. |
| `BD-A18` | Owner-ready commit list for accepted `X26` / `BE` slices | **`BLOCKED`** | `X26` (`[X-1864]`) & `BE` Batches `1–6` (`[X-1866..X-1871]`) await Lead `[C-1286]` acceptance (`0` unaccepted files staged). |
| `BD-A19` | Verify `Config/DefaultGame.ini` `DirectoriesToAlwaysCook` covers all authored & planned `S6–S8` + Greystone assets | **COMPLETE** | [`test_bd_a19_cook_coverage_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bd_a19_cook_coverage_contract.py) verifies all `5` `Player/Greystone/*.uasset`, all `7` `Data/Sevarog/*.uasset`, planned `S6–S8` cards, and `ParagonSevarog` anims. |
| `BD-A20` | Run offline smoke + `check_doc_links.py` & prepare Batch 4 Owner-ready manifest | **COMPLETE** | Full active contract suite PASS + `broken_links=0`. |

---

## 2. Owner-Ready Batch 4 File Manifest (`BD-A20`)

Antigravity deliverables ready for Owner review/commit (`0` commits made):
- `Documentation/Boss/BD_A16_A20_BATCH4_RECEIPT.md`
- `Scripts/Tools/test_bd_a19_cook_coverage_contract.py`
