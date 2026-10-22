"""Connected pieces of the first mesh in a binary FBX (log of a delivery review): polygons that share a vertex index or a position (within 1e-3) are one piece.
Prints per piece: vertices, polygons, bounds in the file's own space. With --near <axis index 0|1|2> it also prints, for every small piece (under 100 vertices), how far its lowest vertex along that axis lies
below the highest vertex of the biggest piece within 3 cm sideways (a negative depth means the piece floats above it): a spire sunk into a guard shows a positive depth. Only vertices of the big piece below the small piece's own tip count.
Usage: python Scripts/fbx_components.py <file.fbx> [--axis 1]   (Blender exports the sword with its length on the file's y axis, hence the default 1). Plain Python, uses fbx_probe's reader."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fbx_probe  # noqa: E402


def main():
    path = sys.argv[1]
    axis = int(sys.argv[sys.argv.index("--axis") + 1]) if "--axis" in sys.argv else 1
    _, top = fbx_probe.parse(path)
    objs = {n["name"]: n for n in top}
    geom = next(o for o in objs["Objects"]["children"] if o["name"] == "Geometry")
    v = fbx_probe.find(geom, "Vertices")[0]["props"][0]
    idx = fbx_probe.find(geom, "PolygonVertexIndex")[0]["props"][0]
    pts = [(v[i], v[i + 1], v[i + 2]) for i in range(0, len(v), 3)]
    # weld by position
    key = {}
    weld = []
    for p in pts:
        k = (round(p[0] / 1e-3), round(p[1] / 1e-3), round(p[2] / 1e-3))
        weld.append(key.setdefault(k, len(key)))
    parent = list(range(len(key)))

    def root(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    polys = []
    cur = []
    for i in idx:
        cur.append(i if i >= 0 else ~i)
        if i < 0:
            polys.append(cur)
            cur = []
    for poly in polys:
        for a, b in zip(poly, poly[1:]):
            ra, rb = root(weld[a]), root(weld[b])
            if ra != rb:
                parent[ra] = rb
    pieces = {}
    for pi, poly in enumerate(polys):
        pieces.setdefault(root(weld[poly[0]]), []).append(pi)
    info = []
    for r, plist in pieces.items():
        vs = {i for pi in plist for i in polys[pi]}
        xs = [pts[i] for i in vs]
        info.append({"polys": len(plist), "verts": len(vs), "pts": xs, "lo": [min(p[k] for p in xs) for k in range(3)], "hi": [max(p[k] for p in xs) for k in range(3)]})
    info.sort(key=lambda d: -d["verts"])
    print("%s: %d piece(s)" % (path, len(info)))
    side = [k for k in range(3) if k != axis]
    big = info[0]
    for n, d in enumerate(info):
        line = "  piece %d: %d verts, %d polygons, bounds lo %s hi %s" % (n, d["verts"], d["polys"], [round(x, 2) for x in d["lo"]], [round(x, 2) for x in d["hi"]])
        if n and d["verts"] < 100:
            cx = sum(p[side[0]] for p in d["pts"]) / len(d["pts"])
            cz = sum(p[side[1]] for p in d["pts"]) / len(d["pts"])
            near = [p[axis] for p in big["pts"] if abs(p[side[0]] - cx) <= 3.0 and abs(p[side[1]] - cz) <= 3.0 and p[axis] < d["hi"][axis]]  # only what is below the spire's own tip: the blade does not count
            if near:
                line += " | lowest %.2f, biggest piece reaches %.2f within 3 cm sideways: depth %.2f cm" % (d["lo"][axis], max(near), max(near) - d["lo"][axis])
            else:
                line += " | nothing of the biggest piece within 3 cm sideways"
        print(line)


main()
