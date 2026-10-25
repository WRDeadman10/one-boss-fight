# P0 Evidence: Weapon & Trace Geometric Alignment

Date: 2026-10-25 (Revision 05)
Investigator: Antigravity (Accountable Visual Investigator)
Review Requested from: Claude (Acting Technical Lead)
Reference Tasks: U04, U05, U10, BOSS-HIT-001, BOSS-HIT-002, BOSS-HIT-003
Reproducibility: Script extract_baseline_kinematics.py -> Log raw_kinematic_extraction.log

---

## 1. Static Mesh Offline Geometric Comparison

Measurements extracted directly via headless Blender 5.1.2 from FBX source geometry:
- Tool: Blender 5.1.2 (headless) | Scene Units: Metric (1.0 scale, meters)
- Coordinate System: Blender Right-Handed (Z-Up, Y-Forward, X-Right)
- Bound Box Computation: Object bound_box transformed by matrix_world gives world-space axis-aligned extents in meters, scaled by 100 to report in centimeters. For un-parented meshes at origin with identity object transform, world bounds coincide with mesh local extents.

| Metric | Hidden Leader Reference Mesh (SM_KwangSword.fbx) | Visible Follower Project Mesh (SM_Boss01_Greatsword.fbx) | Offline Difference |
|---|---|---|---|
| File Path | Import/ThirdParty/Reference/SM_KwangSword.fbx | Import/Boss01/Weapons/SM_Boss01_Greatsword.fbx | Reference vs Project Asset |
| SHA-256 Hash | c25846828a7c47e507c861943a109be8fb995158cf0de374f99b6949e3109a7b | f61ea86f0e8d90bf702d73b2f9bb4d77139ab7340fb8f59d2e89fe895f049307 | Verifiable on disk |
| Byte Size | 348,080 bytes | 35,996 bytes | Optimized mesh |
| Vertices / Polygons | 2,028 verts / 4,018 polys | 541 verts / 569 polys | Follower optimized for silhouette |
| Total Length (Z) | 184.40 cm ([-41.50, +142.90] cm) | 184.63 cm ([-21.33, +163.30] cm) | +0.23 cm overall length |
| Crossguard Width (X) | 22.51 cm ([-10.56, +11.95] cm) | 62.00 cm ([-31.00, +31.00] cm) | +39.49 cm wider crossguard |
| Blade Thickness (Y) | 16.13 cm ([-8.07, +8.06] cm) | 7.64 cm ([-3.82, +3.82] cm) | -8.49 cm thinner spine |
| Hilt Range below Origin (Z<0) | -41.50 cm to 0.00 cm (long 2H grip) | -21.33 cm to 0.00 cm (compact grip) | Pommel is 20.17 cm higher |
| Blade Reach above Origin (Z>0) | 0.00 cm to +142.90 cm | 0.00 cm to +163.30 cm | Physical tip extends +20.40 cm further |
| Attachment Sockets on Mesh | None exported in FBX reference | Exported Empties: BladeStart (15 cm), MiddleSocket (78 cm), BladeEnd (140 cm), Weapon End (142 cm) | Empties on visible cosmetic mesh |

---

## 2. Collision Trace Authority vs Cosmetic Follower

In the project architecture (RPGBossLook.cpp), the hidden leader pack mesh drives combat queries via the pack weapon component, while the player sees SM_Boss01_Greatsword attached to SK_Boss01_Body via HeavySwordSocket_R with NoCollision.

### Provenance & Boundaries (Per Technical Reviews):
1. **Cosmetic Mesh Sockets:** The sockets BladeStart (15 cm), MiddleSocket (78 cm), BladeEnd (140 cm), and Weapon End (142 cm) are authored empties on SM_Boss01_Greatsword.fbx. Because SM_Boss01_Greatsword has NoCollision and is not the pack trace target, adding or altering sockets on this visible static mesh does NOT change gameplay collision.
2. **Production Query Sockets:** The production trace query reads Current Collision Mesh, CollisionSockets, and CollisionRadius from the live pack FTarget object at runtime (RPGPackTrace::FTarget::GetMesh / GetSockets).
3. **Geometric Fact & Exact Terminal Offsets:**
   - The physical blade tip vertex of SM_Boss01_Greatsword.fbx extends to Z = +163.30 cm (20.40 cm longer than SM_KwangSword.fbx at +142.90 cm).
   - Cosmetic empty BladeEnd (Z = +140.00 cm) sits **23.30 cm** behind the physical blade tip (+163.30 cm).
   - Cosmetic empty Weapon End (Z = +142.00 cm) sits **21.30 cm** behind the physical blade tip (+163.30 cm).
   - Sockets must not be conflated with the tip, nor should a single offset be applied to both.
4. **Runtime Limitation:** Whether the live pack trace threat volume corresponds accurately to the visible blade in world space remains **UNVERIFIED / BLOCKED pending Claude runtime query capture** of the active FTarget mesh, socket world locations, and query radius.
