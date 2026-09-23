import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from boot_checks import png_check


def chunk(kind, payload):
    return struct.pack('>I', len(payload)) + kind + payload + struct.pack('>I', zlib.crc32(kind + payload))


class PngRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'asset.png'
        self.png = (b'\x89PNG\r\n\x1a\n' +
                    chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)) +
                    chunk(b'IDAT', zlib.compress(b'\x00\x00\x00\x00')) + chunk(b'IEND', b''))

    def test_accepts_png(self):
        self.path.write_bytes(self.png)
        png_check(self.path)

    def test_rejects_text_conversion(self):
        self.path.write_bytes(self.png.decode('utf-8', errors='replace').encode('utf-8'))
        with self.assertRaisesRegex(RuntimeError, 'signature'):
            png_check(self.path)

    def test_rejects_corrupt_chunk(self):
        data = bytearray(self.png)
        data[29] ^= 1
        self.path.write_bytes(data)
        with self.assertRaisesRegex(RuntimeError, 'CRC'):
            png_check(self.path)

    def test_rejects_missing_end(self):
        self.path.write_bytes(self.png[:-12])
        with self.assertRaisesRegex(RuntimeError, 'Incomplete'):
            png_check(self.path)
