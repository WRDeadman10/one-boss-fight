# AG20: Synthetic Adversarial Evidence-Case Corpus Report (Offline Design Fixture)

**Document Version:** 1.0.0  
**Date:** 2026-10-27  
**Author:** Antigravity (Pair Programmer)  
**Governing Acceptance / Directives:** `Docs/BossCombatReview/Execution/Codex/AG19_A152_ACCEPTANCE.md` / Mailbox `[X-229]`  
**Status:** DESIGN ONLY — Pure Offline Fixture & Analysis (Zero edits to `Source/`, `Config/`, `Scripts/`, or Unreal assets; no UObject instantiation; Claude resting; Owner commits only)

---

## 1. Executive Summary & Context

Work Order AG19 established the orthogonal four-statement information model and candidate reconciliation logic for combat parity verification, accepted bounded in `Docs/BossCombatReview/Execution/Codex/AG19_A152_ACCEPTANCE.md` (`[X-229]`).

Work Order AG20 delivers the **Synthetic Adversarial Evidence-Case Corpus**: an offline, non-validating JSON fixture artifact designed to stress-test future reconciliation checker logic. The corpus models the smallest discriminating set of adversarial and edge-case combinations identified in AG19, ensuring that future checker implementations cannot be fooled by synthetic full-parity claims, unverified hashes, or conflated lifecycle stages.

All cases within the corpus and this report are **strictly synthetic, illustrative, and non-runtime fixtures**. No actual telemetry, live engine captures, git commits, or runtime verification claims are manufactured or implied.

---

## 2. Corpus Specification & Discriminating Test Cases

The corpus is delivered in [`Docs/BossCombatReview/Execution/Antigravity/SYNTHETIC_EVIDENCE_CASE_CORPUS.json`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/SYNTHETIC_EVIDENCE_CASE_CORPUS.json) (`17,032 bytes`, SHA256: `c0af06b942ffa62e51a44c6d3a93ad894bf84da11ed523f27b2775736bfa162a`). It contains exactly **7 discriminating cases** without arbitrary quotas or ungrounded tolerance rules:

```
[SYNTH-01: Documentary Mismatch + Unknown Readback] ──> Preserves both facts without erasure
[SYNTH-02: Assigned + Unknown Native Apply]        ──> Separates struct assignment from component application
[SYNTH-03: Static Guard Analysis vs Performed]     ──> Code path prediction != executed runtime observation
[SYNTH-04: Matching Numbers / Incomparable Target] ──> 6.0 == 6.0 rejected if channels/units differ
[SYNTH-05: Valid Syntax / Stale or Absent Digest]  ──> Syntactic URI/SHA != actual verified artifact
[SYNTH-06: False Performed / False FULL_PARITY]    ──> Premature closure rejected by Consistency Rule 1
[SYNTH-07: All-Unknown Control Baseline]           ──> Honest unmigrated baseline without dummy values
```

### Case-by-Case Breakdown

