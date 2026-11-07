"""Quantified scoreboard for the A-E bots.

Score (0-100), fixed rubric so runs are comparable:

  50  strength      mean bb/100 vs the six dummies, -10 -> 0, +60 -> 50
  15  hard table    mean bb/100 vs tight/equity/shove, -10 -> 0, +40 -> 15
  20  cross-play    mean bb/100 in the A-E round robin, -20 -> 0, +20 -> 20
  10  safety        no faults, slowest move under 2 s
   5  reserved      council marks (added by hand after review)

Usage:
    python score_bots.py --deals 200
    python score_bots.py --deals 400 --only a c e
"""

import argparse
import importlib
import random
import time

from arena.dummies import DUMMIES, EquityBot, TightBot, ShoveBot
from card_utils import full_deck
from engine import play_hand

from botcore import FULL, encode

BB = 20
STACK = 500

BOTS = ["a", "b", "c", "d", "e"]
HARD = ("tight", "equity", "shove")


def deck(key):
    cards = full_deck()
    random.Random(key).shuffle(cards)
    return cards


def build(spec):
    if spec in DUMMIES:
        cls = DUMMIES[spec]
        try:
            return cls(seed=0)
        except TypeError:
            return cls()
    module = importlib.import_module(f"model_{spec}")
    return module.Model()


def pair(label_a, label_b, deals, seed):
    """Duplicate heads-up match: every deck played from both seats.

    Returns (net_a, faults, seconds).  Models survive across hands inside a
    rotation, as the organisers' engine does.
    """
    net_a = 0.0
    faults = 0
    seconds = 0.0
    for rotation in (0, 1):
        a = build(label_a)
        b = build(label_b)
        seats = [a, b] if rotation == 0 else [b, a]
        for d in range(deals):
            cards = deck(seed * 100003 + d)
            start = time.perf_counter()
            result = play_hand(seats, cards, [STACK, STACK], 0, 10, BB)
            seconds = max(seconds, time.perf_counter() - start)
            faults += len(result.faults)
            net_a += result.net[0] if rotation == 0 else result.net[1]
    hands = deals * 2
    return 100.0 * net_a / BB / hands, faults, seconds


def linear(value, low, high, points):
    if value <= low:
        return 0.0
    if value >= high:
        return points
    return points * (value - low) / (high - low)


def run(deals, only, seed=0):
    chosen = [b for b in BOTS if b in only] if only else list(BOTS)
    rows = {}
    for bot in chosen:
        dummies = {}
        for dummy in DUMMIES:
            bb, faults, secs = pair(bot, dummy, deals, seed)
            dummies[dummy] = (bb, faults, secs)
        rows[bot] = {"dummies": dummies}

    cross = {}
    if len(chosen) > 1:
        for i, a in enumerate(chosen):
            for b in chosen[i + 1:]:
                bb, faults, secs = pair(a, b, deals, seed)
                cross[(a, b)] = (bb, -bb, faults, secs)

    print(f"\n{'bot':>4} | " + " ".join(f"{d:>8}" for d in DUMMIES)
          + f" | {'all':>8} {'hard':>8} {'fault':>5} {'sec':>6} | {'SCORE':>6}")
    print("-" * 104)
    scores = {}
    for bot in chosen:
        vals = rows[bot]["dummies"]
        allbb = sum(v[0] for v in vals.values()) / len(vals)
        hardbb = sum(vals[d][0] for d in HARD) / len(HARD)
        faults = sum(v[1] for v in vals.values())
        secs = max(v[2] for v in vals.values())

        crossbb = 0.0
        for (a, b), (bb_ab, bb_ba, f, s) in cross.items():
            if a == bot:
                crossbb += bb_ab
            elif b == bot:
                crossbb += bb_ba
        if cross:
            crossbb /= max(1, sum(1 for pair_ in cross if bot in pair_))

        s_strength = linear(allbb, -10, 60, 50)
        s_hard = linear(hardbb, -10, 40, 15)
        s_cross = linear(crossbb, -20, 20, 20) if cross else 10.0
        s_safe = 10.0 if (faults == 0 and secs < 2.0) else 0.0
        total = s_strength + s_hard + s_cross + s_safe
        scores[bot] = total
        print(f"{bot:>4} | "
              + " ".join(f"{vals[d][0]:>+8.1f}" for d in DUMMIES)
              + f" | {allbb:>+8.1f} {hardbb:>+8.1f} {faults:>5} "
              f"{secs:>6.2f} | {total:>6.1f}")

    if cross:
        print("\ncross-play (row bot bb/100 vs column)")
        print(f"{'':>4} | " + " ".join(f"{b:>7}" for b in chosen))
        for a in chosen:
            cells = []
            for b in chosen:
                if a == b:
                    cells.append(f"{'-':>7}")
                else:
                    key = (a, b) if (a, b) in cross else (b, a)
                    bb = cross[key][0] if key[0] == a else cross[key][1]
                    cells.append(f"{bb:>+7.1f}")
            print(f"{a:>4} | " + " ".join(cells))

    best = max(scores, key=scores.get)
    print(f"\nbest: {best}  score {scores[best]:.1f}/95 (council 5 pending)")
    return scores


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--deals", type=int, default=200)
    parser.add_argument("--only", nargs="*", default=None)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    run(args.deals, args.only, args.seed)


if __name__ == "__main__":
    main()
