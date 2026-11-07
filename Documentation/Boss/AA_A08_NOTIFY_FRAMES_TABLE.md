# AA-A08: Elden Ring Animation Clip Notify Frames Table

Author: Antigravity  
Status: COMPLETE  
Cross-Reference: Codex `Documentation/Boss/AA_C11_C14_ER_CLIP_WIRING_READINESS.md`, Spec `Documentation/Boss/ER_PLAYER_CONTROLS_SPEC.md`  
Target Skeleton: `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin`  

---

## 1. Overview & Code Notify Alignment

This document maps each delivered Elden Ring player animation clip to the exact frame numbers, timestamps (@ 30 fps), and expected gameplay notify events matching the Advanced ARPG Combat and OneBossFight native code contracts (`URPGDodgeTiming`, `RPGFrameworkMoveExecutor`, `FallingAttackMontages`, `air_heavy_selector.py`).

---

## 2. Comprehensive Clip Notify Table

| Clip ID | Clip / Montage Name | Frame (30 fps) | Time (s) | Code Notify Name | Pack / Engine Event Class | Gameplay Effect & State Contract |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ER-A1** | `AN_ER_Backstep_Back` | F0 | 0.000 s | `Montage_Start` | Native Montage Hook | Root motion starts backward (-Y 200 cm), Yaw strictly locked at 0.0°. |
| | | **F2** | **0.067 s** | `IFrame_Start` | `UAnimNotify_IFrame` | Grants invulnerability frames (matches Elden Ring backstep startup). |
| | | **F8** | **0.267 s** | `IFrame_End` | `UAnimNotify_IFrame` | Invulnerability window expires. |
| | | **F8** | **0.267 s** | `InputBuffer_Open` | `UAnimNotify_InputBuffer` | Early input queueing opens for follow-up moves (e.g. backstep attack). |
| | | **F14** | **0.467 s** | `Recover_End` | `UAnimNotify_Recover` | Backstep ends cleanly into combat idle stance. |
| **ER-A4** | `AN_ER_Attack_GuardCounter` | F0 | 0.000 s | `Montage_Start` | Native Montage Hook | Initiates forward lunge (+Y 100 cm) from shield guard pose. |
| | | **F9** | **0.300 s** | `Windup_End` | Native Event | Windup finishes; anticipation apex. |
| | | **F10** | **0.333 s** | `WeaponTrace_Start` | `UAnimNotifyState_WeaponTrace` | Weapon collision trace activates; active damage window opens. |
| | | **F13** | **0.433 s** | `Impact_Peak` | `UAnimNotify_PlaySound` / CamShake | Peak hit contact point, triggers impact audio, spark, and high poise-damage delivery. |
| | | **F16** | **0.533 s** | `WeaponTrace_End` | `UAnimNotifyState_WeaponTrace` | Weapon collision trace deactivates; hit window closes. |
| | | **F18** | **0.600 s** | `InputBuffer_Open` | `UAnimNotify_InputBuffer` | Allows buffering dodge or follow-up attack. |
| | | **F24** | **0.800 s** | `Recover_End` | Native Montage End | Counter-slash recovery ends; returns to combat idle. |
| **ER-A3** | `AN_ER_Attack_Air_Heavy_Plunge` | F0 | 0.000 s | `Montage_Start` | Native Montage Hook | In-place airborne plunge initiated; two-handed sword lift. |
| | | **F6** | **0.200 s** | `Airborne_Windup_End`| Native Event | Apex overhead sword lift completes; downward plunge accelerates. |
| | | **F11** | **0.367 s** | `WeaponTrace_Start` | `UAnimNotifyState_WeaponTrace` | Vertical slash hitbox opens while descending. |
| | | **F15** | **0.500 s** | `Ground_Impact` | `UAnimNotify_CameraShake` / VFX | Character contacts ground; deep knee crouch slam; triggers ground dust/shockwave VFX. |
| | | **F16** | **0.533 s** | `WeaponTrace_End` | `UAnimNotifyState_WeaponTrace` | Active hit trace concludes. |
| | | **F18** | **0.600 s** | `InputBuffer_Open` | `UAnimNotify_InputBuffer` | Input buffering opens during squat rebound. |
| | | **F26** | **0.867 s** | `Recover_End` | Native Montage End | Plunge recovery concludes; smooth return to ground combat idle. |
| **ER-A2** | `AN_ER_Attack_Air_Light` | F0 | 0.000 s | `Montage_Start` | Native Montage Hook | In-place jump light attack; upper body coils right. |
| | | **F4** | **0.133 s** | `Airborne_Windup_End`| Native Event | Windup finishes; diagonal slash begins. |
| | | **F6** | **0.200 s** | `WeaponTrace_Start` | `UAnimNotifyState_WeaponTrace` | Diagonal swipe hitbox activates. |
| | | **F7** | **0.233 s** | `Impact_Peak` | Audio / Impact Notify | Peak slash arc across chest plane. |
| | | **F10** | **0.333 s** | `WeaponTrace_End` | `UAnimNotifyState_WeaponTrace` | Weapon hitbox trace closes. |
| | | **F12** | **0.400 s** | `InputBuffer_Open` | `UAnimNotify_InputBuffer` | Input buffer opens; flows into fall loop or ground landing. |
| | | **F17** | **0.567 s** | `Recover_End` | Native Montage End | Airborne slash recovers to jump falling cycle. |

---

## 3. Integration & Fallback Guarantees

1. **Root Motion Isolation:**
   - `AN_ER_Backstep_Back`: 200 cm along -Y in Unreal space.
   - `AN_ER_Attack_GuardCounter`: 100 cm along +Y in Unreal space.
   - Air attacks (`AN_ER_Attack_Air_Heavy_Plunge`, `AN_ER_Attack_Air_Light`): Zero root translation; movement driven entirely by player jump trajectory and Unreal gravity.
2. **Optional Montage Fields:**
   - In accordance with Codex's `AA-C11..C14`, all montages remain optional `TSoftObjectPtr<UAnimMontage>` fields. If unassigned or failing load, the character automatically falls back to current baseline behaviors (directional roll for dodge, default jump attacks).
