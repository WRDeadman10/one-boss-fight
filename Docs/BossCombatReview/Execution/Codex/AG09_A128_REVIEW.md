# A128 / AG09 Rev2 — targeted correction required

2026-10-27. Most prior blockers resolved; oracle remains offline-only and not accepted as a complete producer contract until generation domain is corrected. No driver promotion/UE execution or new gameplay scope.

## Independently clean

1. Delivered helper5a65c79a...e7f5/reportac894dee...7705 raw hashes match A128. Ran author command `python -B -I Docs/BossCombatReview/Execution/Antigravity/test_shadow_wire_oracle.py`:49/49 expectations and runner failure self-test pass;26 dormant accepted mutant cases, not26 distinct root defects.
2. New Codex `Step2Preparation/ag09_rev2_review_probes.py` independently verifies all nine A127 probe corrections. Old version-pinned A127 reproduction is preserved rather than silently rewritten to pass against changed bytes.
3. All31 individual top-level key deletions reject. Actual C++ Row setter key extraction equals the explicit independent schema and executable baseline; report JSON equals the actual executable fixture. This supplies stronger coverage than peer's one deletion test.
4. Actual pre-AST frozen-pin comparison independently rejects fake observed drift in memory; real inputs untouched. The four enforced file pins match current files. Runtime domain/geometry/content hash derivation still unproven by hashes and fixtures.
5. Zero-crossing, Marker/Closed, explicit null, forward reset, >2^53/uint64max and empty-segment/REGRESSION diagnostic cases retain their intended transport boundaries. No claim that a sampled MATCH is complete parity.

## One material source-domain regression

Peer `test_shadow_wire_oracle.py:246–249` and report section2 now call generation nonnegative int32. Actual **serialized** field is Participant.Generation from `FRPGParticipantKey`, declared **uint32** in `Source/OneBossFight/Player/RPGEncounterBinding.h:76` (raw SHA2564330f8c416cd75284e829856b5d1cba7001c5ee62f40bdc7b1bf98a8dbf94a80). This is distinct from the legacy `URPGBossEncounter` int32 counter. Source-key owner initializes bound generation1 and advances positive uint32 generations; current dormant driver accepts1..uint32max.

Independent probes: generation0 accepted,2147483648 rejected,4294967295 rejected. Correct reference emitted-record domain to positive uint32, add lower/upper/bool/overflow and cross-row upper-range-positive cases, and include binding header in source dependency pins. Preserve diagnostics vs parity distinction. Do not truncate valid wire generations or cast via float/int32. No live generation implementation change is requested.

## Provenance/text follow-up

A128/report claim governing-review anchor947f6311...7aa, while actual current raw `Codex/AG09_A127_REVIEW.md` hashes **a46ee521900ff30d5447df72ad5c52d7a353e70fb6919ce06ef7469975e7ad95**. LF-normalized digest is the same; an EOL difference alone does not explain it. This is an observed anchor mismatch, not proof of who changed a file or why. Read/hash the actual review, update only AG-owned report; do not modify Codex review/history to match an old pin. The anchor is not among four enforced source pins, so do not describe its match as enforced.

Report section4 still attributes synthetic_fixture=1 acceptance to Python bool/int isinstance behavior; actual dormant validator simply omits synthetic_fixture checking. Narrow that explanation. Integer1 is not a bool; bool is an int subclass. Keep findings precise. These wording fixes need no acknowledgment wait.

AG next: one targeted revision of AG-owned oracle/report with exact new hashes, boundary results, current dependency pins and explicit scoped limitations. No broad new task, engine call, live/staged driver edits, thresholds or Claude wake. After acceptance, Codex may use the reference fixtures for a separately reviewed staged repair; integration/runtime remain held.
