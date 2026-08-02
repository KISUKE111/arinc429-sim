"""
arinc429.word
=============

Core building block of the simulator: encoding and decoding a single
32-bit ARINC 429 word.

A word layout (bit 1 = LSB, transmitted first, bit 32 = MSB, transmitted last):

    Bit  1- 8  : Label      (8 bits, conventionally written/read in OCTAL)
    Bit  9-10  : SDI        (Source/Destination Identifier, 2 bits)
    Bit 11-29  : Data       (19 bits, BNR - Binary if numeric data)
    Bit 30-31  : SSM        (Sign/Status Matrix, 2 bits)
    Bit 32     : Parity     (odd parity over bits 1-31)

This module deliberately keeps things simple and explicit (no bit-level
cleverness) so beginners can follow every step.
"""

from dataclasses import dataclass
from enum import IntEnum


class SSM(IntEnum):
    """Sign/Status Matrix values for BNR (binary numeric) data words.

    NOTE: The *meaning* of SSM bits depends on the data type (BNR, BCD,
    discrete, etc). This is the common BNR interpretation, good enough
    for an educational simulator.
    """
    FAILURE_WARNING = 0b00
    NO_COMPUTED_DATA = 0b01
    FUNCTIONAL_TEST = 0b10
    NORMAL_OPERATION = 0b11


@dataclass
class Arinc429Word:
    """A decoded, human-friendly view of one ARINC 429 word."""
    label_octal: str   # e.g. "203" (octal string, as printed on ICDs)
    sdi: int            # 0-3
    data: int           # raw 19-bit unsigned data field value
    ssm: int             # 0-3
    parity_ok: bool
    raw: int             # the full 32-bit integer, for reference

    def __str__(self):
        return (f"Label={self.label_octal} SDI={self.sdi} "
                f"Data={self.data} SSM={SSM(self.ssm).name} "
                f"Parity={'OK' if self.parity_ok else 'BAD'} "
                f"Raw=0x{self.raw:08X}")


def _octal_label_to_int(label_octal: str) -> int:
    """Labels are conventionally written in octal (e.g. '203', '270')."""
    value = int(label_octal, 8)
    if not (0 <= value <= 0o377):
        raise ValueError("Label must fit in 8 bits (000-377 octal)")
    return value


def _odd_parity_bit(value_31_bits: int) -> int:
    """Return the single parity bit that makes the total number of
    1-bits (including this new bit) odd. ARINC 429 uses ODD parity.
    """
    ones = bin(value_31_bits).count("1")
    return 0 if ones % 2 == 1 else 1


def encode(label_octal: str, sdi: int, data: int, ssm: int) -> int:
    """Build a 32-bit ARINC 429 word from its fields.

    Args:
        label_octal: label as an octal string, e.g. "203"
        sdi: 0-3
        data: 0 - 524287 (19-bit unsigned value, caller is responsible
              for any BNR scaling/encoding beforehand)
        ssm: 0-3 (see SSM enum)

    Returns:
        32-bit integer representing the word (parity already set).
    """
    label = _octal_label_to_int(label_octal)

    if not (0 <= sdi <= 0b11):
        raise ValueError("SDI must be 0-3")
    if not (0 <= data <= 0x7FFFF):  # 19 bits
        raise ValueError("Data must fit in 19 bits (0-524287)")
    if not (0 <= ssm <= 0b11):
        raise ValueError("SSM must be 0-3")

    word = 0
    word |= label            # bits 1-8
    word |= sdi << 8         # bits 9-10
    word |= data << 10       # bits 11-29
    word |= ssm << 29        # bits 30-31

    parity = _odd_parity_bit(word)
    word |= parity << 31     # bit 32

    return word


def decode(raw_word: int) -> Arinc429Word:
    """Split a 32-bit integer back into its ARINC 429 fields."""
    if not (0 <= raw_word <= 0xFFFFFFFF):
        raise ValueError("raw_word must be a 32-bit unsigned integer")

    label = raw_word & 0xFF
    sdi = (raw_word >> 8) & 0b11
    data = (raw_word >> 10) & 0x7FFFF
    ssm = (raw_word >> 29) & 0b11
    parity_bit = (raw_word >> 31) & 0b1

    # Recompute what parity *should* be over bits 1-31, compare to bit 32
    bits_1_to_31 = raw_word & 0x7FFFFFFF
    expected_parity = _odd_parity_bit(bits_1_to_31)
    parity_ok = (parity_bit == expected_parity)

    return Arinc429Word(
        label_octal=format(label, "03o"),
        sdi=sdi,
        data=data,
        ssm=ssm,
        parity_ok=parity_ok,
        raw=raw_word,
    )
