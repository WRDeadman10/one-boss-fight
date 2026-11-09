"""Inspect the exact socket transforms of SK_Boss01_Body and SK_Boss01_Crown in engine (C-1172).

Logs:
1. HeavySwordSocket_R on SK_Boss01_Body and its skeleton: bone, relative_location, relative_rotation, relative_scale
2. headSocket / crown attach points on SK_Boss01_Body and its skeleton
3. Hand bone hand_r vs grip socket in idle pose
"""
import unreal

log = lambda m: unreal.log(f"[InspectAttach] {m}")

def inspect():
    body = unreal.load_asset("/Game/OneBossFight/Boss01/Body/SK_Boss01_Body")
    if not body:
        log("ERROR: Failed to load SK_Boss01_Body")
        return

    skel = body.get_editor_property("skeleton")
    log(f"Body: {body.get_name()}, Skeleton: {skel.get_name() if skel else 'None'}")

    for owner, label in ((body, "mesh"), (skel, "skeleton")):
        if not owner: continue
        log(f"--- Sockets on {label} ---")
        try:
            num = owner.num_sockets()
            for i in range(num):
                s = owner.get_socket_by_index(i)
                sname = str(s.get_editor_property("socket_name"))
                bname = str(s.get_editor_property("bone_name"))
                loc = s.get_editor_property("relative_location")
                rot = s.get_editor_property("relative_rotation")
                scale = s.get_editor_property("relative_scale")
                if any(k in sname.lower() for k in ("sword", "weapon", "hand", "crown", "head")):
                    log(f"  [{label}] {sname} on bone '{bname}': loc=({loc.x:.4f}, {loc.y:.4f}, {loc.z:.4f}), rot=(p={rot.pitch:.4f}, y={rot.yaw:.4f}, r={rot.roll:.4f}), scale=({scale.x:.4f}, {scale.y:.4f}, {scale.z:.4f})")
        except Exception as e:
            log(f"Error enumerating {label} sockets: {e}")

    # Inspect Crown mesh bounds & sockets
    crown = unreal.load_asset("/Game/OneBossFight/Boss01/Body/SK_Boss01_Crown")
    if crown:
        cb = crown.get_bounds()
        log(f"Crown bounds: origin=({cb.origin.x:.2f}, {cb.origin.y:.2f}, {cb.origin.z:.2f}), extent=({cb.box_extent.x:.2f}, {cb.box_extent.y:.2f}, {cb.box_extent.z:.2f})")
        log(f"Crown sockets ({crown.num_sockets()}): {[str(crown.get_socket_by_index(i).get_editor_property('socket_name')) for i in range(crown.num_sockets())]}")

if __name__ == "__main__":
    inspect()
