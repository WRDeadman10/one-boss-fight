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

    def test_missing_and_truncated_capture_files_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(FileNotFoundError):
                mean_gray(root / "missing.png")
            complete = grayscale_png_rows([[12, 24, 36]], [0])
            truncated = root / "truncated.png"
            truncated.write_bytes(complete[:-12])  # pixels decode, but required IEND is absent
            with self.assertRaisesRegex(ValueError, "IEND"):
                mean_gray(truncated)

    def test_black_dark_and_usable_frames_keep_distinct_measured_values(self):
        samples = (("black", [[0, 0, 0]], 0.0),
                   ("dark", [[2, 3, 2]], 7.0 / 3.0),
                   ("usable", [[30, 60, 90]], 60.0))
        with tempfile.TemporaryDirectory() as directory:
            for name, rows, expected in samples:
                with self.subTest(name=name):
                    path = Path(directory) / (name + ".png")
                    path.write_bytes(grayscale_png_rows(rows, [0]))
                    self.assertAlmostEqual(mean_gray(path), expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
