# ARINC 429 Simulator (Python, for beginners)

A small, dependency-free Python project that teaches the basics of the
**ARINC 429** avionics data bus by simulating it: encoding/decoding
32-bit words, scaling engineering units (like altitude), and running a
simple bus with a transmitter and multiple filtering receivers.

This is an **educational** project — it models the *data* layer (words,
labels, parity) rather than real electrical/timing behavior. It's aimed
at students, hobbyists, and engineers who are new to avionics data buses
and want to learn by reading and running real code.

> Copyright (c) 2026 Mohammed [Your Last Name]. All Rights Reserved.
> See [LICENSE](LICENSE) for terms.

---

## Table of contents

- [What is ARINC 429?](#what-is-arinc-429)
- [Why does it still matter?](#why-does-it-still-matter)
- [Word structure, in detail](#word-structure-in-detail)
- [Glossary](#glossary)
- [Project layout](#project-layout)
- [Getting started](#getting-started)
- [Quick usage example](#quick-usage-example)
- [How the simulator maps to real hardware](#how-the-simulator-maps-to-real-hardware)
- [Learning path](#learning-path-suggested-order)
- [Frequently asked questions](#frequently-asked-questions)
- [Ideas for extending this project](#ideas-for-extending-this-project)
- [References](#references)
- [License](#license)

---

## What is ARINC 429?

ARINC 429 is a data transfer standard published by **Aeronautical Radio,
Incorporated (ARINC)**, first introduced in 1977 and still the most
widely used avionics data bus in commercial and business aircraft today.
It defines both the electrical characteristics of the wiring and the
format of the data sent over it.

Key characteristics:

- **Unidirectional / simplex**: each bus has exactly **one transmitter**
  and up to **20 receivers**. Data flows only one way — if a device needs
  to both send and receive, it needs two separate buses (one out, one in).
- **Point-to-multipoint, broadcast-style**: the transmitter doesn't
  address individual receivers. It just puts words on the wire, and
  every receiver decides for itself which labels it cares about.
- **Two speeds**: Low speed (12.5 kbit/s) and High speed (100 kbit/s).
- **Twisted, shielded pair of wires**, using bipolar return-to-zero (RZ)
  signaling with three voltage states (HI, LO, NULL) — this is the
  electrical layer, which this simulator does **not** model.
- **32-bit words** are the atomic unit of data, each carrying one
  parameter (e.g., altitude, airspeed, heading) identified by a **label**.

## Why does it still matter?

Even though newer standards exist (like **ARINC 664 / AFDX**, used on the
Airbus A380 and A350, and **ARINC 825 / CAN bus** for some newer
systems), ARINC 429 remains extremely common because:

- It's simple, robust, and well understood — decades of certified designs
  exist.
- Its low speed and simplex nature make it easy to test, verify, and
  certify to strict aviation safety standards (DO-178C, DO-254).
- Retrofits and legacy aircraft (a huge share of the world's fleet) still
  rely on it heavily.
- It's a great *first* protocol to learn before tackling more complex
  buses, because the entire spec fits in a few pages and the whole word
  format can be explained on one whiteboard — which is exactly why this
  project starts here.

## Word structure, in detail

Every ARINC 429 word is exactly 32 bits, transmitted bit 1 first
(least significant bit first) and bit 32 last:

| Bits  | Field  | Width | Meaning                                              |
|-------|--------|-------|-------------------------------------------------------|
| 1–8   | Label  | 8     | Identifies the parameter. Conventionally written in **octal** (e.g. `203` = altitude on many ICDs). |
| 9–10  | SDI    | 2     | Source/Destination Identifier — can distinguish which system instance sent the word (e.g. Captain vs. First Officer side), or be used as extra data bits depending on the ICD. |
| 11–29 | Data   | 19    | The actual value. Encoded as BNR (Binary), BCD (Binary Coded Decimal), or discrete bits, depending on the parameter. |
| 30–31 | SSM    | 2     | Sign/Status Matrix — validity/sign/test flag (see below). |
| 32    | Parity | 1     | A single **odd parity** bit over bits 1–31, for basic error detection. |

### Data encoding types

This project currently implements **BNR (Binary)** encoding, which is
the most common for continuous analog-style parameters (altitude,
speed, heading, temperature, etc.). Each parameter's ICD defines a
**resolution** (the real-world value represented by the least
significant data bit):

```
raw_data  = round(engineering_value / resolution)
engineering_value = raw_data * resolution
```

The other common type is **BCD (Binary Coded Decimal)**, typically used
for things like frequency tuning (e.g. VOR/NAV radio frequencies) where
each group of 4 bits represents one decimal digit. BCD is **not yet
implemented** in this project — it's listed under
[Ideas for extending this project](#ideas-for-extending-this-project).

### SSM (Sign/Status Matrix)

For BNR data, the 2-bit SSM field commonly means:

| Value | Name              | Meaning                                    |
|-------|-------------------|---------------------------------------------|
| `00`  | Failure/Warning   | The data is invalid — do not use it.        |
| `01`  | No Computed Data  | The source hasn't computed a value yet.     |
| `10`  | Functional Test   | The system is in a test mode.               |
| `11`  | Normal Operation  | The data is valid and trustworthy.          |

**This is one of the most important lessons of the whole project**:
avionics data is never "just a number" — it always comes bundled with a
validity/status flag, and a well-behaved receiver must check the SSM
before trusting or displaying the data.

### Parity

ARINC 429 uses a single **odd parity** bit (bit 32): the transmitter
sets it so that the total number of `1` bits across all 32 bits is odd.
A receiver recomputes this on arrival — if the count comes out even, at
least one bit was corrupted in transit (usually from electrical noise),
and the word should be discarded. This is a very old but still effective
first line of defense; it can detect any single-bit error (and many
multi-bit errors), though not all of them.

## Glossary

| Term | Meaning |
|------|---------|
| **LRU** | Line Replaceable Unit — a self-contained avionics box (e.g. an Air Data Computer, a display) that can be swapped out as a single unit. |
| **ICD** | Interface Control Document — the specification that defines exactly which labels, scaling, and SSM meanings a specific aircraft/system uses. Every aircraft program has its own ICDs. |
| **Label** | An 8-bit octal-conventioned identifier for a parameter (e.g. `203` = altitude on many platforms — but always check the specific ICD, since label assignments can vary by system). |
| **SDI** | Source/Destination Identifier — 2 bits, often used to indicate which redundant system sent the word. |
| **SSM** | Sign/Status Matrix — 2-bit validity/status flag. |
| **BNR** | Binary — numeric encoding for continuous values, scaled by a resolution. |
| **BCD** | Binary Coded Decimal — numeric encoding where each 4-bit group is one decimal digit. |
| **AFDX / ARINC 664** | A newer, higher-speed, switched Ethernet-based avionics network standard, used alongside or instead of ARINC 429 on newer aircraft. |

## Project layout

```
arinc429-sim/
├── arinc429/
│   ├── __init__.py     # public API
│   ├── word.py         # encode()/decode() a 32-bit word, parity logic
│   ├── bnr.py           # engineering-unit <-> raw data scaling
│   └── bus.py            # Bus / Transmitter / Receiver simulation
├── examples/
│   ├── altitude_broadcast.py   # transmitter + multiple filtering receivers
│   └── parity_error_demo.py    # simulated bit corruption + detection
├── tests/
│   └── test_word.py     # unit tests for encode/decode/parity/scaling
├── README.md
├── LICENSE
└── requirements.txt      # no external dependencies (stdlib only)
```

## Getting started

No external dependencies — just **Python 3.8+** (standard library only).

```bash
git clone https://github.com/<your-username>/arinc429-sim.git
cd arinc429-sim
python3 examples/altitude_broadcast.py
python3 examples/parity_error_demo.py
python3 -m unittest discover -s tests -v
```

On Windows PowerShell, use `python` instead of `python3`, and backslashes
in paths are handled automatically by Python — no changes needed.

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

## How the simulator maps to real hardware

| Real-world concept | This project |
|---|---|
| Air Data Computer transmitting altitude | `Bus.transmit(word)` |
| A display or autopilot wired to receive certain labels | `Receiver(name, label_filter=[...])` |
| Twisted-pair wire carrying electrical signals | *Not modeled* — words are just passed as Python integers in memory |
| Bus speed (12.5 / 100 kbit/s) and timing gaps | *Not modeled* — this project focuses purely on the data/word format |
| Electrical noise corrupting a bit | Simulated manually in `parity_error_demo.py` via `raw_word ^ (1 << n)` |
| ICD-defined scaling per parameter | `BnrParameter` objects in `bnr.py` (e.g. `ALTITUDE`, `AIRSPEED`, `HEADING`) |

This project is intentionally scoped to the **data/word layer** — the
part most beginners actually need to understand first. The electrical
and timing layers are a separate (and much more hardware-specific)
topic.

## Learning path (suggested order)

1. Read `arinc429/word.py` — understand bit layout, encode/decode, parity.
2. Run `examples/parity_error_demo.py` — see how corruption is detected.
3. Read `arinc429/bnr.py` — understand engineering-unit scaling.
4. Run `examples/altitude_broadcast.py` — see a transmitter + filtering receivers.
5. Read `tests/test_word.py` — see how to test bit-level code.
6. **Extend it yourself**: add a new parameter (e.g. airspeed already stubbed
   in `bnr.py`), add a new label, or add a receiver that only reacts to
   `SSM.FAILURE_WARNING`.

## Frequently asked questions

**Q: Is this suitable for real avionics development or certification work?**
No. This is an educational simulator for learning the data format. Real
avionics software must comply with standards like DO-178C and be
developed against a specific aircraft's certified ICDs.

**Q: Why octal for labels?**
It's simply the industry convention — every ARINC 429 ICD you'll ever
read prints labels in octal, so this project follows that convention to
build the habit early.

**Q: Does label 203 always mean altitude?**
Not necessarily — label assignments can vary between aircraft programs
and manufacturers. The specific ICD is always the source of truth. This
project uses label 203 for altitude as a common, illustrative example.

**Q: Why 19 data bits specifically?**
That's simply how the ARINC 429 word format allocates its 32 bits: 8 for
label, 2 for SDI, 19 for data, 2 for SSM, 1 for parity — the standard
doesn't leave room to change this.

**Q: Can I simulate negative values (e.g. -500 ft)?**
Not yet with the current `BnrParameter` implementation, which treats
data as unsigned. Real ICDs typically handle sign via two's complement
or a dedicated sign bit within the data field — this is listed as a
possible extension below.

## References

These are good next steps if you want to go deeper than this project:
- ARINC Specification 429, Parts 1–3 (published by ARINC/Aeronautical
  Radio, Inc. — the official standard, available for purchase through
  SAE/ARINC).
- Public ARINC 429 tutorials from avionics test-equipment vendors
  (search "ARINC 429 tutorial") — useful for cross-checking label/SSM
  conventions used on specific real aircraft.

## License

Copyright (c) 2026 Mohammed amine mohammadi. All Rights Reserved.
See [LICENSE](LICENSE) for full terms.