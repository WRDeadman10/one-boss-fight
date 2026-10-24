"""
merge_a3_combo.py
-----------------
Merges AN_Boss01_A3a_Combo1.fbx (0.80 s, frames 0-24) and
AN_Boss01_A3b_Combo2.fbx (1.3333 s, frames 0-40) into a single
combined FBX at Import/Boss01/Animations/AN_Boss01_A3_Combo.fbx.

Strategy:
- Parse both FBX files into a node tree.
- Use A3a as the base (skeleton, connections, global settings).
- For each AnimationCurve in A3b, find the matching curve in A3a by
  mapping via the Connections graph: bone->CurveNode->Curve.
- Append the A3b keyframe times (shifted by A3a_stop = 24 * KTIME_PER_FRAME)
  and values to the A3a curves.
- Update AnimationStack LocalStop/ReferenceStop to the combined length.
- Write binary FBX 7400 from the mutated node tree.

KTime: 1/46186158000 s.  Frame at 30 fps: 46186158000/30 = 1539538600 KTime.
A3a: 24 frames = 36948926400 KTime  (0.8 s)
A3b: 40 frames = 61581544000 KTime  (1.3333... s)
Combined: 64 frames = 98530470400 KTime  (2.1333... s)
"""
import struct
import sys
import zlib
import os

KTIME = 46186158000.0
KTIME_PER_FRAME_30 = int(KTIME / 30)  # 1539538600

PROJECT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
A3A_PATH = os.path.join(PROJECT, "Import", "Boss01", "Animations", "AN_Boss01_A3a_Combo1.fbx")
A3B_PATH = os.path.join(PROJECT, "Import", "Boss01", "Animations", "AN_Boss01_A3b_Combo2.fbx")
OUT_PATH = os.path.join(PROJECT, "Import", "Boss01", "Animations", "AN_Boss01_A3_Combo.fbx")

# ─── FBX binary reader ────────────────────────────────────────────────────────

def read_props(data, pos, count, wide):
    props = []
    for _ in range(count):
        t = chr(data[pos]); pos += 1
        if t in "YCIFDL":
            size = {"Y": 2, "C": 1, "I": 4, "F": 4, "D": 8, "L": 8}[t]
            fmt  = {"Y": "<h","C": "<b","I": "<i","F": "<f","D": "<d","L": "<q"}[t]
            props.append(struct.unpack_from(fmt, data, pos)[0]); pos += size
        elif t in "fdlib":
            length, enc, comp = struct.unpack_from("<III", data, pos); pos += 12
            raw = data[pos:pos + comp]; pos += comp
            if enc == 1:
                raw = zlib.decompress(raw)
            code = {"f": "f", "d": "d", "l": "q", "i": "i", "b": "b"}[t]
            props.append(list(struct.unpack("<%d%s" % (length, code), raw)))
        elif t in "SR":
            (length,) = struct.unpack_from("<I", data, pos); pos += 4
            raw = data[pos:pos + length]; pos += length
            props.append(raw.decode("utf-8", "replace") if t == "S" else raw)
        else:
            raise ValueError("unknown property type %r" % t)
    return props, pos


def read_node(data, pos, wide):
    head = 24 if wide else 12
    if wide:
        end, nprops, plen = struct.unpack_from("<QQQ", data, pos)
    else:
        end, nprops, plen = struct.unpack_from("<III", data, pos)
    name_len = data[pos + head]
    if end == 0:
        return None, pos + head + 1
    name = data[pos + head + 1: pos + head + 1 + name_len].decode("utf-8", "replace")
    p = pos + head + 1 + name_len
    props, p = read_props(data, p, nprops, wide)
    children = []
    while p < end:
        child, p = read_node(data, p, wide)
        if child is None:
            break
        children.append(child)
    return {"name": name, "props": props, "children": children, "_types": None}, end


