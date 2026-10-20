"""Self-check for Boss 01 deliveries (Antigravity runs it before reporting, Claude runs the same checks). Usage (needs Pillow): python Scripts/check_boss01_delivery.py
Checks, all objective:
  1. every FBX in Import/Boss01 (skeletal and animation): the first bone node is named exactly "root" (not "root.001", not "Armature"), and no node name has a Blender duplicate suffix (".001" and so on);
  2. body FBX: node names are the same set as the pack mannequin reference (extra or missing bones listed);
  3. textures in Import/Boss01/**/Textures: size, and detail (number of different colors in a 128 x 128 downsample). A normal map with fewer than 300 colors is flat (no baked detail),
     a base color or ORM with fewer than 300 is a flat color;
  4. renders (png in Import/Boss01): mean brightness (must be above 25 of 255) and the fraction of edge pixels (must be above 1.5 percent: an empty gradient with a horizon line fails);
     pictures with identical decoded pixels are listed.
Exit code 1 when something fails. Prints one line per problem."""
import glob
import hashlib
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Import")
BOSS = os.path.join(ROOT, "Boss01")
REF = os.path.join(ROOT, "ThirdParty", "Reference", "SKM_CombatMannequin_Simple.fbx")
problems = []


def nodes(path):
    data = open(path, "rb").read()
    return [m.decode("latin-1") for m in re.findall(rb"([A-Za-z0-9_\. ]+)\x00\x01Model", data)]


def node_transform(path, node):
    """Lcl Translation / Rotation / Scaling of a Model node in a binary FBX ({} when the node carries none, which is how Unreal exports identity)."""
    import struct
    d = open(path, "rb").read()
    i = d.find(node.encode() + b"\x00\x01Model")
    if i < 0:
        return None
    seg = d[i:i + 3000]
    next_m = seg.find(b"\x00\x01Model", len(node) + 7)
    if next_m > 0:
        seg = seg[:next_m]
    out = {}
    for key in (b"Lcl Translation", b"Lcl Rotation", b"Lcl Scaling"):
        j = seg.find(key)
        if j < 0:
            continue
        for p in range(j, j + 200):
            if seg[p:p + 1] == b"D" and seg[p + 9:p + 10] == b"D" and seg[p + 18:p + 19] == b"D":
                out[key.decode()[4:7]] = tuple(round(struct.unpack("<d", seg[p + 1 + 9 * k:p + 9 + 9 * k])[0], 3) for k in range(3))
                break
    return out


ref_nodes = [n for n in nodes(REF) if not n.startswith("SKM_")] if os.path.exists(REF) else []
for f in sorted(glob.glob(os.path.join(BOSS, "**", "*.fbx"), recursive=True)):
    name = os.path.relpath(f, BOSS)
    ns = nodes(f)
    if "Weapons" in f or not ns:
        suffixed = [n for n in ns if re.search(r"\.\d{3}$", n)]
        if suffixed:
            problems.append("%s: node names with a Blender suffix: %s" % (name, suffixed[:5]))
        for main in [n for n in ns if not n.startswith("SOCKET_")][:1]:
            t = node_transform(f, main) or {}
            if any(abs(v) > 0.001 for v in t.get("Tra", (0, 0, 0))) or any(abs(v) > 0.001 for v in t.get("Rot", (0, 0, 0))) or any(abs(v - 1) > 0.001 for v in t.get("Sca", (1, 1, 1))):
                problems.append("%s: the mesh object carries a transform %s: apply all transforms (location 0, rotation 0, scale 1) so the origin sits at the grip" % (name, t))
        continue
    bones = [n for n in ns if not n.startswith("SK_") and not n.startswith("SKM_") and not n.startswith("AN_")]
    if not bones or bones[0] != "root":
        problems.append("%s: first bone is %r, must be exactly 'root'" % (name, bones[0] if bones else None))
    suffixed = [n for n in ns if re.search(r"\.\d{3}$", n)]
    if suffixed:
        problems.append("%s: node names with a Blender suffix: %s" % (name, suffixed[:5]))
    for main in ("root", "SK_Boss01_Body"):
        t = node_transform(f, main) or {}
        if any(abs(v - 1) > 0.001 for v in t.get("Sca", (1, 1, 1))):
            problems.append("%s: node %s has scaling %s (Unreal imports the mesh 100 times too big or small): unit scale must be centimetres and every object scale 1" % (name, main, t["Sca"]))
    if "Body" in name:
        geo = [m.decode("latin-1") for m in re.findall(rb"([A-Za-z0-9_\. ]+)\x00\x01Geometry", open(f, "rb").read())]
        extra_geo = [g for g in geo if "Morph" in g or "stage" in g.lower()]
        if extra_geo:
            problems.append("%s: extra geometry nodes next to the body mesh (shape keys or helper meshes exported as geometry): %s" % (name, extra_geo[:6]))
    if ref_nodes and "Body" in name:
        missing = [n for n in ref_nodes if n not in ns and not n.startswith("SKM_")]
        extra = [n for n in bones if n not in ref_nodes]
        if missing:
            problems.append("%s: bones missing compared with the mannequin: %s" % (name, missing[:8]))
        if extra:
            problems.append("%s: extra nodes compared with the mannequin: %s" % (name, extra[:8]))

try:
    from PIL import Image
except ImportError:
    Image = None
    print("Pillow missing: texture and render checks skipped")

if Image:
    for f in sorted(glob.glob(os.path.join(BOSS, "**", "Textures", "*.png"), recursive=True)):
        im = Image.open(f).convert("RGB")
        colors = len(set(im.resize((128, 128)).getdata()))
        if colors < 300:
            problems.append("%s: only %d colors in a 128x128 downsample (%s): flat, no baked or painted detail" % (os.path.relpath(f, BOSS), colors, im.size))
    hashes = {}
    for f in sorted(glob.glob(os.path.join(BOSS, "**", "*.png"), recursive=True)):
        if "Textures" in f:
            continue
        rel = os.path.relpath(f, BOSS)
        img = Image.open(f).convert("RGB")
        # duplicates are judged on the decoded pixels, not on the file bytes (metadata or padding must not hide a repeated image)
        h = hashlib.md5(img.tobytes()).hexdigest()
        hashes.setdefault(h, []).append(rel)
        g = img.convert("L").resize((256, 256))
        px = list(g.getdata())
        mean = sum(px) / len(px)
        # detail: how many pixels sit on an edge (a neighbour differs by more than 10 levels). A plain gradient with a horizon line has well under 1 percent; a lit model has several percent.
        edge = 0
        for y in range(1, 255):
            row, prev = y * 256, (y - 1) * 256
            for x in range(1, 255):
                v = px[row + x]
                if abs(v - px[row + x - 1]) > 10 or abs(v - px[prev + x]) > 10:
                    edge += 1
        frac = edge / (254 * 254)
        if mean < 25:
            problems.append("%s: render is almost black (mean brightness %.0f of 255)" % (rel, mean))
        if frac < 0.015:
            problems.append("%s: the picture has no subject: only %.2f percent of the pixels are edges (an empty background or a speck)" % (rel, frac * 100))
    for h, files in hashes.items():
        if len(files) > 1:
            problems.append("identical pictures (same pixels, different file bytes counts): %s" % files)

for p in problems:
    print("FAIL " + p)
print("%d problem(s)" % len(problems))
sys.exit(1 if problems else 0)
