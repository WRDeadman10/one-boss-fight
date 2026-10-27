# AG09 Delivery Report: P1 Shadow Wire Contract Oracle & Comprehensive Mutation Suite (Revision 03)

**Document ID:** `Docs/BossCombatReview/Execution/Antigravity/P1_SHADOW_WIRE_ORACLE_REPORT.md`  
**Revision:** Rev 03 (incorporating all corrections from `[X-194]` and `Docs/BossCombatReview/Execution/Codex/AG09_A128_REVIEW.md`)  
**Author:** Antigravity (Assistant)  
**Assigned By:** Codex Technical Lead (`[X-191]`, `[X-193]`, `[X-194]`)  
**Work Order:** AG09 (Phase 1 P1 Shadow Wire Contract Oracle & Mutation Suite)  
**Date:** 2026-10-27  
**Execution Environment:** Windows / Python 3.10 / Pure Offline Verification (No Engine, No PIE, No Source/ Edits)

---

## 1. Pinned Source Hash Registry & Enforced Pin Checks

All specifications, reference contract validators, and test matrices are strictly pinned. The five source files are enforced with runtime fail-on-drift checks: any discrepancy raises `RuntimeError` prior to AST compilation or test execution. The governing review hashes are recorded as observational review anchors:

### Enforced Frozen Source Pins (Fail-on-Drift Active):
| Component | Repository Path | Frozen Expected Hash | Observed Hash | Status |
| :--- | :--- | :--- | :--- | :---: |
| **Staged Test Driver** | `Docs/BossCombatReview/Execution/Codex/Drafts/Scripts/Editor/pie_timeline_shadow.py` | `c0af0dc6066b73bbbd248981244fc231d653cfc9fbd58cfde4c054958caad99c` | `c0af0dc6066b73bbbd248981244fc231d653cfc9fbd58cfde4c054958caad99c` | **MATCH (ENFORCED)** |
| **C++ Shadow Producer** | `Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGShadowCompare.cpp` | `f6a0274c3bad8d5221981fa10dc529a284aa3285eb1220ba3e4f991a07363924` | `f6a0274c3bad8d5221981fa10dc529a284aa3285eb1220ba3e4f991a07363924` | **MATCH (ENFORCED)** |
| **C++ Producer Header** | `Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGShadowCompare.h` | `95da9c0c6a72a302ed16cc1d9c3b0d5f7fd8e758f573dd65bda0bc4b13ca00ab` | `95da9c0c6a72a302ed16cc1d9c3b0d5f7fd8e758f573dd65bda0bc4b13ca00ab` | **MATCH (ENFORCED)** |
| **C++ Timeline Compiler** | `Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGTimelineCompiler.h` | `5bf162ff250469cf6b80f2edaad5cfc39e969ed4eb6e8d6256cf56b640fe119e` | `5bf162ff250469cf6b80f2edaad5cfc39e969ed4eb6e8d6256cf56b640fe119e` | **MATCH (ENFORCED)** |
| **C++ Participant Key** | `Source/OneBossFight/Player/RPGEncounterBinding.h` | `4330f8c416cd75284e829856b5d1cba7001c5ee62f40bdc7b1bf98a8dbf94a80` | `4330f8c416cd75284e829856b5d1cba7001c5ee62f40bdc7b1bf98a8dbf94a80` | **MATCH (ENFORCED)** |

### Observational Review Anchors:
| Review Document | Repository Path | Raw File SHA256 | LF-Normalized SHA256 | Role |
| :--- | :--- | :--- | :--- | :--- |
| **Codex AG09 A127 Review** | `Docs/BossCombatReview/Execution/Codex/AG09_A127_REVIEW.md` | `a46ee521900ff30d5447df72ad5c52d7a353e70fb6919ce06ef7469975e7ad95` | `a46ee521900ff30d5447df72ad5c52d7a353e70fb6919ce06ef7469975e7ad95` | Observational Anchor |
| **Codex AG09 A128 Review** | `Docs/BossCombatReview/Execution/Codex/AG09_A128_REVIEW.md` | `1e1601024a385bb7e12b28afad4045a4b46acb567af80aa3ced6dd941ac5a8f5` | `1e1601024a385bb7e12b28afad4045a4b46acb567af80aa3ced6dd941ac5a8f5` | Observational Anchor |