def parse_fbx(path):
    data = open(path, "rb").read()
    if not data.startswith(b"Kaydara FBX Binary"):
        raise SystemExit("not a binary FBX: " + path)
    version = struct.unpack_from("<I", data, 23)[0]
    wide = version >= 7500
    pos = 27
    nodes = []
    while pos < len(data) - 40:
        node, pos = read_node(data, pos, wide)
        if node is None:
            break
        nodes.append(node)
    return version, nodes

# ─── FBX binary writer ────────────────────────────────────────────────────────

def write_prop(val, type_hint=None):
    """Serialize a single property value. type_hint overrides auto-detection."""
    if isinstance(val, bool):
        return b"C" + struct.pack("<b", int(val))
    if isinstance(val, int):
        if type_hint == "L" or not (-2147483648 <= val <= 2147483647):
            return b"L" + struct.pack("<q", val)
        return b"I" + struct.pack("<i", val)
    if isinstance(val, float):
        if type_hint == "F":
            return b"F" + struct.pack("<f", val)
        return b"D" + struct.pack("<d", val)
    if isinstance(val, str):
        enc = val.encode("utf-8")
        return b"S" + struct.pack("<I", len(enc)) + enc
    if isinstance(val, bytes):
        return b"R" + struct.pack("<I", len(val)) + val
    if isinstance(val, list):
        if not val:
            # empty array — use int array
            return b"i" + struct.pack("<III", 0, 0, 0)
        if isinstance(val[0], int):
            raw = struct.pack("<%dq" % len(val), *val)
            comp = zlib.compress(raw, 1)
            if len(comp) < len(raw):
                return b"l" + struct.pack("<III", len(val), 1, len(comp)) + comp
            return b"l" + struct.pack("<III", len(val), 0, len(raw)) + raw
        if isinstance(val[0], float):
            raw = struct.pack("<%dd" % len(val), *val)
            comp = zlib.compress(raw, 1)
            if len(comp) < len(raw):
                return b"d" + struct.pack("<III", len(val), 1, len(comp)) + comp
            return b"d" + struct.pack("<III", len(val), 0, len(raw)) + raw
        raise ValueError("list of unknown type: %r" % type(val[0]))
    raise ValueError("cannot serialize %r (%s)" % (val, type(val)))


def write_node(node, wide):
    """Serialize a node to bytes (FBX 7400 format, wide=False)."""
    head = 24 if wide else 12
    int_fmt  = "<Q" if wide else "<I"
    int_size = 8    if wide else 4

    name_bytes = node["name"].encode("utf-8")
    props_data = b""

    # Carry the original property types if stored
    types = node.get("_types") or []
    for i, val in enumerate(node["props"]):
        th = types[i] if i < len(types) else None
        props_data += write_prop(val, th)

    # Null sentinel for children end
    sentinel = bytes(head + 1)

    # Recurse children
    children_data = b""
    for child in node["children"]:
        children_data += write_node(child, wide)
    if node["children"]:
        children_data += sentinel

    # Build body
    body = props_data + children_data
    # Header: end_offset (placeholder), num_props, prop_len, name_len, name
    body_start = head + 1 + len(name_bytes)
    node_size  = body_start + len(body)
    # end_offset is relative to the START of the file, so we can't know it here.
    # We'll use a two-pass approach: write with 0 then patch.
    # Actually, we'll just return the fragment and patch later.
    # For simplicity, write everything into a buffer and patch inline.
    buf = bytearray()
    # placeholder end_offset
    if wide:
        buf += struct.pack("<Q", 0)  # end offset placeholder
        buf += struct.pack("<Q", len(node["props"]))
        buf += struct.pack("<Q", len(props_data))
    else:
        buf += struct.pack("<I", 0)  # end offset placeholder
        buf += struct.pack("<I", len(node["props"]))
        buf += struct.pack("<I", len(props_data))
    buf += bytes([len(name_bytes)])
    buf += name_bytes
    buf += props_data
    buf += children_data
    if node["children"]:
        buf += sentinel
    return bytes(buf)


