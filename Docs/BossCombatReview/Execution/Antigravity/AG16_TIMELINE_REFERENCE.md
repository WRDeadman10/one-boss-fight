# AG-16: Offline Reference Implementation of the Timeline Compiler (Revision 04)

**Document ID:** `AG16_TIMELINE_REFERENCE`  
**Revision:** Rev 04 (Updated per Claude `[C-147]` and Codex `[X-136]`)  
**Author:** Antigravity (Visual & Technical Animation Investigator)  
**Parent Work Order:** `ANTIGRAVITY_WORK_ORDER_04.md` (`AG-16`, `AG-20`, `AG-24`)  
**Reference Implementations:**  
- Script: [`Docs/BossCombatReview/Execution/Antigravity/Evidence/timeline_reference.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Evidence/timeline_reference.py)  
- Expected Output: [`Docs/BossCombatReview/Execution/Antigravity/Evidence/timeline_expected.json`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Evidence/timeline_expected.json)  
**Status:** DELIVERED (Rev 04)  

---

## 1. Executive Summary & Resolution of Codex [X-125] & [X-136] Critiques

Task `AG-16` delivers an independent offline reference implementation of the timeline compiler to provide mathematical ground-truth expected values for Codex's Step 3 tests (`RPGTimelineCompiler`, `RPGShadowCompare`).

### 1.1 Resolution of Codex [X-136] Critiques (Rev 04)
In `[X-136]`, Codex Astra identified two boundary vulnerabilities in Revision 03's `evaluate_crossing`:
1. **IEEE 754 Non-Finite Position Guard (`math.isfinite`):**  
   In Python and C++, any relational comparison with `float('nan')` evaluates to `False` (`float('nan') < 0.0` is `False`, `float('nan') > length` is `False`). Consequently, a `NaN` position slipped through the bounds checks and returned `MATCH`.  
   *Remediation in Rev 04:* Added an explicit `math.isfinite(prev_s) and math.isfinite(curr_s)` check at the very entry of `evaluate_crossing`. Non-finite values (`NaN`, `+Inf`, `-Inf`) immediately return `{"status": "INCONCLUSIVE", "reason": "Non-finite position detected (NaN or Inf): ...", "crossings": []}`.
2. **Full Declared-Wrap Handling for `ForwardLoop`:**  
   In Rev 03, the loop wrap branch required `loop_ordinal == prev_loop_ordinal + 1 and curr_s < prev_s`. When traversing a forward loop where `curr_s >= prev_s` (for example advancing from $0.1\text{ s}$ to $0.2\text{ s}$ across loop boundary $0 \to 1$), the condition failed, falling through and returning empty crossings.  
   *Remediation in Rev 04:* Whenever `traversal == "ForwardLoop"` (or `loop_ordinal == prev_loop_ordinal + 1`), the compiler evaluates the full wrap across interval A $(prev\_s, Length]$ on loop $N$ and interval B $[0.0, curr\_s]$ on loop $N+1$, independent of whether `curr_s < prev_s` or `curr_s >= prev_s`.
3. **Live Text Export Hash Pinning:**  
   Corrected the live raw export digest in the provenance table from the historical Rev 02/03 hash (`c72b2c93...`) to the current repository hash `950c611ee5eae7bcdd7abca1ea56c051c3b42d988b427cf64452829142ab0b31`.

### 1.2 Plain Correction of Prior Inaccurate Claims in Rev 02 (A-70 / X-125)
1. **Montage-Level Payload Digest:** Rev 02 only attached `payload_hash` to individual windows and markers; montage dictionary omitted `payload_sha256`. Remediated in Rev 03 with verified 64-character hex `payload_sha256`.
2. **SectionJump Traversal Leak:** Remediated in Rev 03; non-forward traversal strictly returns `INCONCLUSIVE`.
3. **Out-of-Bounds Evaluation Leak:** Remediated in Rev 03; out-of-bounds positions strictly return `INCONCLUSIVE`.
4. **Scope Transparency of Text Export Hashes:** Windows/markers explicitly declare `payload_scope = "TEXT_EXPORT_CLASS_AND_INTERVAL_ONLY"`, and topology declares `UNVERIFIED_IN_TEXT_EXPORT`.

---

## 2. Input Provenance & Cryptographic Hashes

Every input file consumed by the reference compiler is verified and cryptographically pinned:

| Input File | Category | SHA-256 Digest |
| :--- | :--- | :--- |
| `Claude/Evidence/exports/montage_notifies_2026-10-25.txt` | Live Engine Export (Current) | `950c611ee5eae7bcdd7abca1ea56c051c3b42d988b427cf64452829142ab0b31` |
| *(Historical Rev 02/03 pre-normalization hash)* | *Historical Reference* | `c72b2c938b8aa8cfbe5be089a8449079df9269d03c6218d3c50fe3fa752763fc` |
| `movesheets/AN_Boss01_A1_QuickSlash.json` | Project Movesheet | `86cae7502caee1ce9629194ec8fe7eaef566060c23985fe66b720b0c2794eb09` |
| `movesheets/AN_Boss01_A2_ApexHold.json` | Project Movesheet | `76d9e030b6e3f458e0a811a2f647c0bc789f7142436d4df572886f69ae83fbb8` |
| `movesheets/AN_Boss01_A2_Raise.json` | Project Movesheet | `b46c650fa4644eb987545939ca5a09b30c45aa7e6e584a20b0805562130ff387` |
| `movesheets/AN_Boss01_A2_Slam.json` | Project Movesheet | `92dc75ea5dcdd4b8e5c544d67894a73f8b0568fcfe2fe31e9a7e6b001a1c9772` |
| `movesheets/AN_Boss01_A3a_Combo1.json` | Project Movesheet | `4fa89a263ca93652c713fb9ef6a18d184cf438787f97eead9aeae37905d6cbbf` |
| `movesheets/AN_Boss01_A3b_Combo2.json` | Project Movesheet | `6747d8ffb265ecb909015949d854cfce396d11b51fc36ce44062884a44fb8477` |
| `movesheets/AN_Boss01_A4_LowSweep.json` | Project Movesheet | `784d1bc96df8f7957ff987d6cf628bb9c922a573ae0f9d96c97ec59b581e1fe3` |
| `movesheets/AN_Boss01_A5_JavelinThrow.json`| Project Movesheet | `1fe8d249fbf1fc62aa53bb401ee0a82705b7661b0c0a87679803df6dc5397441` |
| `movesheets/AN_Boss01_DeathLegend.json` | Project Movesheet | `d7e97ca80fa9e8ceea3dfd6f1a8c04e223b246aa1d62489f664b321c1a965709` |
| `movesheets/AN_Boss01_DormantIdle.json` | Project Movesheet | `11181829f7988362637021eb31a5905d52fc3f86e92ba5716dfd08c87cc3e8f4` |
| `movesheets/AN_Boss01_PhaseRoar.json` | Project Movesheet | `321b1940989f688001150033d59648a3cf8d940c83a0058ec12f7a9ddab09e17` |
| `movesheets/AN_Boss01_StaggerDown.json` | Project Movesheet | `bb8ffc99bead1ea67851d7c4dbbe0f6a27e799276ea9f13013d508269e80a0aa` |
| `movesheets/AN_Boss01_StaggerFall.json` | Project Movesheet | `88c9df4f71fb3d5aee202f5e7f1cae79f61b0f0a52df710c59e742e4726dcff5` |
| `movesheets/AN_Boss01_StaggerGetUp.json` | Project Movesheet | `9c43d78da4b462bf4ea6717eb481ec5fb6cb774fc710c0879555aa717e12e12e` |
| `movesheets/AN_Boss01_Wake.json` | Project Movesheet | `4f8286a1df887c7e90e72c842e4313d4b6795fbb3ca9bbab857b21235121307b` |
| `movesheets/AN_Riposte_Boss_Reaction.json`| Project Movesheet | `6f3c5f49ef63e3d6232e01691ea03ff02e07ee50d876d782163b71ca0406df66` |
| `movesheets/AN_Riposte_Player_Front.json` | Project Movesheet | `47343e740ae808aa9171f6ceb7ea7c89f257a412850935fb6f59d28bb46c4f1c` |
| `movesheets/GS_Attack01.json` | Pack Movesheet | `d720c756f70912cb8d6368d9e262176b6d510255866c2db5f76ee4ba60655d99` |
| `movesheets/GS_Attack02.json` | Pack Movesheet | `b4e64fdf66a5069f9e0f6c20fe1bc00938b813134cbff38b46e30018ceef528c` |
| `movesheets/GS_Attack03.json` | Pack Movesheet | `97d5eb270c5e317e828eeb2957422f2834b6b6ec4e0622a49aa523eb41d7cb32` |
| `movesheets/GS_Attack04.json` | Pack Movesheet | `6aa43033d59eeb6f1ec28f9d6a36cff138670bc235cf653ec8f6a9b40026e64c` |
| `movesheets/GS_ChargedAttack.json` | Pack Movesheet | `c2f34731be4d8f07297e6822fc9081e695d7bfa5e9b978939e1a14a87c126d4c` |
| `movesheets/GS_LeapAttack.json` | Pack Movesheet | `575ddf79a941571477747e152912a20fc1bfba26c91d4e73b432e65d214ee6b6` |
| `movesheets/GS_SprintAttackFollowUp.json` | Pack Movesheet | `71b2d075eb46115933eb91f5e27863102ce51908b981682782b3a16223b53f6d` |
| `movesheets/Mid01.json` | Pack Movesheet | `d8a2daae850f3408f653a9e7f4c5e3f538d38865c3e7216a9c3756317b2b512c` |
| `movesheets/RetaliationAttack.json` | Pack Movesheet | `44882ea7945d7a64ce14fbe239a51ebcbe8fa5cb884742a031a0eecf014ae9a4` |

---

## 3. Deliberate Self-Test Verification Suite (11/11 Tests)

The reference implementation executes 11 deliberate failure and boundary cases to guarantee compiler robustness against corrupted asset metadata, Codex's reversed-interval counterexample, and all issues raised in `[X-125]` and `[X-136]`:

```text
[TimelineRef] Loaded inputs. 1 export + 26 movesheets parsed.
[SelfTest] Running 11 deliberate rejection and boundary verification tests...
  Test 1 PASSED: Rejected window End <= Begin
  Test 2 PASSED: Rejected duplicate asset ID across windows
  Test 3 PASSED: Rejected negative montage length
  Test 4 PASSED: Rejected marker placed beyond montage sequence length
  Test 5 PASSED: Detected non-forward traversal ('Reverse') as INCONCLUSIVE
  Test 6 PASSED (Codex Counterexample): Rejected window with Begin (1.2s) >= Length (1.0s)
  Test 7 PASSED (Codex X-125 Critique 1): Reclassified SectionJump traversal as INCONCLUSIVE
  Test 8 PASSED (Codex X-125 Critique 2): Reclassified out-of-bounds evaluation position as INCONCLUSIVE
  Test 9 PASSED (Codex X-125 Critique 3): Verified whole-montage payload_sha256 generation (64-char hex)
  Test 10 PASSED (Codex X-136 Reproducer 1): NaN position rejected as INCONCLUSIVE
  Test 11 PASSED (Codex X-136 Reproducer 2): ForwardLoop with curr >= prev evaluated as MATCH with crossings
[SelfTest] All 11/11 deliberate verification tests PASSED successfully!

[TimelineRef] Parsed 14 montages from montage_notifies_2026-10-25.txt.
[TimelineRef] Successfully compiled 14 timelines to C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Antigravity\Evidence\timeline_expected.json
```

### 3.1 Codex Counterexample, X-125, & X-136 Additions
- **Test 6 (Codex Clamp Counterexample):** Rejects $Begin \ge Length$ before clamping can synthesize a backwards interval.
- **Test 7 (Codex Critique 1 - SectionJump):** `evaluate_crossing(compiled, 0.0, 0.9, traversal="SectionJump")` yields `INCONCLUSIVE` (`"Unsupported traversal 'SectionJump'"`).
- **Test 8 (Codex Critique 2 - Out of Bounds):** `evaluate_crossing(compiled, 0.0, 2.5, traversal="Forward")` on length $2.0\text{ s}$ yields `INCONCLUSIVE` (`"Position out of bounds: prev=0.0, curr=2.5, length=2.0"`).
- **Test 9 (Codex Critique 3 - Montage Payload SHA-256):** Verifies that `compile_montage` injects a 64-character hex string into `payload_sha256` of every compiled montage object.
- **Test 10 (Codex X-136 Reproducer 1 - NaN/Inf Finite Guard):** `evaluate_crossing(compiled, float('nan'), 0.5)` strictly yields `INCONCLUSIVE` (`"Non-finite position detected (NaN or Inf)"`).
- **Test 11 (Codex X-136 Reproducer 2 - ForwardLoop Wrap):** `evaluate_crossing(compiled, 0.1, 0.2, traversal="ForwardLoop", prev_loop_ordinal=0, loop_ordinal=1)` strictly returns `MATCH` with crossings across both loop intervals $(0.1, Length]$ and $[0.0, 0.2]$.

---

## 4. Compiled Timeline Highlights (`timeline_expected.json`)

The reference compiler processed all 14 distinct montages. Below are representative compiled timeline summaries from Revision 03:

### 4.1 `GS_ChargedAttack_Montage` (Pack A2 Baseline, 3.400s)
- **Whole-Montage Digest:** `payload_sha256 = "406d4d96b638e9e0e0b749c5935aa6d5a27c371421d5e55b06749f1b71129ef9"`
- **Section Graph:** `topology: UNVERIFIED_IN_TEXT_EXPORT`, inferred section `"Default"`, declared sections: 1.
- **Windows:**
  * `W_00_ANS_DisableMovement_C`: $[0.000\text{ s}, 3.400\text{ s}]$ (Normalized: $[0.0, 1.0]$) — *Clamped from raw 4.933s*. Scope: `TEXT_EXPORT_CLASS_AND_INTERVAL_ONLY`. Digest: `cc0c15572697ae1e519d150059af94498f7caa5e34ffc4ac7cb39cad0ef6e758` *(matches Codex C++ draft test `FRPGTimelineA2GoldenDraftTest`)*.
  * `W_01_ANS_CollisionTrace_C`: $[1.567\text{ s}, 1.760\text{ s}]$ (Normalized: $[0.460882, 0.517647]$). Digest: `c6e25f9fc8c1c2357d53f315650aa46a8a22e7f3d7010bc5ea64a0ee4cc6a375`.
  * `W_02_ANS_CollisionTrace_C`: $[1.925\text{ s}, 2.104\text{ s}]$ (Normalized: $[0.566176, 0.618824]$). Digest: `df596f6bb1fef1b43db24c0237c3871aefdd8a246a139c0935ffba352997366d`.
- **Markers:**
  * `M_00_AnimNotify_PlaySound`: $1.593\text{ s}$ (Normalized: $0.468529$).
  * `M_01_AnimNotify_PlaySound`: $1.817\text{ s}$ (Normalized: $0.534412$).

### 4.2 `AM_Boss01_A1` (Boss Quick Slash, 1.200s)
- **Whole-Montage Digest:** `payload_sha256 = "486f0aa6763ea119f429188e999c647bfae6bfbcfa04ef9a5ae31bf9caeeeb47"`
- **Section Graph:** `topology: UNVERIFIED_IN_TEXT_EXPORT`, inferred section `"Default"`, declared sections: 1.
- **Windows:**
  * `W_00_ANS_DisableMovement_C`: $[0.000\text{ s}, 0.500\text{ s}]$, Semantic: `MovementLock`.
  * `W_01_ANS_SetDesiredRotation_C`: $[0.000\text{ s}, 0.330\text{ s}]$, Semantic: `RotationTracking`.
  * `W_02_ANS_CollisionTrace_C`: $[0.350\text{ s}, 0.500\text{ s}]$, Semantic: `ActiveDamage`.
- **Markers:**
  * `M_00_AnimNotify_PlaySound`: $0.330\text{ s}$, Semantic: `AcousticCue`.

---

## 5. Evidence and Limits Table

| Topic / Requirement | Reference Script Output | Status | Offline Limit / Boundary |
| :--- | :--- | :--- | :--- |
| **Input Hashing** | `timeline_reference.py:51-64` | Verified across 27 source files | Pinned from text export and 26 movesheets. |
| **Notify & Movesheet Parsing** | `timeline_reference.py:66-146` | 14 montages + 26 movesheets parsed | Limited to text exports provided in live repo. |
| **Window Clamping Rule** | `timeline_reference.py:190-201` | Clamps $End \le Length$; rejects $Begin \ge Length$ | Pre-clamp check prevents reversed interval counterexample. |
| **Section Topology** | `timeline_reference.py:249-264` | Honest `UNVERIFIED_IN_TEXT_EXPORT` | Text export omits section track names and composite links. |
| **Payload Scope** | `timeline_reference.py:205-245` | Declares `TEXT_EXPORT_CLASS_AND_INTERVAL_ONLY` | Hashes text fields only; binary UObject data unexported. |
| **Montage Payload SHA-256** | `timeline_reference.py:277-280` | Pinned across all 14 compiled montages | Deterministic canonical JSON dictionary hash. |
| **Crossing Evaluation** | `timeline_reference.py:295-410` | Guards SectionJump, Reverse, finite check (NaN/Inf), ForwardLoop wrap, and bounds $[0, Length]$ | Non-forward or non-finite paths classified strictly as `INCONCLUSIVE`. Full wrap spans emitted on ForwardLoop. |
| **Self-Tests Passed** | `timeline_reference.py:412-520` | 11/11 verification tests passed | Verified in offline Python 3.10 runtime (incorporating Codex X-125 and X-136 reproducers). |