### Current AG09 Deliverable:
| Component | Repository Path | Raw SHA256 Hash |
| :--- | :--- | :--- |
| **Test Runner & Suite** | `Docs/BossCombatReview/Execution/Antigravity/test_shadow_wire_oracle.py` | `4125d69227d868f6279f85ac5b02fccb9f29ac00fc5c909d509a4e6d2ea2edaf` |

---

## 2. Executable 31-Field Producer Baseline

The reference synthetic record reproduces the complete top-level wire contract emitted by `URPGCombatTimelineShadow::ObserveAfterTracker` (`RPGShadowCompare.cpp:139-223`).

The baseline JSON below is rendered directly from `COMPLETE_31_FIELD_BASELINE_ROW` in [`test_shadow_wire_oracle.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/test_shadow_wire_oracle.py#L90-L150):

```json
{
  "world_session": "8A32D1844DF2474AA03870678D4E1122",
  "encounter_instance": "C1F7201B94C647B7B08878A7605D3344",
  "participant_slot": "Boss",
  "generation": 1,
  "observation_ordinal": "1",
  "playback_ordinal": "1",
  "authoritative_action": null,
  "source_asset": "/Game/OneBossFight/Boss/Anims/AM_Boss_Attack_01",
  "observed_source_asset": "/Game/OneBossFight/Boss/Anims/AM_Boss_Attack_01",
  "observed_segment_asset": "/Game/OneBossFight/Boss/Anims/AS_Boss_Attack_01",
  "asset_sha256": "4a5e3f1082d491c9b2075f1a30f36f9c87b1c4112e52b2b1a8d01f8e12489110",
  "adapter_sha256": "81c03bf8449c256722ad95a62d088921e649e1a182479e39b972cf61a38bb921",
  "synthetic_fixture": true,
  "projection_policy": 0,
  "move": "A1",
  "variant": "Default",
  "section": "Default",
  "coverage_scope": "GetCurrentActiveMontage result; first slot track/current segment only; other slots, additive sequences, inactive blend-outs UNCOVERED",
  "previous": 0.0,
  "current": 0.016,
  "game_time": 10.016,
  "actual_rate": 1.0,
  "traversal": 0,
  "loop": 0,
  "engine_instance": null,
  "legacy_snapshot": {
    "tracked": true,
    "move": "A1",
    "phase": "Active",
    "instance": 1,
    "illegal_starts": 0,
    "double_launches": 0
  },
  "compiled_crossings": [
    {
      "id": "DamageWindow_01",
      "semantic": "ActiveDamage",
      "position": 0.016,
      "edge": 0,
      "loop_ordinal": 0
    }
  ],
  "window_projections": [],
  "comparison_status": "MATCH",
  "limitation": "MATCH covers sampled active state only, not hit/geometry/cause parity",
  "possible_explanations_not_acceptance": []
}
```

### Verified C++ Serialization Semantics:
1. **Producer Function & Serialization:** Emitted by `URPGCombatTimelineShadow::ObserveAfterTracker(const FObservation& O)` in `RPGShadowCompare.cpp:139-223`.
2. **Generation Domain (`uint32`):** Serialized from `Participant.Generation` where `Participant` is `FRPGParticipantKey` (`Source/OneBossFight/Player/RPGEncounterBinding.h:76`), declared as `uint32 Generation = 0;`. Bound participant keys initialize generation to 1 and advance through positive `uint32` values (`1..4294967295`). Emitted records require positive `uint32`.
3. **GUID Format:** `world_session` and `encounter_instance` are serialized via `Participant.WorldSession.ToString()` which in Unreal Engine 5.5 defaults to `EGuidFormats::Digits` (`Guid.h:322`), producing exactly 32 hexadecimal characters without hyphens.
4. **Ordinal Decimal Stringification:** `observation_ordinal` (`LexToString(O.Sample)`) and `playback_ordinal` (`LexToString(O.PlaybackOrdinal)`) start at 1 because `FPlaybackAdapter::Observe` executes `++Sequence;` and `++Ordinal;` prior to observation creation (`RPGShadowCompare.cpp:59, 81`). They are serialized as canonical ASCII positive decimal strings (`^[1-9][0-9]{0,19}$`) bounded by `2^64 - 1` (`18446744073709551615`).
5. **Source-Permitted Empty Segment Asset:** `CaptureAfterTracker` only sets `CurrentSegmentAsset` if an active montage segment exists (`RPGShadowCompare.cpp:42-49`). When absent, `ObservedSegmentAsset` serializes as empty string `""` (`RPGShadowCompare.cpp:76, 151`). The wire contract permits empty string for `observed_segment_asset`, distinct from omitting the key.
6. **Always-Present Nullable Keys:** `authoritative_action` and `engine_instance` are unconditionally emitted on the wire. When unset, they serialize as explicit JSON `null` (`MakeShared<FJsonValueNull>()`). Omission of either key from the row dictionary is a wire format violation.
7. **Integer Representability:**
   - `generation`: positive `uint32` (`1 <= x <= 4294967295`).
   - `engine_instance`: int32 (`0 <= x <= 2147483647` in PIE, or `null`).
   - `loop`: uint32 (`0 <= x <= 4294967295`).
   - `legacy_snapshot.instance`: int32 (`-2147483648 <= x <= 2147483647`).
   - `legacy_snapshot.illegal_starts` and `double_launches`: non-negative int32 (`0 <= x <= 2147483647`).
   - `compiled_crossings[].loop_ordinal`: uint32 (`0 <= x <= 4294967295`).
8. **Diagnostic Status Transport:** Valid producer-emitted statuses include `"MATCH"`, `"REGRESSION_CANDIDATE"`, `"UNTRACKED_PACK_PATH"`, `"MISSING_METADATA"`, `"INCONCLUSIVE_SAMPLING"`, and `"INVALID_RUN"`. Diagnostic status transport validity is strictly separated from gameplay parity verdict.

---

## 3. Targeted Corrections in Revision 03

Per Codex Review `[X-194]` / `AG09_A128_REVIEW.md`:

1. **Generation Domain Correction (`FRPGParticipantKey::Generation`):**
   - Corrected oracle validation to positive `uint32` (`1..4294967295`).
   - Added `POS-13` (`generation = 2147483648` / `2^31`), `POS-14` (`generation = 4294967295` / uint32 max), and `POS-15` (cross-row upper-range advance `2^31 -> 2^31 + 1`).
   - Added mutations `MUT-37` (`generation = 0` rejected), `MUT-38` (`generation = 4294967296` overflow rejected), `MUT-39` (`generation = -1` rejected), and `MUT-40` (`generation = True` bool-as-int rejected).
2. **Pinned Binding Header Dependency:**
   - Added `Source/OneBossFight/Player/RPGEncounterBinding.h` (`4330f8c416cd75284e829856b5d1cba7001c5ee62f40bdc7b1bf98a8dbf94a80`) to enforced frozen pins.
3. **Provenance & Anchor Clarification:**
   - Updated governing review hash citations: `AG09_A127_REVIEW.md` raw file hash is `a46ee521900ff30d5447df72ad5c52d7a353e70fb6919ce06ef7469975e7ad95`; `AG09_A128_REVIEW.md` is `1e1601024a385bb7e12b28afad4045a4b46acb567af80aa3ced6dd941ac5a8f5`.
   - Distinctly separated enforced file pins from observational review anchors.
4. **Clarified Synthetic Fixture Explanation:**
   - Narrowed description: dormant validator in `pie_timeline_shadow.py` accepts `synthetic_fixture = 1` because it omits `synthetic_fixture` checking entirely.
5. **Full Individual Key Deletions Test Matrix:**
   - Added 31 isolated test cases (`MUT-KEY-DEL-01` to `MUT-KEY-DEL-31`) proving that every single key in `INDEPENDENT_PRODUCER_31_KEYS` is individually required and rejected upon deletion.

---

## 4. Test Suite Execution & Results (86 Cases)

The expanded test suite executes 86 test cases (15 positive fixtures, 40 isolated one-defect mutations, and 31 individual key deletion mutations):

- **Positive Fixtures (15/15 PASS):**
  * `POS-01`: Complete 31-field baseline fixture.
  * `POS-02`: Zero compiled crossings MATCH (mid-window tick).
  * `POS-03`: `EEdge::Marker` crossing (`edge = 2`).
  * `POS-04`: `EEdge::Closed` crossing (`edge = 3`, id=`"None"`).
  * `POS-05`: Explicit null-valued required keys (`authoritative_action`, `engine_instance`).
  * `POS-06`: Reset generation advance with continuous clock (`gen 1 -> 2`, `time 10.0 -> 10.5`).
  * `POS-07`: Source-permitted empty `observed_segment_asset` (`""`).
  * `POS-08`: Diagnostic status transport (`REGRESSION_CANDIDATE`).
  * `POS-09`: uint64 ordinal above `2^53` (`9007199254740993`).
  * `POS-10`: uint64 maximum boundary (`18446744073709551615`).
  * `POS-11`: Traversal variant (`ETraversal::Reverse = 1`).
  * `POS-12`: Engine instance int32 max (`2147483647`).
  * `POS-13`: Positive uint32 generation (`2^31 = 2147483648`).
  * `POS-14`: Maximum uint32 generation boundary (`4294967295`).
  * `POS-15`: Cross-row upper-range generation advance (`2^31 -> 2^31 + 1`).

- **Isolated One-Defect Mutations (40/40 PASS):**
  * `MUT-01` to `MUT-04`: Missing required and nullable keys (`playback_ordinal`, `authoritative_action`, `engine_instance`, `observed_segment_asset`).
  * `MUT-05` to `MUT-11`: Canonical ordinals (JSON number, non-decimal, zero `'0'`, leading zero `'01'`, newline `'1\n'`, non-ASCII Arabic `'١'`, uint64 overflow).
  * `MUT-12` to `MUT-20`: Types, source widths, enum bounds (`synthetic_fixture` int, `engine_instance` overflow, row `loop` overflow/negative, crossing `loop_ordinal` overflow, `legacy_snapshot.instance` overflow, `traversal` out-of-domain, `projection_policy` out-of-domain, crossing `edge` out-of-domain).
  * `MUT-21` to `MUT-22`: GUID format (hyphenated rejected, non-hex rejected).
  * `MUT-23` to `MUT-26`: Safe malformed inputs (`comparison_status = []` safely rejected without `TypeError`; `current = 10**400` safely rejected without `OverflowError`; `NaN` float; `Inf` crossing position).
  * `MUT-27` to `MUT-31`: Nested schemas (empty legacy, legacy type error, crossing missing edge, projection missing ClampedFrom, explanation missing evidence).
  * `MUT-32` to `MUT-36`: Trace continuity (session identity leak, ordinal inversion, generation regression, backward time same gen, reset time continuity inversion).
  * `MUT-37` to `MUT-40`: Generation domain (`generation = 0` rejected; `generation = 2^32` overflow rejected; `generation = -1` negative rejected; `generation = True` bool-as-int rejected).

- **Individual Key Deletions (31/31 PASS):**
  * `MUT-KEY-DEL-01` to `MUT-KEY-DEL-31`: Deletion of each of the 31 keys in `INDEPENDENT_PRODUCER_31_KEYS` independently rejected.

- **Suite Totals:**
  * **86/86 assertions passed** (Exit Code 0).
  * Detected **39 permissive gaps** in dormant validator AST (`pie_timeline_shadow.py`).
  * **Runner Failure-Path Self-Test Verified:** Proven in-memory that contradictory expectations trigger the harness failure branch and exit with code 1.
