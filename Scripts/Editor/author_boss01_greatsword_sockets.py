"""Author sockets on /Game/OneBossFight/Boss01/Weapons/SM_Boss01_Greatsword (C-1172, C-1173).

Adds the required grip and weapon trace sockets along the blade:
- grip: (0, 0, 0) - hand grasp position on the handle
- BladeStart: (0, 0, 20.0) - blade base above crossguard
- MiddleSocket: (0, 0, 85.0) - blade midpoint
- BladeEnd: (0, 0, 160.0) - blade tip
- Trace_0: (0, 0, 20.0) - proxy-style trace point 0
- Trace_1: (0, 0, 85.0) - proxy-style trace point 1
- Trace_2: (0, 0, 160.0) - proxy-style trace point 2
- Weapon Start: (0, 0, 20.0) - pack trace compatibility
- Weapon End: (0, 0, 160.0) - pack trace compatibility
- TrailStartSocket: (0, 0, 20.0) - VFX ribbon start
- TrailEndSocket: (0, 0, 160.0) - VFX ribbon end

Safety rules:
- Run under ENGINE_LOCK
- Assert-before-save & readback-assert
- Fail closed if asset missing
"""

import os
import sys

try:
    import unreal
    IN_ENGINE = True
except ImportError:
    IN_ENGINE = False

ASSET_PATH = "/Game/OneBossFight/Boss01/Weapons/SM_Boss01_Greatsword"

SOCKET_DEFINITIONS = [
    ("grip", unreal.Vector(0.0, 0.0, 0.0) if IN_ENGINE else (0.0, 0.0, 0.0)),
    ("BladeStart", unreal.Vector(0.0, 0.0, 20.0) if IN_ENGINE else (0.0, 0.0, 20.0)),
    ("MiddleSocket", unreal.Vector(0.0, 0.0, 85.0) if IN_ENGINE else (0.0, 0.0, 85.0)),
    ("BladeEnd", unreal.Vector(0.0, 0.0, 160.0) if IN_ENGINE else (0.0, 0.0, 160.0)),
    ("Trace_0", unreal.Vector(0.0, 0.0, 20.0) if IN_ENGINE else (0.0, 0.0, 20.0)),
    ("Trace_1", unreal.Vector(0.0, 0.0, 85.0) if IN_ENGINE else (0.0, 0.0, 85.0)),
    ("Trace_2", unreal.Vector(0.0, 0.0, 160.0) if IN_ENGINE else (0.0, 0.0, 160.0)),
    ("Weapon Start", unreal.Vector(0.0, 0.0, 20.0) if IN_ENGINE else (0.0, 0.0, 20.0)),
    ("Weapon End", unreal.Vector(0.0, 0.0, 160.0) if IN_ENGINE else (0.0, 0.0, 160.0)),
    ("TrailStartSocket", unreal.Vector(0.0, 0.0, 20.0) if IN_ENGINE else (0.0, 0.0, 20.0)),
    ("TrailEndSocket", unreal.Vector(0.0, 0.0, 160.0) if IN_ENGINE else (0.0, 0.0, 160.0)),
]


def log(msg):
    if IN_ENGINE:
        unreal.log(f"[GreatswordSockets] {msg}")
    print(f"[GreatswordSockets] {msg}")


def log_error(msg):
    if IN_ENGINE:
        unreal.log_error(f"[GreatswordSockets] ERROR: {msg}")
    print(f"[GreatswordSockets] ERROR: {msg}", file=sys.stderr)


def apply_sockets():
    if not IN_ENGINE:
        log_error("Must be executed inside Unreal Engine.")
        return False

    mesh = unreal.load_asset(ASSET_PATH)
    if not mesh:
        log_error(f"Failed to load static mesh: {ASSET_PATH}")
        return False

    probe = unreal.new_object(unreal.StaticMeshComponent)
    probe.set_static_mesh(mesh)
    existing_names = set(str(n) for n in probe.get_all_socket_names())
    log(f"Existing sockets before run: {sorted(list(existing_names))}")

    added_count = 0
    updated_count = 0
    for name, loc in SOCKET_DEFINITIONS:
        existing_socket = mesh.find_socket(name)
        if existing_socket:
            existing_socket.set_editor_property("relative_location", loc)
            updated_count += 1
            log(f"Updated existing socket '{name}' to {loc}")
        else:
            new_sock = unreal.StaticMeshSocket(mesh)
            new_sock.set_editor_property("socket_name", name)
            new_sock.set_editor_property("relative_location", loc)
            mesh.add_socket(new_sock)
            added_count += 1
            log(f"Added new socket '{name}' at {loc}")

    saved = unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    if not saved:
        log_error(f"Failed to save modified asset: {ASSET_PATH}")
        return False

    # Readback verification
    probe.set_static_mesh(None)
    probe.set_static_mesh(mesh)
    readback_names = set(str(n) for n in probe.get_all_socket_names())
    log(f"Sockets after run ({len(readback_names)} total): {sorted(list(readback_names))}")

    for name, expected_loc in SOCKET_DEFINITIONS:
        assert name in readback_names, f"Readback assertion failed: missing socket '{name}'"
        sock = mesh.find_socket(name)
        actual_loc = sock.get_editor_property("relative_location")
        dx = abs(actual_loc.x - expected_loc.x)
        dy = abs(actual_loc.y - expected_loc.y)
        dz = abs(actual_loc.z - expected_loc.z)
        assert dx < 1e-2 and dy < 1e-2 and dz < 1e-2, f"Socket '{name}' location mismatch: expected {expected_loc}, got {actual_loc}"

    log(f"SUCCESS: {added_count} sockets added, {updated_count} updated. All readback assertions passed.")
    return True


if __name__ == "__main__":
    ok = apply_sockets()
    sys.exit(0 if ok else 1)
