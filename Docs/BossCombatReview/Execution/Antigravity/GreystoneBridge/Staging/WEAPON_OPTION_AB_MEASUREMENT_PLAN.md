# Weapon Bridge Architecture: Option A vs Option B Measurement Plan (A-255)

> **Document Status**: Staged Architecture & Verification Plan  
> **Target Subsystem**: `URPGGreystoneVisualBridgeSubsystem` / `URPGGreystoneVisualBridgeComponent`  
> **Location**: `Docs/BossCombatReview/Execution/Antigravity/GreystoneBridge/Staging/`  
> **Reviewers**: Implementer (Claude) & Owner

---

## 1. Problem Formulation & Governance Context

In the Advanced ARPG Combat pack, player melee attacks execute weapon collision sweeps using `UTraceComponent` referencing sockets located on the equipped weapon mesh (`BP_BaseWeapon` / `BP_Weapon_Master`).

When Paragon Greystone is introduced via our runtime retarget bridge:
- **Option A (Reattach Pack Weapon to Greystone)**:  
  The pack weapon actor is re-parented to Greystone's visual hand socket.  
  *Consequence:* The weapon traces follow Greystone's retargeted skeletal pose. Because Greystone's limb proportions differ from `SK_CombatMannequin`, this represents a **gameplay change** (altering player hit reach, arc timing, and hit-box registration vs Sevarog).
- **Option B (Weapon Stays on Hidden Mannequin + Visual Proxy on Greystone)**:  
  The real pack weapon actor remains attached to the hidden mannequin (which ticks and refreshes bones every frame), executing the exact baseline gameplay traces. A visual-only cosmetic weapon mesh is attached to Greystone.  
  *Consequence:* **100% gameplay and balance parity** with the pack baseline is guaranteed.

Per lead directive C-385, Option A must be measured against the baseline mannequin traces. If Option A introduces measurable balance deviations beyond tolerance, Option B is the mandated fallback.

---

## 2. Dynamic Socket Resolution Architecture

The weapon bridge must **not** assume a hardcoded socket name such as `"hand_r"`.

### 2.1 Inspection Hierarchy
As implemented in `URPGGreystoneVisualBridgeComponent::ResolvePackWeaponSocketName()`:
1. **Dynamic Child Inspection**: Inspects all active attachment children of `MannequinMeshComponent`.
2. **Actor Identification**: Identifies child components owned by external weapon actors (`BP_BaseWeapon`).
3. **Socket Extraction**: Queries `Child->GetAttachSocketName()`.
4. **Pack Socket Fallbacks**: If unattached at initialization, checks standard pack socket identifiers:
   - `WeaponSocket_R` (primary 1-handed sword socket in `SK_CombatMannequin`)
   - `SnS_Socket` (sword-and-shield weapon socket)
   - `HeavySwordSocket` (2-handed weapon socket)

---

## 3. Quantitative Measurement Methodology

To arbitrate between Option A and Option B, the implementer will execute a dedicated automated PIE telemetry driver evaluating the primary player attack (`Attack_PrimaryA_Anim`):

```text
Baseline (Pure Mannequin) <---- Compare ----> Option A (Greystone Re-Attachment)
```

### 3.1 Measured Metrics
1. **Maximum Forward Reach ($R_{\max}$)**:  
   The furthest forward component-space distance ($+X$ in character forward orientation) reached by the weapon tip socket (`WeaponEndSocket` / `root_weapon_end_r`) during the active swing window.
2. **First Contact Timestamp ($t_{\text{hit}}$)**:  
   The simulation time (in seconds and frame index) when the swept trace first intersects Sevarog's capsule collision at a fixed baseline separation ($180\text{ cm}$).
3. **Swept Arc Lateral Width ($W_{\text{arc}}$)**:  
   The total lateral envelope ($\Delta Y$) swept by the weapon trace line between swing start and recovery.
4. **Damage Registration Parity**:  
   Boolean confirmation that identical inputs produce identical hit/whiff results against stationary target dummies.

---

## 4. Arbitration & Disqualification Thresholds

Option A is evaluated against the following strict tolerance gates:

| Metric | Permitted Tolerance | Disqualification Condition | Fallback Action |
| :--- | :---: | :--- | :--- |
| **Reach Delta ($|\Delta R_{\max}|$)** | $\le 5.0\text{ cm}$ | $|\Delta R_{\max}| > 5.0\text{ cm}$ (excessive reach advantage or handicap) | Disqualify Option A $\to$ Adopt Option B |
| **Hit Timing Delta ($|\Delta t_{\text{hit}}|$)** | $\le 16.67\text{ ms}$ | $|\Delta t_{\text{hit}}| > 1\text{ frame at 60 FPS}$ (noticeable delay or advance) | Disqualify Option A $\to$ Adopt Option B |
| **Swept Arc Width Delta ($|\Delta W_{\text{arc}}|$)** | $\le 10.0\text{ cm}$ | $|\Delta W_{\text{arc}}| > 10.0\text{ cm}$ (distorted hit coverage) | Disqualify Option A $\to$ Adopt Option B |
| **Hit Outcome Parity** | $100\%$ Match | Any case where baseline hits but Option A misses (or vice versa) | Disqualify Option A $\to$ Adopt Option B |

---

## 5. Implementation Recommendation

- **Staged Default**: `URPGGreystoneVisualBridgeComponent` defaults to `OptionB_VisualProxyWeaponOnGreystone`.
- **Measurement Harness**: The implementer enables `OptionA_ReattachPackWeaponToGreystone` via test commandline (`-VisualBridgeWeapon=OptionA`) during the Greystone lane verification run to log the telemetry deltas.
- **Production Decision**: If all 4 metrics pass within tolerance, Option A may be approved by the lead to eliminate the need for a cosmetic proxy actor. Otherwise, Option B remains active, guaranteeing zero gameplay impact.
