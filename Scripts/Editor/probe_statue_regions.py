"""Prints, for the corpse statue mesh as the engine holds it (log prefix [StatueRegions]), the centroid and extent of its vertices in height bands, per material slot: to compare with the DeathLegend final pose (head (0, 52, 76), pelvis (0, 1, 48), hands (47,-9,79) and (-55,11,55), feet (30,-38,14) and (-33,13,4)) without pixels."""
import unreal

log = lambda m: unreal.log("[StatueRegions] " + m)
m = unreal.load_asset("/Game/OneBossFight/Boss01/Remains/SM_Boss01_CorpseStatue")
d = m.get_static_mesh_description(0)
n = d.get_vertex_count() if hasattr(d, "get_vertex_count") else None
log("vertex count %s" % n)
pts = []
for i in range(n):
    p = d.get_vertex_position(unreal.VertexID(i))
    pts.append((p.x, p.y, p.z))
bands = [(0, 20), (20, 40), (40, 60), (60, 80), (80, 110)]
for lo, hi in bands:
    sel = [p for p in pts if lo <= p[2] < hi]
    if sel:
        cx = sum(p[0] for p in sel) / len(sel); cy = sum(p[1] for p in sel) / len(sel)
        log("z %d..%d: %d verts, centroid x %.1f y %.1f, x %.0f..%.0f, y %.0f..%.0f" % (lo, hi, len(sel), cx, cy, min(p[0] for p in sel), max(p[0] for p in sel), min(p[1] for p in sel), max(p[1] for p in sel)))
# the sword: the long thin extreme in x
xs = sorted(pts, key=lambda p: p[0])
log("lowest x vertex %s, highest x vertex %s; lowest y vertex %s, highest y %s" % (tuple(round(v) for v in xs[0]), tuple(round(v) for v in xs[-1]), tuple(round(v) for v in min(pts, key=lambda p: p[1])), tuple(round(v) for v in max(pts, key=lambda p: p[1]))))
