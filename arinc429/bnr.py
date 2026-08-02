"""
arinc429.bnr
============

Helpers for BNR (Binary, i.e. two's-complement-like fractional binary)
numeric encoding, which is how most analog parameters (altitude, speed,
heading, etc.) are represented on ARINC 429.

Each parameter's ICD (Interface Control Document) defines a "resolution"
(a.k.a. LSB weight) — the real-world value represented by the least
significant of the 19 data bits. To encode a value:

    raw_data = round(value / resolution)

To decode:

    value = raw_data * resolution

Negative values use sign-magnitude in real ICDs (with the sign folded
into the top data bit / SSM), but for an educational simulator we keep
it simple: we treat the 19-bit data field as an unsigned magnitude and
use the SSM to flag failure/test/normal, which mirrors how many student
labs use it. Advanced users can extend this module for two's complement.
"""

from dataclasses import dataclass


@dataclass
class BnrParameter:
    """Describes how to scale one ARINC 429 parameter.

    Example: Altitude, label 203, range 0-131072 ft, resolution 1 ft.
    """
    name: str
    label_octal: str
    resolution: float   # engineering units per LSB
    num_bits: int = 19  # data field width

    def encode_value(self, value: float) -> int:
        """Convert an engineering-unit value into a raw N-bit integer."""
        max_value = (2 ** self.num_bits) - 1
        raw = round(value / self.resolution)
        if raw < 0 or raw > max_value:
            raise ValueError(
                f"{self.name}: value {value} out of range for "
                f"{self.num_bits}-bit field with resolution {self.resolution}"
            )
        return raw

    def decode_value(self, raw: int) -> float:
        """Convert a raw N-bit integer back into an engineering-unit value."""
        return raw * self.resolution


# A few common, real-world-inspired example parameters for teaching.
# (Resolutions are illustrative/simplified for classroom use.)
ALTITUDE = BnrParameter(name="Altitude", label_octal="203", resolution=1.0)
AIRSPEED = BnrParameter(name="Computed Airspeed", label_octal="206", resolution=0.125)
HEADING = BnrParameter(name="Magnetic Heading", label_octal="320", resolution=0.0055)
