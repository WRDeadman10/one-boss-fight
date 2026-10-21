"""Reads a binary FBX without Blender or Unreal and prints what a delivery review needs: the models (name, type, parent, local transform), the geometries (vertex and polygon counts, bounds in the object's own space), the material
names, the animation stacks (start, stop and length in seconds, from the file's own KTime values) and the time mode of the scene. Plain Python, no packages.
Usage: python -I Scripts/fbx_probe.py <file.fbx> [--verts <ModelNameContains>] [--cluster <BoneNameContains>]   (--verts prints the highest and lowest vertex z of the matching geometry and the model's transform).
It does not apply the skin or the animation: the numbers are the rest geometry as stored, in the file's units (Blender exports centimetres here)."""
import struct
import sys
import zlib

KTIME = 46186158000.0


def read_props(data, pos, count, wide):
    props = []
    for _ in range(count):
        t = chr(data[pos])
        pos += 1
        if t in "YCIFDL":
            size = {"Y": 2, "C": 1, "I": 4, "F": 4, "D": 8, "L": 8}[t]
            fmt = {"Y": "<h", "C": "<b", "I": "<i", "F": "<f", "D": "<d", "L": "<q"}[t]
            props.append(struct.unpack_from(fmt, data, pos)[0])
            pos += size
        elif t in "fdlib":
            length, enc, comp = struct.unpack_from("<III", data, pos)
            pos += 12
            raw = data[pos:pos + comp]
            pos += comp
            if enc == 1:
                raw = zlib.decompress(raw)
            code = {"f": "f", "d": "d", "l": "q", "i": "i", "b": "b"}[t]
            props.append(list(struct.unpack("<%d%s" % (length, code), raw)))
        elif t in "SR":
            (length,) = struct.unpack_from("<I", data, pos)
            pos += 4
            raw = data[pos:pos + length]
            pos += length
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
    name = data[pos + head + 1:pos + head + 1 + name_len].decode("utf-8", "replace")
    p = pos + head + 1 + name_len
    props, p = read_props(data, p, nprops, wide)
    children = []
    while p < end:
        child, p = read_node(data, p, wide)
        if child is None:
            break
        children.append(child)
    return {"name": name, "props": props, "children": children}, end


def parse(path):
    data = open(path, "rb").read()
    if not data.startswith(b"Kaydara FBX Binary"):
        raise SystemExit("not a binary FBX")
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


def find(node, name):
    return [c for c in node["children"] if c["name"] == name]