def patch_offsets(data, base_offset, wide):
    """Walk the serialized binary and patch end-offsets."""
    head = 24 if wide else 12
    int_fmt  = "<Q" if wide else "<I"
    int_size = 8    if wide else 4
    pos = 0
    result = bytearray(data)
    while pos < len(data):
        if pos + head + 1 > len(data):
            break
        if wide:
            end_off, nprops, plen = struct.unpack_from("<QQQ", data, pos)
        else:
            end_off, nprops, plen = struct.unpack_from("<III", data, pos)
        name_len = data[pos + head]
        if end_off == 0 and name_len == 0 and nprops == 0:
            # null sentinel
            break
        # We need to compute the true end offset by scanning
        # Instead patch with the actual end of the node block
        # Walk props to find start of children
        p = pos + head + 1 + name_len
        # skip props
        try:
            _, p2 = read_props_raw(data, p, nprops, wide)
        except Exception:
            break
        # Find end by recursing
        # (Brute: use the node we already wrote—end_off is 0 as placeholder)
        # We'll do a second pass
        break
    return bytes(result)


# ─── Two-pass serializer with correct end offsets ─────────────────────────────

def _serialize_node(node, wide):
    """Recursively serializes a node; returns bytes with end-offset placeholder = 0."""
    head = 24 if wide else 12
    name_b = node["name"].encode("utf-8")

    types = node.get("_types") or []
    props_data = b""
    for i, val in enumerate(node["props"]):
        th = types[i] if i < len(types) else None
        props_data += _write_prop(val, th)

    children_data = b""
    for child in node["children"]:
        children_data += _serialize_node(child, wide)
    sentinel = bytes(head + 1)
    if node["children"]:
        children_data += sentinel

    if wide:
        hdr = struct.pack("<QQQ", 0, len(node["props"]), len(props_data))
    else:
        hdr = struct.pack("<III", 0, len(node["props"]), len(props_data))
    hdr += bytes([len(name_b)]) + name_b
    return hdr + props_data + children_data


def serialize_nodes(nodes, wide=False):
    """Serialize a list of top-level nodes, patching absolute end offsets.
    
    Uses sys.setrecursionlimit for deep skeletons (89 bones * 3 channels * 3 axes = many levels).
    """
    import sys
    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(10000)
    try:
        parts = [_serialize_node(n, wide) for n in nodes]
        head = 24 if wide else 12
        sentinel = bytes(head + 1)
        body = b"".join(parts) + sentinel
        # Now patch end offsets. base = 27 (FBX header size before body).
        result = bytearray(body)
        _patch_iterative(result, 0, len(body), 27, wide, head)
        return bytes(result)
    finally:
        sys.setrecursionlimit(old_limit)


def _scan_node_end(buf, pos, wide, head):
    """Find the byte position just past this node (including its children)."""
    if wide:
        end_ph, nprops, plen = struct.unpack_from("<QQQ", buf, pos)
    else:
        end_ph, nprops, plen = struct.unpack_from("<III", buf, pos)
    name_len = buf[pos + head]
    if name_len == 0 and nprops == 0 and plen == 0:
        return pos + head + 1  # null sentinel
    p = pos + head + 1 + name_len + plen
    # Walk children until sentinel
    while p < len(buf):
        if wide:
            child_end, cnprops, cplen = struct.unpack_from("<QQQ", buf, p)
        else:
            child_end, cnprops, cplen = struct.unpack_from("<III", buf, p)
        cname_len = buf[p + head]
        if cname_len == 0 and cnprops == 0 and cplen == 0:
            p += head + 1
            break
        p = _scan_node_end(buf, p, wide, head)
    return p


