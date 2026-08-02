"""
Example: show what happens when a word gets corrupted in transit
and how a receiver can detect it via the parity bit.

Run with:
    python examples/parity_error_demo.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from arinc429 import encode, decode, SSM


def main():
    good_word = encode(label_octal="270", sdi=0, data=42, ssm=SSM.NORMAL_OPERATION)
    print("Good word:      ", decode(good_word))

    # Simulate electrical noise flipping one data bit (but not fixing parity)
    corrupted_word = good_word ^ (1 << 12)
    print("Corrupted word: ", decode(corrupted_word))

    decoded = decode(corrupted_word)
    if not decoded.parity_ok:
        print("\n-> Receiver would REJECT this word: parity check failed.")


if __name__ == "__main__":
    main()