def props70(node):
    out = {}
    for block in find(node, "Properties70"):
        for p in find(block, "P"):
            out[p["props"][0]] = p["props"][4:]
    return out


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    path = sys.argv[1]
    version, top = parse(path)
    objs = {n["name"]: n for n in top}
    print("%s: FBX %d" % (path, version))
    gs = props70(objs["GlobalSettings"]) if "GlobalSettings" in objs else {}
    tm = gs.get("TimeMode")
    print("time mode %s, unit scale %s, up axis %s front axis %s" % (tm[-1] if tm else None, gs.get("UnitScaleFactor", [None])[-1], gs.get("UpAxis", [None])[-1], gs.get("FrontAxis", [None])[-1]))
    objects = objs.get("Objects", {"children": []})
    ids = {}
    for o in objects["children"]:
        ids[o["props"][0]] = o
    models = [o for o in objects["children"] if o["name"] == "Model"]
    geoms = [o for o in objects["children"] if o["name"] == "Geometry"]
    mats = [o for o in objects["children"] if o["name"] == "Material"]
    stacks = [o for o in objects["children"] if o["name"] == "AnimationStack"]
    # parent links
    parent = {}
    for conn in find(objs.get("Connections", {"children": []}), "C") if "Connections" in objs else []:
        kind, child, par = conn["props"][0], conn["props"][1], conn["props"][2]
        if kind == "OO":
            parent.setdefault(child, []).append(par)
    nm = lambda i: ids[i]["props"][1].split("\x00")[0] if i in ids else str(i)
    print("models %d:" % len(models))
    for m in models:
        pr = props70(m)
        print("  %-34s %-10s parent %-24s T %s R %s S %s" % (m["props"][1].split("\x00")[0], m["props"][2], ",".join(nm(p) for p in parent.get(m["props"][0], [])), [round(x, 2) for x in pr.get("Lcl Translation", [])[-3:]],
              [round(x, 1) for x in pr.get("Lcl Rotation", [])[-3:]], [round(x, 3) for x in pr.get("Lcl Scaling", [])[-3:]]))
    for g in geoms:
        verts = find(g, "Vertices")
        v = verts[0]["props"][0] if verts else []
        idx = find(g, "PolygonVertexIndex")
        polys = sum(1 for i in (idx[0]["props"][0] if idx else []) if i < 0)
        if v:
            xs, ys, zs = v[0::3], v[1::3], v[2::3]
            print("geometry %-30s verts %d polygons %d bounds x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (g["props"][1].split("\x00")[0], len(xs), polys, min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)))
        else:
            print("geometry %s (no vertices)" % g["props"][1].split("\x00")[0])
    print("materials: %s" % [m["props"][1].split("\x00")[0] for m in mats])
    for s in stacks:
        pr = props70(s)
        start, stop = pr.get("LocalStart", [0])[-1], pr.get("LocalStop", [0])[-1]
        print("animation stack %s: %.4f to %.4f s, length %.4f s" % (s["props"][1].split("\x00")[0], start / KTIME, stop / KTIME, (stop - start) / KTIME))
    if "--cluster" in sys.argv:
        # the highest and lowest vertex (z in the geometry's own space) that a skin cluster of a bone weights above 0.5
        key = sys.argv[sys.argv.index("--cluster") + 1].lower()
        model_ids = {m["props"][0] for m in models}
        links = {}
        for conn in find(objs["Connections"], "C"):
            a, b = conn["props"][1], conn["props"][2]
            links.setdefault(a, set()).add(b)
            links.setdefault(b, set()).add(a)
        geom = geoms[0]["props"][0] if geoms else None
        vz = find(geoms[0], "Vertices")[0]["props"][0][2::3] if geoms else []
        for o in objects["children"]:
            if o["name"] == "Deformer" and len(o["props"]) > 2 and o["props"][2] == "Cluster":
                bones = [i for i in links.get(o["props"][0], ()) if i in model_ids]
                if not bones or key not in nm(bones[0]).lower():
                    continue
                idx, wts = find(o, "Indexes"), find(o, "Weights")
                if not idx or not wts:
                    continue
                vx = find(geoms[0], "Vertices")[0]["props"][0][0::3]
                vy = find(geoms[0], "Vertices")[0]["props"][0][1::3]
                sel = [i for i, w in zip(idx[0]["props"][0], wts[0]["props"][0]) if w > 0.5 and i < len(vz)]
                zs = [vz[i] for i in sel]
                if zs:
                    # the head's top part (the 200 vertices highest in z) and its centre: where a crown would have to sit
                    top = sorted(sel, key=lambda i: vz[i])[-200:]
                    print("cluster %s (bone %s): %d vertices above 0.5 weight, highest z %.3f, lowest z %.3f; the highest %d: centre x %.2f y %.2f, x %.2f..%.2f y %.2f..%.2f" % (o["props"][1].split(chr(0))[0], nm(bones[0]), len(zs), max(zs), min(zs),
                        len(top), sum(vx[i] for i in top) / len(top), sum(vy[i] for i in top) / len(top), min(vx[i] for i in top), max(vx[i] for i in top), min(vy[i] for i in top), max(vy[i] for i in top)))
    if "--verts" in sys.argv:
        key = sys.argv[sys.argv.index("--verts") + 1].lower()
        for m in models:
            if key in m["props"][1].lower():
                pr = props70(m)
                print("model %s transform T %s R %s S %s" % (m["props"][1].split("\x00")[0], pr.get("Lcl Translation"), pr.get("Lcl Rotation"), pr.get("Lcl Scaling")))
        for g in geoms:
            if key in g["props"][1].lower():
                v = find(g, "Vertices")[0]["props"][0]
                zs = sorted(v[2::3])
                print("geometry %s: lowest z %.3f, highest z %.3f (first 5 lowest %s)" % (g["props"][1].split("\x00")[0], zs[0], zs[-1], [round(z, 2) for z in zs[:5]]))


if __name__ == "__main__":
    main()
