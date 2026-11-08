"""Small standard-library PNG decoder for Lead capture brightness checks."""
import struct
import zlib

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def mean_gray(path):
    """Return mean 8-bit luma for non-interlaced PNG screenshots; reject unknown formats."""
    with open(path, "rb") as stream:
        data = stream.read()
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("not a PNG")
    offset = len(PNG_SIGNATURE)
    width = height = depth = color = interlace = None
    saw_iend = False
    compressed = []
    while offset + 12 <= len(data):
        size = struct.unpack(">I", data[offset:offset + 4])[0]
        kind = data[offset + 4:offset + 8]
        start = offset + 8
        end = start + size
        if end + 4 > len(data):
            raise ValueError("truncated PNG chunk")
        chunk = data[start:end]
        if kind == b"IHDR":
            width, height, depth, color, compression, filtering, interlace = struct.unpack(">IIBBBBB", chunk)
            if compression != 0 or filtering != 0:
                raise ValueError("unsupported PNG compression/filter method")
        elif kind == b"IDAT":
            compressed.append(chunk)
        elif kind == b"IEND":
            if size != 0:
                raise ValueError("invalid PNG IEND chunk")
            saw_iend = True
            break
        offset = end + 4
    if not saw_iend:
        raise ValueError("missing PNG IEND chunk")
    if not width or not height or depth != 8 or interlace != 0 or color not in (0, 2, 4, 6):
        raise ValueError("unsupported PNG screenshot format")
    channels = {0: 1, 2: 3, 4: 2, 6: 4}[color]
    stride = width * channels
    raw = zlib.decompress(b"".join(compressed))
    if len(raw) != height * (stride + 1):
        raise ValueError("PNG pixel payload size mismatch")
    previous = bytearray(stride)
    total = 0.0
    count = 0
    position = 0
    for _ in range(height):
        filter_type = raw[position]
        position += 1
        source = raw[position:position + stride]
        position += stride
        row = bytearray(stride)
        if filter_type == 0:
            row[:] = source
        elif filter_type in (1, 2, 3, 4):
            for i, value in enumerate(source):
                left = row[i - channels] if i >= channels else 0
                up = previous[i]
                upper_left = previous[i - channels] if i >= channels else 0
                if filter_type == 1:
                    predictor = left
                elif filter_type == 2:
                    predictor = up
                elif filter_type == 3:
                    predictor = (left + up) // 2
                else:
                    base = left + up - upper_left
                    da, db, dc = abs(base - left), abs(base - up), abs(base - upper_left)
                    predictor = left if da <= db and da <= dc else (up if db <= dc else upper_left)
                row[i] = (value + predictor) & 255
        else:
            raise ValueError("unsupported PNG row filter %d" % filter_type)
        if color in (0, 4):
            total += sum(row[i] for i in range(0, stride, channels))
            count += width
        else:
            for i in range(0, stride, channels):
                red, green, blue = row[i], row[i + 1], row[i + 2]
                total += 0.299 * red + 0.587 * green + 0.114 * blue
                count += 1
        previous = row
    return total / count
