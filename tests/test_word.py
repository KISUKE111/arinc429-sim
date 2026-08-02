import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from arinc429 import encode, decode, SSM
from arinc429.bnr import ALTITUDE


class TestWordRoundtrip(unittest.TestCase):
    def test_encode_decode_roundtrip(self):
        raw = encode(label_octal="203", sdi=1, data=12345, ssm=SSM.NORMAL_OPERATION)
        decoded = decode(raw)
        self.assertEqual(decoded.label_octal, "203")
        self.assertEqual(decoded.sdi, 1)
        self.assertEqual(decoded.data, 12345)
        self.assertEqual(decoded.ssm, SSM.NORMAL_OPERATION)
        self.assertTrue(decoded.parity_ok)

    def test_parity_is_odd(self):
        raw = encode(label_octal="000", sdi=0, data=0, ssm=0)
        ones = bin(raw).count("1")
        self.assertEqual(ones % 2, 1)

    def test_corrupted_word_fails_parity(self):
        raw = encode(label_octal="203", sdi=0, data=100, ssm=SSM.NORMAL_OPERATION)
        corrupted = raw ^ 0b1  # flip one data bit, parity bit unchanged
        decoded = decode(corrupted)
        self.assertFalse(decoded.parity_ok)

    def test_invalid_label_raises(self):
        with self.assertRaises(ValueError):
            encode(label_octal="400", sdi=0, data=0, ssm=0)  # > 377 octal

    def test_invalid_data_range_raises(self):
        with self.assertRaises(ValueError):
            encode(label_octal="203", sdi=0, data=2**19, ssm=0)


class TestBnrScaling(unittest.TestCase):
    def test_altitude_roundtrip(self):
        raw = ALTITUDE.encode_value(35000)
        value = ALTITUDE.decode_value(raw)
        self.assertEqual(value, 35000.0)

    def test_altitude_out_of_range_raises(self):
        with self.assertRaises(ValueError):
            ALTITUDE.encode_value(-5)


if __name__ == "__main__":
    unittest.main()
