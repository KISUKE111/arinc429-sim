"""
arinc429.bus
============

A tiny in-memory simulation of an ARINC 429 bus:

- One Transmitter puts words "on the bus".
- One or more Receivers "listen" and can filter by label, just like a
  real avionics LRU (Line Replaceable Unit) that's only wired to care
  about a handful of labels out of everything on the bus.

This is intentionally not about timing/electrical simulation (real
ARINC 429 is 12.5 or 100 kbit/s, unidirectional, differential pair) -
it's about teaching the *data* model: words, labels, filtering.
"""

from typing import Callable, List, Optional
from .word import decode, Arinc429Word


class Receiver:
    """A receiver that only reacts to a chosen set of labels
    (pass label_filter=None to receive everything).
    """

    def __init__(self, name: str, label_filter: Optional[List[str]] = None):
        self.name = name
        self.label_filter = set(label_filter) if label_filter else None
        self.inbox: List[Arinc429Word] = []

    def receive(self, raw_word: int):
        decoded = decode(raw_word)
        if self.label_filter is None or decoded.label_octal in self.label_filter:
            self.inbox.append(decoded)
            print(f"  [{self.name}] received -> {decoded}")

    def last(self) -> Optional[Arinc429Word]:
        return self.inbox[-1] if self.inbox else None


class Bus:
    """The shared medium. Transmitter writes words here; all attached
    receivers get a chance to see every word (and filter it themselves,
    mirroring real hardware wiring)."""

    def __init__(self, name: str = "ARINC429-BUS"):
        self.name = name
        self.receivers: List[Receiver] = []
        self.history: List[int] = []

    def attach(self, receiver: Receiver):
        self.receivers.append(receiver)

    def transmit(self, raw_word: int):
        self.history.append(raw_word)
        decoded = decode(raw_word)
        status = "OK" if decoded.parity_ok else "PARITY ERROR"
        print(f"[{self.name}] TX word: {decoded}  ({status})")
        for r in self.receivers:
            r.receive(raw_word)
