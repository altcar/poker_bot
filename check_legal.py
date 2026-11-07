"""Legality gate for every variant, mirroring tests/test_model.py.

Builds each model, plays heads-up against every dummy, a 6-handed table and
a short-stack table, and reports any fault (exception, illegal move).
"""
import importlib
import random

from arena.dummies import DUMMIES
from card_utils import full_deck
from engine import play_hand

BOTS = ["a", "b", "c", "d", "e"]


def fresh(spec):
    if spec in DUMMIES:
        cls = DUMMIES[spec]
        try:
            return cls(seed=0)
        except TypeError:
            return cls()
    return importlib.import_module(f"model_{spec}").Model()


def run_table(specs, deals, stack, label):
    faults = {}
    for d in range(deals):
        deck = full_deck()
        random.Random(5000 + d).shuffle(deck)
        seats = [fresh(spec) for spec in specs]
        result = play_hand(seats, deck, [stack] * len(specs), 0, 10, 20)
        for seat, why in result.faults.items():
            faults.setdefault(specs[seat], why)
    status = "ok" if not faults else "FAULT"
    print(f"  {label:<28} {status}")
    for who, why in faults.items():
        print(f"      {who}: {why}")
    return not faults


def main():
    ok = True
    for bot in BOTS:
        print(f"model_{bot}")
        for dummy in DUMMIES:
            ok &= run_table([bot, dummy], 8, 500, f"HU vs {dummy}")
        table = [bot] + [d for d in DUMMIES if d != "equity"]
        ok &= run_table(table, 3, 500, "6-handed")
        ok &= run_table([bot, "shove", "random", "call"], 8, 60, "short stacks")
    print("\nALL LEGAL" if ok else "\nFAULTS FOUND")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
