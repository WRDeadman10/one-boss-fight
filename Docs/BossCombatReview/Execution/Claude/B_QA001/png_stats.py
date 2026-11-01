# QA-001 helper (lead, Claude): decodes a PNG with the standard library only (no PIL on this machine) and prints how much of it is NOT black, plus the share of "overlay yellow" pixels (the boss overlay is drawn yellow).
# Usage: python -I png_stats.py <file.png>
import json
import struct
import sys
import zlib

data = open(sys.argv[1], 'rb').read()
assert data[:8] == b'\x89PNG\r\n\x1a\n', 'not a PNG'
pos, idat, ihdr = 8, b'', None
while pos < len(data):
    ln, typ = struct.unpack('>I4s', data[pos:pos + 8])
    body = data[pos + 8:pos + 8 + ln]
    if typ == b'IHDR':
        ihdr = struct.unpack('>IIBBBBB', body)
    elif typ == b'IDAT':
        idat += body
    pos += 12 + ln
w, h, depth, ctype, _, _, interlace = ihdr
assert depth == 8 and interlace == 0 and ctype in (2, 6), ('unsupported PNG', ihdr)
bpp = 3 if ctype == 2 else 4
raw = zlib.decompress(idat)
stride = w * bpp
prev = bytearray(stride)
nonblack = yellow = 0
rs, gs, bs = 0, 0, 0
i = 0
for y in range(h):
    f = raw[i]; line = bytearray(raw[i + 1:i + 1 + stride]); i += 1 + stride
    for x in range(stride):
        a = line[x - bpp] if x >= bpp else 0
        b = prev[x]
        c = prev[x - bpp] if x >= bpp else 0
        if f == 1: line[x] = (line[x] + a) & 255
        elif f == 2: line[x] = (line[x] + b) & 255
        elif f == 3: line[x] = (line[x] + ((a + b) >> 1)) & 255
        elif f == 4:
            p = a + b - c; pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
            pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
            line[x] = (line[x] + pr) & 255
    for x in range(0, stride, bpp):
        r, g, bl = line[x], line[x + 1], line[x + 2]
        rs += r; gs += g; bs += bl
        if r > 16 or g > 16 or bl > 16:
            nonblack += 1
        if r > 200 and g > 180 and bl < 90:
            yellow += 1
    prev = line
n = w * h
print(json.dumps({'file': sys.argv[1], 'width': w, 'height': h, 'pixels': n, 'nonblack_fraction': round(nonblack / n, 4), 'yellow_overlay_pixels': yellow, 'mean_rgb': [round(rs / n, 1), round(gs / n, 1), round(bs / n, 1)]}))
