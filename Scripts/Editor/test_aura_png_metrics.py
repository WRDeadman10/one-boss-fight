"""Pure-Python fixtures for the Lead aura screenshot brightness gate."""
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

from Scripts.Editor.aura_png_metrics import mean_gray


def chunk(kind, payload):
    return (struct.pack(">I", len(payload)) + kind + payload +
            struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF))


def grayscale_png_rows(rows, filters):
    height = len(rows)
    width = len(rows[0])
    encoded = bytearray()
    previous = [0] * width
    for pixels, filter_type in zip(rows, filters):
        encoded.append(filter_type)
        for index, value in enumerate(pixels):
            left = pixels[index - 1] if index else 0
            up = previous[index]
            upper_left = previous[index - 1] if index else 0
            if filter_type == 0:
                predictor = 0
            elif filter_type == 1:
                predictor = left
            elif filter_type == 2:
                predictor = up
            elif filter_type == 3:
                predictor = (left + up) // 2
            else:
                base = left + up - upper_left
                distances = (abs(base - left), abs(base - up), abs(base - upper_left))
                predictor = (left, up, upper_left)[distances.index(min(distances))]
            encoded.append((value - predictor) & 255)
        previous = pixels
    header = struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) +
            chunk(b"IDAT", zlib.compress(bytes(encoded))) + chunk(b"IEND", b""))


class AuraPngMetricTests(unittest.TestCase):
    def test_mean_gray_decodes_all_png_row_filters(self):
        rows = [[9, 31, 77] for _ in range(5)]
        data = grayscale_png_rows(rows, [0, 1, 2, 3, 4])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "filters.png"
            path.write_bytes(data)
            self.assertAlmostEqual(mean_gray(path), sum(rows[0]) / 3)

    def test_mean_gray_rejects_non_png(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "not.png"
            path.write_bytes(b"not a png")
            with self.assertRaisesRegex(ValueError, "not a PNG"):
                mean_gray(path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