def _patch_iterative(buf, start, limit, base, wide, head):
    """Iteratively patch end-offsets at the current level, recursing into children."""
    pos = start
    while pos < limit:
        if pos + head + 1 > limit:
            break
        if wide:
            _, nprops, plen = struct.unpack_from("<QQQ", buf, pos)
        else:
            _, nprops, plen = struct.unpack_from("<III", buf, pos)
        name_len = buf[pos + head]
        if name_len == 0 and nprops == 0 and plen == 0:
            pos += head + 1
            break
        p = pos + head + 1 + name_len + plen
        # Find where children end
        child_end = p
        has_children = False
        while child_end < limit:
            if wide:
                ce, cnp, cpl = struct.unpack_from("<QQQ", buf, child_end)
            else:
                ce, cnp, cpl = struct.unpack_from("<III", buf, child_end)
            cname_len = buf[child_end + head]
            if cname_len == 0 and cnp == 0 and cpl == 0:
                child_end += head + 1
                break
            has_children = True
            # Recurse into child to patch its offsets
            _patch_iterative(buf, child_end, limit, base, wide, head)
            # Advance past this child
            child_end = _scan_node_end(buf, child_end, wide, head)

        node_end = child_end
        absolute_end = base + node_end
        if wide:
            struct.pack_into("<Q", buf, pos, absolute_end)
        else:
            struct.pack_into("<I", buf, pos, absolute_end)
        pos = node_end


def _write_prop(val, type_hint=None):
    """Serialize a single property value."""
    if isinstance(val, bool):
        return b"C" + struct.pack("<b", int(val))
    if isinstance(val, int):
        if type_hint == "L" or not (-2147483648 <= val <= 2147483647):
            return b"L" + struct.pack("<q", val)
        return b"I" + struct.pack("<i", val)
    if isinstance(val, float):
        if type_hint == "F":
            return b"F" + struct.pack("<f", val)
        return b"D" + struct.pack("<d", val)
    if isinstance(val, str):
        enc = val.encode("utf-8")
        return b"S" + struct.pack("<I", len(enc)) + enc
    if isinstance(val, bytes):
        return b"R" + struct.pack("<I", len(val)) + val
    if isinstance(val, list):
        if not val:
            return b"i" + struct.pack("<III", 0, 0, 0)
        if isinstance(val[0], int):
            raw = struct.pack("<%dq" % len(val), *val)
            comp = zlib.compress(raw, 1)
            if len(comp) < len(raw):
                return b"l" + struct.pack("<III", len(val), 1, len(comp)) + comp
            return b"l" + struct.pack("<III", len(val), 0, len(raw)) + raw
        if isinstance(val[0], float):
            raw = struct.pack("<%dd" % len(val), *val)
            comp = zlib.compress(raw, 1)
            if len(comp) < len(raw):
                return b"d" + struct.pack("<III", len(val), 1, len(comp)) + comp
            return b"d" + struct.pack("<III", len(val), 0, len(raw)) + raw
        raise ValueError("list of unknown element type: %r" % type(val[0]))
    raise ValueError("cannot serialize %r (%s)" % (val, type(val)))


# ─── Helper tree functions ────────────────────────────────────────────────────

def find_children(node, name):
    return [c for c in node["children"] if c["name"] == name]


def find_child(node, name):
    for c in node["children"]:
        if c["name"] == name:
            return c
    return None


def props70(node):
    out = {}
    for block in find_children(node, "Properties70"):
        for p in find_children(block, "P"):
            out[p["props"][0]] = p["props"][4:]
    return out


def set_prop70(node, key, values):
    """Update or insert a P entry in Properties70."""
    for block in find_children(node, "Properties70"):
        for p in find_children(block, "P"):
            if p["props"][0] == key:
                p["props"][4:] = values
                return
        # Not found: insert
        new_p = {
            "name": "P",
            "props": [key] + ["", "", ""] + values,
            "children": [],
            "_types": None,
        }
        block["children"].append(new_p)


# ─── Build a curve ID → curve node map ───────────────────────────────────────

