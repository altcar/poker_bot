"""Sanity + speed checks for botcore.eval7 against the repo's evaluate()."""
import random
import time

from card_utils import Card, evaluate
from botcore import encode, eval7, equity, PERCENTILE, preflop_class

DECK = [Card(r, s) for r in "23456789TJQKA" for s in "CDHS"]
INTS = [encode(c) for c in DECK]
assert len(set(INTS)) == 52


def from_int(c):
    return DECK[INTS.index(c)]


rng = random.Random(7)
# 1. correctness on 3000 random 7-card sets
bad = 0
start = time.perf_counter()
for _ in range(3000):
    cs = rng.sample(range(52), 7)
    mine = eval7(cs)
    theirs = evaluate([DECK[c] for c in cs])
    # compare category + tiebreakers, ignore extra category slot
    if mine != tuple(theirs):
        bad += 1
        if bad < 5:
            print("MISMATCH", [str(DECK[c]) for c in cs], mine, theirs)
print("mismatches:", bad)

n = 20000
t = time.perf_counter()
for _ in range(n):
    eval7(rng.sample(range(52), 7))
fast = (time.perf_counter() - t) / n
print(f"eval7: {fast*1e6:.2f} us")

t = time.perf_counter()
for _ in range(300):
    evaluate([DECK[c] for c in rng.sample(range(52), 7)])
slow = (time.perf_counter() - t) / 300
print(f"engine evaluate: {slow*1e6:.1f} us  ({slow/fast:.0f}x slower)")

t = time.perf_counter()
rng2 = random.Random(1)
for _ in range(20):
    equity([0, 5], [10, 20, 30, 40], 1, rng2, iterations=500)
ms = (time.perf_counter() - t) / 20 * 1000
print(f"equity 500 iters, 1 opp: {ms:.2f} ms")

print("classes:", len(PERCENTILE), "AA", PERCENTILE["AA"], "72o", PERCENTILE["72o"])
