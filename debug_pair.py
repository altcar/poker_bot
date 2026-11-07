"""Debug one pairing: action mix and the hands that cost the most."""
import sys
import random
from collections import Counter

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

net = 0
faults = 0
mix = Counter()
worst = []
for rot in (0, 1):
    you, them = Model(), (Opp(seed=0) if opp == "random" else Opp())
    seats = [you, them] if rot == 0 else [them, you]
    for d in range(deals):
        deck = full_deck()
        random.Random(100003 + d).shuffle(deck)
        result = play_hand(seats, deck, [500, 500], 0, 10, BB)
        s = 0 if rot == 0 else 1
        mynet = result.net[s]
        net += mynet
        faults += len(result.faults)
        for a in result.actions:
            if a.player_id == s:
                mix[a.kind] += 1
        if mynet <= -100:
            worst.append((mynet, [str(c) for c in result.hands[s]],
                          [str(c) for c in result.board],
                          [(a.kind, a.player_id, a.amount)
                           for a in result.actions if a.player_id >= 0]))
        if len(worst) > 6:
            worst = sorted(worst, key=lambda x: x[0])[:6]

hands = deals * 2
print(bot, "vs", opp, "bb/100", round(100 * net / BB / hands, 1),
      "faults", faults)
print("actions:", dict(mix))
for w in sorted(worst, key=lambda x: x[0])[:3]:
    print("\nnet", w[0], "hole", w[1], "board", w[2])
    print(w[3][:24])
