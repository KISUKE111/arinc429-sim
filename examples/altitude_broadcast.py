"""
Example: simulate an Air Data Computer (ADC) broadcasting altitude
(label 203) on an ARINC 429 bus, received by a Display and an Autopilot,
while a third receiver only cares about a different label and ignores it.

Run with:
    python examples/altitude_broadcast.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from arinc429 import encode, ALTITUDE, SSM, Bus, Receiver


def main():
    bus = Bus(name="Flight-Data-Bus")

    display = Receiver(name="PFD-Display", label_filter=["203"])
    autopilot = Receiver(name="Autopilot", label_filter=["203"])
    # This one listens for airspeed (label 206) and will ignore altitude
    airspeed_only = Receiver(name="Airspeed-Indicator", label_filter=["206"])

    bus.attach(display)
    bus.attach(autopilot)
    bus.attach(airspeed_only)

    altitudes_ft = [0, 1500, 10000, 35000, 41000]

    for alt in altitudes_ft:
        raw_data = ALTITUDE.encode_value(alt)
        word = encode(
            label_octal=ALTITUDE.label_octal,
            sdi=0,
            data=raw_data,
            ssm=SSM.NORMAL_OPERATION,
        )
        bus.transmit(word)
        print()

    print("Autopilot's last known altitude (decoded back to feet):")
    last = autopilot.last()
    if last:
        print(f"  {ALTITUDE.decode_value(last.data)} ft")


if __name__ == "__main__":
    main()