| Case Identifier | Scenario Category | Supplied Candidate Claim | Expected Checker Disposition | Why Full Closure is Unsupported |
| :--- | :--- | :--- | :--- | :--- |
| **SYNTH-01** | Documentary Mismatch + Unknown Readback | Declared: `9999.0 HP`<br>Baseline: `2000.0 HP`<br>Assigned: `2000.0`<br>Native Apply: `APPLIED`<br>Readback: `UNOBSERVED` | `evidenceCoverage: INCOMPLETE_DOCUMENTARY_ONLY`<br>`metadataComparison: MISMATCH`<br>`overallAssessment: DOCUMENTARY_DISCREPANCY` | Declared intent and extracted baseline disagree. Telemetry is unobserved. Claiming full parity would fabricate runtime evidence and erase documentary drift. |
| **SYNTH-02** | Typed Assignment Succeeded + Unknown Native Application | Declared: `0.5 HP`<br>Baseline: `2000.0 HP`<br>Assigned: `0.5`<br>Native Apply: `UNKNOWN`<br>Readback: `UNOBSERVED` | `evidenceCoverage: STAGED_PRE_EXECUTION`<br>`metadataComparison: MISMATCH`<br>`nativeApplicationDisposition: UNKNOWN`<br>`overallAssessment: UNVERIFIED_INCOMPLETE` | Struct property assignment succeeded in memory, but native adapter application was never invoked. Conflating struct assignment with native execution is invalid. |
| **SYNTH-03** | Static Guard Analysis vs Performed Observation | Declared: `0.5 HP`<br>Baseline: `2000.0 HP`<br>Assigned: `0.5`<br>Native Apply: Candidate asserts `SKIPPED_OVERRIDE_GUARD` based on static analysis (`0.5 <= 1.f`)<br>Readback: `UNOBSERVED` | `evidenceCoverage: STAGED_HYPOTHETICAL_ONLY`<br>`nativeApplicationDisposition: SKIPPED_OVERRIDE_GUARD`<br>`overallAssessment: APPLICATION_GUARD_SKIPPED` | Static guard analysis predicts code path behavior, but does not prove the actor was instantiated, hydrated, or executed. Telemetry remains unobserved. |
| **SYNTH-04** | Matching Numbers with Incomparable Channel / Units | Declared: `6.0 Seconds`<br>Baseline: `6.0` (`Attribute.PoiseRecoveryInterval`)<br>Assigned: `6.0`<br>Native Apply: `APPLIED`<br>Readback: `6.0` (`RegenDelaySeconds`)<br>Claim: `FULL_PARITY` | `evidenceCoverage: FULL_EVIDENCE_OBSERVED`<br>`metadataComparison: INCOMPARABLE_TARGET_CHANNEL`<br>`overallAssessment: TARGET_IDENTITY_DISCREPANCY` | Numeric equality (`6.0 == 6.0`) is not parity when target channels differ (pack poise recovery interval vs native tick delay). Incomparable without an approved crosswalk. |
| **SYNTH-05** | Valid Syntax with Stale or Absent Telemetry Artifact | Declared: `1.2`<br>Baseline: `1.2`<br>Assigned: `1.2`<br>Native Apply: `APPLIED`<br>Readback: `1.2`<br>Artifact: `fixture://synthetic/missing_telemetry.json`<br>Claim: `FULL_PARITY` | `evidenceCoverage: ARTIFACT_UNVERIFIED_STALE`<br>`metadataComparison: MATCH`<br>`overallAssessment: UNVERIFIED_INCOMPLETE` | Syntactically valid URI and SHA256 strings do not prove the artifact exists or was captured from a fresh binary run. Telemetry remains unverified. |
| **SYNTH-06** | False Performed Full Parity Claim | Declared: `1.2`<br>Baseline: `1.2`<br>Assigned: `1.2`<br>Native Apply: `APPLIED`<br>Readback: `UNOBSERVED`<br>Claim: `FULL_PARITY` | `evidenceCoverage: STAGED_PRE_EXECUTION`<br>`metadataComparison: MATCH`<br>`overallAssessment: REJECTED_FALSE_CLOSURE_FORCED_UNVERIFIED` | Candidate falsely claimed `FULL_PARITY` while readback is `UNOBSERVED`. Directly violates Consistency Rule 1; checker overrides claim to `UNVERIFIED_INCOMPLETE`. |
| **SYNTH-07** | Honest All-Unknown Control Baseline | All Statements (1-4): `status: "UNKNOWN"`, values `null`<br>Claim: `UNVERIFIED_INCOMPLETE` | `evidenceCoverage: UNKNOWN_INCOMPLETE`<br>`metadataComparison: UNCHECKED`<br>`overallAssessment: UNVERIFIED_INCOMPLETE` | Control baseline. Accurately represents unmigrated/unaddressed backlog items without placeholder dummy numbers or inferred configuration success. |

---

## 3. Syntax Verification Results

Standard JSON syntax verification was executed via Python standard library `json.loads` against the raw bytes of the corpus:

```powershell
python -c "import json, hashlib; path='Docs/BossCombatReview/Execution/Antigravity/SYNTHETIC_EVIDENCE_CASE_CORPUS.json'; raw=open(path, 'rb').read(); data=json.loads(raw.decode('utf-8')); print('JSON Syntax Valid. Cases parsed:', len(data['cases']), 'Bytes:', len(raw), 'SHA256:', hashlib.sha256(raw).hexdigest())"
```

**Verification Output:**
* **Status:** JSON Syntax Valid
* **Parsed Case Count:** 7 cases
* **File Size:** 17,032 bytes
* **SHA256 Checksum:** `c0af06b942ffa62e51a44c6d3a93ad894bf84da11ed523f27b2775736bfa162a`

*Narrow Verification Scope:* This result establishes strictly that the JSON artifact is well-formed according to standard JSON syntax specifications. It does **not** imply that a checker program was executed, that JSON Schema validation was performed, that external dependencies were installed, or that live combat gameplay has been validated.

---

## 4. Architectural Boundaries & Project Governance

