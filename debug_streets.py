"""Where do the chips go? Bucket net by street reached and last aggressor."""
import sys
import random
from collections import Counter, defaultdict

from card_utils import full_deck
from engine import play_hand
from arena.dummies import DUMMIES
import importlib

BB = 20
bot = sys.argv[1] if len(sys.argv) > 1 else "d"
opp = sys.argv[2] if len(sys.argv) > 2 else "random"
deals = int(sys.argv[3]) if len(sys.argv) > 3 else 300

Model = importlib.import_module(f"model_{bot}").Model
Opp = DUMMIES[opp]
buckets = defaultdict(lambda: [0, 0])
showdown = Counter()

for rot in (0, 1):
    you, them = Model(), (Opp(seed=0) if opp == "random" else Opp())
    seats = [you, them] if rot == 0 else [them, you]
    for d in range(deals):
        deck = full_deck()
        random.Random(100003 + d).shuffle(deck)
        result = play_hand(seats, deck, [500, 500], 0, 10, BB)
        s = 0 if rot == 0 else 1
        net = result.net[s]
        street = {0: "pre", 3: "flop", 4: "turn", 5: "river"}[len(result.board)]
        # Was the last aggressive action ours?
        last_raise = None
        for a in result.actions:
            if a.kind == "raise":
                last_raise = a.player_id
        who = "us" if last_raise == s else ("them" if last_raise is not None else "none")
        buckets[(street, who)][0] += net
        buckets[(street, who)][1] += 1
        if len(result.board) == 5 and len([1 for a in result.actions
                                           if a.kind == "reveal_card" and a.player_id >= 0]) >= 4:
            showdown[(who, net > 0)] += 1

total_hands = deals * 2
print(bot, "vs", opp, "bb/100", round(100 * sum(v[0] for v in buckets.values()) / BB / total_hands, 1))
for key in sorted(buckets):
    chips, n = buckets[key]
    print(f"{key[0]:<5} last={key[1]:<4} n={n:<5} net={chips:<8} "
          f"bb/100={100 * chips / BB / total_hands:>7.1f}")
print("showdowns (last aggressor, we won):", dict(showdown))
