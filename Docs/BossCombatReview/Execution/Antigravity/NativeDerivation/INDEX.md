# Native Derivation Dossier: Index & Delivery Manifest

## 1. Overview
This dossier provides the definitive offline native derivation for the five boss components that do not yet have a typed profile or authoring schema in the project toolkit (`RPGBossShockwave`, `RPGBossHealPunish`, `RPGBossDeath`, `RPGBossLook`, `RPGBossCloseClipSwap`).

Authored strictly from real engine C++ source files in `Source/OneBossFight/Player/` under order `AG-CONTENT06` (from `[C-261]`), this documentation equips Codex to author subsequent DD packages (DD21 through DD25) deterministically without re-reading or reverse-engineering C++ component source code.

---

## 2. Component Synthesis & Summary Table

| Component | Authored Fields | Soft Paths | Key Dependencies | Recommended DD | 1-Line Risk Summary |
|---|---|---|---|---|---|
| `RPGBossShockwave` | 8 | 0 | `URPGAttackTracker` (Move A6), `URPGBossEncounter`, `URPGDamageResolver` | **DD21** | Lowest risk; purely numeric relational invariants (`StartRadius < MaxRadius`, `JumpClearance > 0`), zero soft paths, zero memory mutation. |
| `RPGBossHealPunish` | 14 | 0 (hardcoded cpp) | `URPGAttackTracker` (Move A5), `ARPGBossJavelin`, `URPGBossEncounter`, hardcoded `DrinkingPotion_Montage` | **DD22** | Low-to-moderate risk; numeric multi-bound clamps (`MinRange < MaxRange`, `MinSpeed <= MaxSpeed`, `FlightTime >= 0.05`), plus mesh socket array. |
| `RPGBossLook` | 5 | 5 (1 body, 3 pieces, 1 sword) | Owner character leader mesh, attached weapon static meshes (`Contains("Weapon")`) | **DD23** | Moderate risk; requires validating array of soft object paths (`TArray<TSoftObjectPtr<USkeletalMesh>>`) and handling follower component attachment lifecycle. |
| `RPGBossCloseClipSwap` | 5 | 3 (A1, A3a, A3b) | `GA_GS_Boss_CloseAttack_C`, `URPGBossEncounter`, `URPGBossDeath`, `RPGBossCloseClipSwapRules.h` | **DD24** | High risk; mutates live GameplayAbility memory in-place via reflection; failing to match all 3 pack montages triggers permanent fallback (`bPermanentFailure`). |
| `RPGBossDeath` | 12 | 2 (DeathClip, DeathMontage) | `GA_EnemyRagdollDeath_C`, `URPGBossStagger/Posture/Phases`, `ARPGBossRemains`, `RPGBossClips` | **DD25** | Highest risk; dual execution modes (`PackMontage` vs `OwnClip`), suppression of pack ragdoll physics simulation, and tight coordination with death actor destruction (`KI-083`). |

---

## 3. Recommended Delivery Order (DD21 .. DD25)

1. **DD21: `RPGBossShockwave`**
   - *Rationale:* Zero soft paths, zero reflection, zero runtime component spawning. Pure numerical configuration (`Damage`, `StartRadius`, `MaxRadius`, `Speed`, `Thickness`, `JumpClearance`, `MoveId`). Validates relational ordering (`StartRadius < MaxRadius`, `JumpClearance > 0`) using standard float32 normalization.
   - *One-Line Risk:* Zero-risk arithmetic profile; wrong bounds cause immediate wave termination or un-jumpable damage bands.

2. **DD22: `RPGBossHealPunish`**
   - *Rationale:* Expands the numeric domain to include socket lists (`TArray<FName> SpawnSockets`) and velocity clamps. The player potion montage is hardcoded in C++, so the profile remains purely scalar/symbolic.
   - *One-Line Risk:* Inverting `MinRange`/`MaxRange` or `MinSpeed`/`MaxSpeed` silences heal punish entirely or triggers undefined clamp behavior.

3. **DD23: `RPGBossLook`**
   - *Rationale:* Introduces soft path validation for meshes: 1 skeletal mesh, 1 static mesh, and 1 array of skeletal meshes (`Pieces`). Clean component lifecycle (`PrimaryComponentTick.bCanEverTick = false`) with clear separation of visual followers and leader physics.
   - *One-Line Risk:* Missed soft paths or invalid socket names fall back to Kwang mesh or hand bone without crashing, but profile authoring helper must support array-of-soft-paths serialization.

4. **DD24: `RPGBossCloseClipSwap`**
   - *Rationale:* Introduces live GameplayAbility memory mutation via reflection. The profile specifies 3 soft montage paths, but runtime application is strictly governed by `RPGBossCloseClipSwapRules.h` requiring exactly 4 pack entries and 3 matching candidate names.
   - *One-Line Risk:* In-memory ability array surgery permanently disables authored attack clips on any montage mismatch.

5. **DD25: `RPGBossDeath`**
   - *Rationale:* The most architecturally intricate component in the boss fight. Handles dual presentation modes (`PackMontage` reflection injection vs `OwnClip` custom clip pause & ragdoll suppression), tick ordering prerequisites (`Stagger`, `Posture`, `Phases`), and static remains spawning (`ARPGBossRemains`).
   - *One-Line Risk:* Dual-mode branching and physics suppression timing directly impact boss destruction flow and end-of-combat victory stability (`KI-083`).

---

## 4. Dossier File Manifest
All dossiers are located in `Docs/BossCombatReview/Execution/Antigravity/NativeDerivation/`:

- `RPGBossShockwave.md`: Full derivation for `URPGBossShockwave` (8 authored fields, code reads, extremes, dependencies, domain, lifecycle).
- `RPGBossHealPunish.md`: Full derivation for `URPGBossHealPunish` (14 authored fields, code reads, extremes, dependencies, domain, lifecycle).
- `HealPunish_domain_proposal.md`: Proposal sheet for `URPGBossHealPunish` (DD22 contract proposal).
- `RPGBossDeath.md`: Full derivation for `URPGBossDeath` (12 authored fields, code reads, extremes, dependencies, domain, lifecycle).
- `RPGBossDeath_domain_proposal.md`: Proposal sheet for `URPGBossDeath` (DD25 contract proposal, revised per C-274; v1 preserved under `original_A192/`).
- `RPGBossLook.md`: Full derivation for `URPGBossLook` (5 authored fields, code reads, extremes, dependencies, domain, lifecycle).
- `RPGBossLook_domain_proposal.md`: Proposal sheet for `URPGBossLook` (DD23 contract proposal).
- `RPGBossCloseClipSwap.md`: Full derivation for `URPGBossCloseClipSwap` (5 authored fields, rules header, code reads, extremes, dependencies, domain, lifecycle).
- `RPGBossCloseClipSwap_domain_proposal.md`: Proposal sheet for `URPGBossCloseClipSwap` (DD24 contract proposal).
- `INDEX.md`: Synthesis, summary matrix, and DD21-DD25 sequencing rationale.
- `evidence_sha256.txt`: Cryptographic receipt for all dossier markdown files.