In accordance with project rules (`RULE[c:\UnrealProject\OneBossFight\AGENTS.md]`) and governing acceptance directives (`AG19_A152_ACCEPTANCE.md`):
1. **Design Fixture Only:** The corpus and expected dispositions serve as a reference for future offline checker design. They do not constitute an approved C++ schema, runtime adapter implementation, or build gate policy.
2. **Honest Incompleteness:** No case within this corpus asserts real task closure. All 83 active review tasks maintain their required verification backlog.
3. **Zero Code or Asset Edits:** No modifications were made to `Source/`, `Config/`, `Scripts/`, or Unreal assets.
4. **Zero Engine Execution:** No Unreal Editor, PIE, build, packaging, or `UnrealPak` commands were executed.
5. **Team Protocol:** Claude remains resting. The owner retains sole commit authority.

---

## 5. Input Artifact Receipts & Verifications

The analysis in this report was conducted strictly offline against the following pinned codebase artifacts:

| Artifact Path | Size (Bytes) | SHA256 Checksum |
| :--- | :--- | :--- |
| `Source/OneBossFight/Player/RPGEncounterBinding.h` | 7,338 | `4330f8c416cd75284e829856b5d1cba7001c5ee62f40bdc7b1bf98a8dbf94a80` |
| `Source/OneBossFight/Player/RPGEncounterBinding.cpp` | 14,964 | `2fe63bcb78261b9bdd15be33607ea3c696ae33227989facc5b67e15cd91110dc` |
| `Source/OneBossFight/Player/RPGBossPhases.h` | 8,607 | `0887f37564a28564261b81ad21a1baf2a4c6f6adae99a3a49c3c15622225a69a` |
| `Source/OneBossFight/Player/RPGBossPhases.cpp` | 21,965 | `c43615412e1f345d6ed75cc6d6a6b0d9ece6acaaac612e545b42cc24087f7a06` |
| `Source/OneBossFight/Player/RPGBossPosture.h` | 7,551 | `bca70f5816a45733f0ea2d5550651da7192ba179a5e31d736eab90fd46cd3ff8` |
| `Source/OneBossFight/Player/RPGBossEncounter.h` | 5,359 | `4f3ab203562ef2d3a2d18828feaf5f437a5a7eaff1054e9b6ce60e9150cae9d6` |
| `Source/OneBossFight/Player/RPGBossEncounter.cpp` | 12,526 | `dc149393f2fff1788ea22daf42db0b14f85ac36f58ad59c459b44ee94600c96d` |
| `Docs/BossCombatReview/Execution/Codex/Step2Preparation/02_ADAPTER_FIELD_AUDIT.md` | 14,623 | `ec676909bc43c13b19314a18aae834265044361b571f9137b3b1e1c436d1bd20` |
| `Docs/BossCombatReview/Execution/Codex/Step2Preparation/09_FIRST_CLUSTER_TYPED_PARITY_CROSSWALK.md` | 9,936 | `13b747fdcfba9951af5a0062e46499cd037d821aed94ac9e7e60eb1dcc03fd13` |
| `Docs/BossCombatReview/Execution/Codex/Step2Preparation/18_NATIVE_CAPABILITY_PROPOSAL.md` | 8,066 | `5f5b4a029f55a145f76d67796c53928944a975b6714a82a5c2bc5078753a3be1` |
| `Docs/BossCombatReview/Execution/Codex/AG18_A148_ACCEPTANCE.md` | 5,773 | `c042ead91284dcba4fc43fde9f46472ee02cfb4d3c46f7c8e15ebdf05b8a17e4` |
| `Docs/BossCombatReview/Execution/Codex/AG19_A149_REVIEW.md` | 7,531 | `689a4b42ec5c8048cf052cbda8db54abe975b1505538ac5d363dd6bcb3b65ef7` |
| `Docs/BossCombatReview/Execution/Codex/AG19_A150_REVIEW.md` | 4,889 | `63776bd64d635af238430b0b1e5c6909d7c7f9638cc7b0071f0f851161303f95` |
| `Docs/BossCombatReview/Execution/Codex/AG19_A151_REVIEW.md` | 2,660 | `bc3b883393f0616af9dcf2af8b84b5d77d86dc52d0c9ae7e2e8aed6d8be8dece` |
| `Docs/BossCombatReview/Execution/Codex/AG19_A152_ACCEPTANCE.md` | 5,419 | `d9c72377a3c6ccb0f78a347cf3e17449732b228fa2a252b68391fff3b8a94585` |
| `Docs/BossCombatReview/Execution/Antigravity/DATA_AUTHORITY_EVIDENCE_RECORD_OPTIONS.md` [Rev 04] | 33,683 | `15fe22e474eea1ced25fef507394925635c2cc4d0780beea326a1d4bd1f35cdd` |
| `Docs/BossCombatReview/Execution/Antigravity/SYNTHETIC_EVIDENCE_CASE_CORPUS.json` | 17,032 | `c0af06b942ffa62e51a44c6d3a93ad894bf84da11ed523f27b2775736bfa162a` |
