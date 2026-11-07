"""Plan A - conservative, deterministic hand-strength heuristic.

No Monte-Carlo, no opponent modelling.  Very hard to fault, cheap on the
clock, and enough to punish the fold/call dummies.
"""

from policy import PokerBot


class Model(PokerBot):
    TIER = 1

    OPEN = 0.80
    THREE_BET = 0.09
    DEFEND = 1.0
    FOUR_BET = 0.03
    CALL_FOUR = 1.0

    VALUE = 0.58
    RAISE = 0.58
    MARGIN = 0.0
    BLUFF = 0.0
    VALUE_SIZE = 1.25
    ITERATIONS = 0
