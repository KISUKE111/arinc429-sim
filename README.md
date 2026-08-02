# ARINC 429 Simulator (Python, for beginners)

A small, dependency-free Python project that teaches the basics of the
**ARINC 429** avionics data bus by simulating it: encoding/decoding
32-bit words, scaling engineering units (like altitude), and running a
simple bus with a transmitter and multiple filtering receivers.

This is an **educational** project — it models the *data* layer (words,
labels, parity) rather than real electrical/timing behavior.

## What is ARINC 429?

ARINC 429 is the most common avionics data bus standard. Key facts:

- **One-directional**: one transmitter, up to 20 receivers per bus.
- **32-bit words**, sent at 12.5 kbit/s (low speed) or 100 kbit/s (high speed).
- Each word is split into fields:

| Bits  | Field  | Meaning                                   |
|-------|--------|--------------------------------------------|
| 1-8   | Label  | Identifies the parameter (written in octal) |
| 9-10  | SDI    | Source/Destination Identifier               |
| 11-29 | Data   | The actual value (often BNR-scaled)         |
| 30-31 | SSM    | Sign/Status Matrix (validity/sign/test)     |
| 32    | Parity | Odd parity, for basic error detection       |

## Project layout

```
arinc429-sim/
├── arinc429/
│   ├── __init__.py     # public API
│   ├── word.py         # encode()/decode() a 32-bit word
│   ├── bnr.py           # engineering-unit <-> raw data scaling
│   └── bus.py            # Bus / Transmitter / Receiver simulation
├── examples/
│   ├── altitude_broadcast.py
│   └── parity_error_demo.py
├── tests/
│   └── test_word.py
├── README.md
├── LICENSE
└── requirements.txt
```

## Getting started

No external dependencies — just Python 3.8+.

```bash
git clone https://github.com/<your-username>/arinc429-sim.git
cd arinc429-sim
python3 examples/altitude_broadcast.py
python3 examples/parity_error_demo.py
python3 -m unittest discover -s tests -v
```

## Quick usage example

```python
from arinc429 import encode, decode, SSM, ALTITUDE

# Encode altitude = 35,000 ft as label 203
raw_data = ALTITUDE.encode_value(35000)
word = encode(label_octal="203", sdi=0, data=raw_data, ssm=SSM.NORMAL_OPERATION)

# ... word travels across the "bus" ...

decoded = decode(word)
altitude_ft = ALTITUDE.decode_value(decoded.data)
print(altitude_ft)  # 35000.0
```

## Learning path (suggested order)

1. Read `arinc429/word.py` — understand bit layout, encode/decode, parity.
2. Run `examples/parity_error_demo.py` — see how corruption is detected.
3. Read `arinc429/bnr.py` — understand engineering-unit scaling.
4. Run `examples/altitude_broadcast.py` — see a transmitter + filtering receivers.
5. Read `tests/test_word.py` — see how to test bit-level code.
6. **Extend it yourself**: add a new parameter (e.g. airspeed already stubbed
   in `bnr.py`), add a new label, or add a receiver that only reacts to
   `SSM.FAILURE_WARNING`.

## Ideas for extending this project

- Add BCD (Binary Coded Decimal) encoding, the other common ARINC 429 data type.
- Add discrete-word decoding (label-specific bit meanings).
- Simulate two's-complement signed BNR values.
- Add a CLI (`argparse`) to encode/decode words from the terminal.
- Add a simple GUI (tkinter) bus monitor.
- Simulate timing/bus speed and word gaps.

## License

Copyright (c) 2026 Mohammed amine mohammadi. All Rights Reserved.