def build_curve_id_map(nodes_list):
    """
    Returns:
      curves: {id: node}  for AnimationCurve nodes
      curve_nodes: {id: node}  for AnimationCurveNode nodes
      connections: list of [kind, child_id, parent_id, (optional prop)]
    """
    objs = {n["name"]: n for n in nodes_list}
    objects = objs.get("Objects", {"children": []})
    conns_node = objs.get("Connections", {"children": []})

    curves = {}
    curve_nodes = {}
    for o in objects["children"]:
        oid = o["props"][0]
        if o["name"] == "AnimationCurve":
            curves[oid] = o
        elif o["name"] == "AnimationCurveNode":
            curve_nodes[oid] = o

    connections = []
    for c in find_children(conns_node, "C"):
        connections.append(c["props"])

    return curves, curve_nodes, connections


def get_anim_stack_stop(nodes_list):
    """Return the LocalStop KTime of the first AnimationStack."""
    objs = {n["name"]: n for n in nodes_list}
    objects = objs.get("Objects", {"children": []})
    for o in objects["children"]:
        if o["name"] == "AnimationStack":
            pr = props70(o)
            return pr.get("LocalStop", [0])[-1]
    return 0


def set_anim_stack_times(nodes_list, start_ktime, stop_ktime):
    """Set LocalStart/LocalStop/ReferenceStart/ReferenceStop on all AnimationStacks."""
    objs = {n["name"]: n for n in nodes_list}
    objects = objs.get("Objects", {"children": []})
    for o in objects["children"]:
        if o["name"] == "AnimationStack":
            set_prop70(o, "LocalStart",      [start_ktime])
            set_prop70(o, "LocalStop",       [stop_ktime])
            set_prop70(o, "ReferenceStart",  [start_ktime])
            set_prop70(o, "ReferenceStop",   [stop_ktime])

    # Also update Takes node if present
    takes_node = objs.get("Takes")
    if takes_node:
        take = find_child(takes_node, "Take")
        if take:
            local_time = find_child(take, "LocalTime")
            if local_time:
                local_time["props"] = [start_ktime, stop_ktime]
            ref_time = find_child(take, "ReferenceTime")
            if ref_time:
                ref_time["props"] = [start_ktime, stop_ktime]


# ─── Build a bone->curvenode->curve mapping for matching ─────────────────────

def build_bone_curve_map(nodes_list):
    """
    Returns a dict: bone_name -> channel_name ('T'/'R'/'S') -> axis_idx (0/1/2) -> curve_id
    and the inverse: curve_id -> (bone_name, channel, axis)
    """
    objs = {n["name"]: n for n in nodes_list}
    objects = objs.get("Objects", {"children": []})
    conns_node = objs.get("Connections", {"children": []})

    # Build id->name map
    id_to_name = {}
    id_to_type = {}
    for o in objects["children"]:
        oid = o["props"][0]
        raw_name = o["props"][1] if len(o["props"]) > 1 else ""
        # name is "BoneName\x00\x01Type"
        clean_name = raw_name.split("\x00")[0]
        id_to_name[oid] = clean_name
        id_to_type[oid] = o["name"]

    # Build connection graph: child->parents, parent->children
    child_to_parents = {}  # child_id -> list of (parent_id, prop_name)
    parent_to_children = {}  # parent_id -> list of (child_id, prop_name)
    for c in find_children(conns_node, "C"):
        kind = c["props"][0]
        cid  = c["props"][1]
        pid  = c["props"][2]
        prop = c["props"][3] if len(c["props"]) > 3 else ""
        child_to_parents.setdefault(cid, []).append((pid, prop))
        parent_to_children.setdefault(pid, []).append((cid, prop))

    # For each AnimationCurve, trace upward:
    # AnimationCurve -> (OP conn with prop d|X/Y/Z) AnimationCurveNode -> (OO) bone Model
    curve_to_info = {}  # curve_id -> (bone_name, channel_name, axis_prop)
    for o in objects["children"]:
        if o["name"] != "AnimationCurve":
            continue
        cid = o["props"][0]
        # Parents of AnimationCurve are AnimationCurveNodes (via OP connection)
        for (pid, prop) in child_to_parents.get(cid, []):
            if id_to_type.get(pid) == "AnimationCurveNode":
                channel = id_to_name.get(pid, "")  # 'T', 'R', 'S'
                # Parents of AnimationCurveNode are bones (via OO or OP)
                for (gpid, gprop) in child_to_parents.get(pid, []):
                    if id_to_type.get(gpid) == "Model":
                        bone = id_to_name.get(gpid, "")
                        curve_to_info[cid] = (bone, channel, prop)

    return curve_to_info, id_to_name


