"""Reads the material layer of a binary FBX (7.x) and prints how many polygons use each material slot. Usage: python Scripts/fbx_materials.py file.fbx
Used to check that a delivered skinned mesh really spreads its polygons over the declared material slots."""
import struct
import sys
import zlib


def read_node(d, pos, ver64):
    if ver64:
        end, nprops, plen = struct.unpack_from("<QQQ", d, pos)
        pos += 24
    else:
        end, nprops, plen = struct.unpack_from("<III", d, pos)
        pos += 12
    nlen = d[pos]
    pos += 1
    name = d[pos:pos + nlen].decode("latin-1")
    pos += nlen
    if end == 0:
        return None, pos
    props = []
    for _ in range(nprops):
        t = chr(d[pos])
        pos += 1
        if t in "YCFDIL":
            size = {"Y": 2, "C": 1, "F": 4, "D": 8, "I": 4, "L": 8}[t]
            fmt = {"Y": "<h", "C": "<B", "F": "<f", "D": "<d", "I": "<i", "L": "<q"}[t]
            props.append(struct.unpack_from(fmt, d, pos)[0])
            pos += size
        elif t in "fdilb":
            n, enc, clen = struct.unpack_from("<III", d, pos)
            pos += 12
            raw = d[pos:pos + clen]
            pos += clen
            if enc == 1:
                raw = zlib.decompress(raw)
            fmt = {"f": "f", "d": "d", "i": "i", "l": "q", "b": "b"}[t]
            props.append(list(struct.unpack("<%d%s" % (n, fmt), raw)))
        elif t in "SR":
            n = struct.unpack_from("<I", d, pos)[0]
            pos += 4
            props.append(d[pos:pos + n])
            pos += n
    children = []
    while pos < end:
        child, pos = read_node(d, pos, ver64)
        if child is None:
            break
        children.append(child)
    return (name, props, children), end


def slot_usage(path, quiet=False):
    """Returns (mapping, {slot index: polygon count}) of the first material layer, and prints it unless quiet."""
    result = []
    d = open(path, "rb").read()
    ver = struct.unpack_from("<I", d, 23)[0]
    pos = 27
    nodes = []
    while pos < len(d) - 40:
        node, pos = read_node(d, pos, ver >= 7500)
        if node is None:
            break
        nodes.append(node)

    def walk(n, depth=0):
        name, props, children = n
        if name == "LayerElementMaterial":
            kv = {c[0]: c[1] for c in children}
            mats = kv.get("Materials", [[]])[0]
            mapping = kv.get("MappingInformationType", [b""])[0]
            counts = {}
            for m in mats:
                counts[m] = counts.get(m, 0) + 1
            if not quiet:
                print("LayerElementMaterial mapping %s, %d entries, polygons per slot index: %s" % (mapping, len(mats), dict(sorted(counts.items()))))
            result.append((mapping.decode("latin-1"), dict(sorted(counts.items()))))
        for c in children:
            walk(c, depth + 1)

    for n in nodes:
        walk(n)
    return result[0] if result else ("none", {})


if __name__ == "__main__":
    slot_usage(sys.argv[1])