# ─── Main merge logic ─────────────────────────────────────────────────────────

def merge_curves(a3a_nodes, a3b_nodes, time_offset_ktime):
    """
    For each AnimationCurve in a3b, find the matching curve in a3a
    (same bone, same channel, same axis), then append a3b keyframes
    (shifted by time_offset_ktime) to a3a.
    Bones/curves not in a3a get added.
    """
    # Build bone->curve mappings for both
    a3a_curve_info, a3a_id_name = build_bone_curve_map(a3a_nodes)
    a3b_curve_info, a3b_id_name = build_bone_curve_map(a3b_nodes)

    # Build reverse: (bone, channel, axis) -> curve_id for a3a
    a3a_info_to_id = {v: k for k, v in a3a_curve_info.items()}

    # Build id->node map for a3a curves
    objs_a3a = {n["name"]: n for n in a3a_nodes}
    objects_a3a = objs_a3a.get("Objects", {"children": []})
    a3a_curves = {}
    for o in objects_a3a["children"]:
        if o["name"] == "AnimationCurve":
            a3a_curves[o["props"][0]] = o

    # Build id->node map for a3b curves
    objs_a3b = {n["name"]: n for n in a3b_nodes}
    objects_a3b = objs_a3b.get("Objects", {"children": []})
    a3b_curves = {}
    for o in objects_a3b["children"]:
        if o["name"] == "AnimationCurve":
            a3b_curves[o["props"][0]] = o

    matched = 0
    unmatched = 0

    for a3b_cid, (bone, channel, axis) in a3b_curve_info.items():
        a3a_cid = a3a_info_to_id.get((bone, channel, axis))
        if a3a_cid is None:
            unmatched += 1
            continue

        a3a_curve = a3a_curves.get(a3a_cid)
        a3b_curve = a3b_curves.get(a3b_cid)
        if a3a_curve is None or a3b_curve is None:
            unmatched += 1
            continue

        # Get keyframes from a3b
        a3b_key_times = None
        a3b_key_vals  = None
        for child in a3b_curve["children"]:
            if child["name"] == "KeyTime":
                a3b_key_times = child["props"][0]  # list of int (KTime)
            elif child["name"] == "KeyValueFloat":
                a3b_key_vals  = child["props"][0]  # list of float

        if a3b_key_times is None or a3b_key_vals is None:
            unmatched += 1
            continue

        # Shift times by time_offset
        shifted_times = [t + time_offset_ktime for t in a3b_key_times]

        # Get a3a keyframes
        a3a_key_times = None
        a3a_key_vals  = None
        a3a_key_attr_flags    = None
        a3a_key_attr_data     = None
        a3a_key_attr_ref_count= None

        for child in a3a_curve["children"]:
            if child["name"] == "KeyTime":
                a3a_key_times = child
            elif child["name"] == "KeyValueFloat":
                a3a_key_vals  = child
            elif child["name"] == "KeyAttrFlags":
                a3a_key_attr_flags = child
            elif child["name"] == "KeyAttrDataFloat":
                a3a_key_attr_data  = child
            elif child["name"] == "KeyAttrRefCount":
                a3a_key_attr_ref_count = child

        # Get a3b attr data too
        a3b_key_attr_flags    = None
        a3b_key_attr_data     = None
        a3b_key_attr_ref_count= None
        for child in a3b_curve["children"]:
            if child["name"] == "KeyAttrFlags":
                a3b_key_attr_flags = child
            elif child["name"] == "KeyAttrDataFloat":
                a3b_key_attr_data  = child
            elif child["name"] == "KeyAttrRefCount":
                a3b_key_attr_ref_count = child

        # Append keyframes to a3a
        if a3a_key_times is not None:
            a3a_key_times["props"][0].extend(shifted_times)
        if a3a_key_vals is not None:
            a3a_key_vals["props"][0].extend(a3b_key_vals)

        # Merge KeyAttrRefCount: sum up the total count
        # Simple approach: extend flags and data, and concatenate ref counts
        if a3a_key_attr_flags is not None and a3b_key_attr_flags is not None:
            a3a_key_attr_flags["props"][0].extend(a3b_key_attr_flags["props"][0])
        if a3a_key_attr_data is not None and a3b_key_attr_data is not None:
            a3a_key_attr_data["props"][0].extend(a3b_key_attr_data["props"][0])
        if a3a_key_attr_ref_count is not None and a3b_key_attr_ref_count is not None:
            a3a_key_attr_ref_count["props"][0].extend(a3b_key_attr_ref_count["props"][0])

        # Update KeyCount
        for child in a3a_curve["children"]:
            if child["name"] == "KeyCount":
                total = len(a3a_key_times["props"][0]) if a3a_key_times else 0
                child["props"][0] = total

        matched += 1

    print("Curve merge: matched %d, unmatched %d (of %d a3b curves)" % (matched, unmatched, len(a3b_curve_info)))


def write_fbx(path, version, nodes):
    """Write FBX binary 7400."""
    header = b"Kaydara FBX Binary  \x00\x1a\x00"
    header += struct.pack("<I", version)  # version 7400
    wide = version >= 7500
    body = serialize_nodes(nodes, wide=wide)
    # Footer: 13-byte padding block of zeros, then some fixed bytes
    footer = b"\x00" * 13
    footer += b"\xfa\xbc\xab\x09\xd0\xc8\xd4\x66\xb1\x76\xfb\x83\x1c\xf7\x26\x7e"
    footer += b"\x00" * 120
    footer += struct.pack("<I", version)
    footer += b"\x00" * 120
    footer += b"\xf8\x5a\x8c\x6a\xde\xf5\xd9\x7e\xec\xe9\x0c\xe3\x75\x8f\x29\x0b"
    with open(path, "wb") as f:
        f.write(header + body + footer)
    print("Written: %s (%d bytes)" % (path, os.path.getsize(path)))


def main():
    print("Parsing A3a...")
    ver_a3a, nodes_a3a = parse_fbx(A3A_PATH)
    print("Parsing A3b...")
    ver_a3b, nodes_a3b = parse_fbx(A3B_PATH)

    print("A3a version: %d, A3b version: %d" % (ver_a3a, ver_a3b))

    # Get the stop times
    a3a_stop = get_anim_stack_stop(nodes_a3a)
    a3b_stop = get_anim_stack_stop(nodes_a3b)
    print("A3a stop: %d KTime (%.4f s)" % (a3a_stop, a3a_stop / KTIME))
    print("A3b stop: %d KTime (%.4f s)" % (a3b_stop, a3b_stop / KTIME))

    combined_stop = a3a_stop + a3b_stop
    print("Combined stop: %d KTime (%.4f s)" % (combined_stop, combined_stop / KTIME))

    # Merge curves: A3a is the base, append A3b curves offset by a3a_stop
    print("Merging curves...")
    merge_curves(nodes_a3a, nodes_a3b, a3a_stop)

    # Update AnimationStack time range
    print("Updating animation stack times...")
    set_anim_stack_times(nodes_a3a, 0, combined_stop)

    # Write combined FBX
    print("Writing combined FBX...")
    write_fbx(OUT_PATH, ver_a3a, nodes_a3a)
    print("Done!")


if __name__ == "__main__":
    main()
