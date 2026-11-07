"""Parameter sweep against the informative dummies."""
import itertools
import sys

import score_bots as s
from policy import PokerBot

OPPS = ("equity", "tight", "shove", "random", "call")


def trial(name, params, deals=100):
    s.build = build_with(params)
    cells = []
    total = 0.0
    for opp in OPPS:
        bb, faults, secs = s.pair("tune", opp, deals, 0)
        cells.append(f"{opp[:4]} {bb:+7.1f}")
        total += bb
    print(f"{name:<22} " + "  ".join(cells)
          + f"  | mean {total/len(OPPS):+7.1f} faults {faults}")
    return total / len(OPPS)


def build_with(params):
    def build(spec):
        if spec == "tune":
            attrs = dict(TIER=2, OPEN=0.0, THREE_BET=0.0, DEFEND=0.99,
                         CALL_FOUR=0.99, VALUE=0.76, RAISE=0.76,
                         MARGIN=0.0, BLUFF=0.0, ITERATIONS=200)
            attrs.update(params)
            return type("Tuned", (PokerBot,), attrs)()
        import importlib
        from arena.dummies import DUMMIES
        if spec in DUMMIES:
            cls = DUMMIES[spec]
            try:
                return cls(seed=0)
            except TypeError:
                return cls()
        return importlib.import_module(f"model_{spec}").Model()
    return build


if __name__ == "__main__":
    deals = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    configs = [
        ("o55 d85 3b12", {"OPEN": 0.55, "DEFEND": 0.85, "THREE_BET": 0.12}),
        ("  + value.64", {"OPEN": 0.55, "DEFEND": 0.85, "THREE_BET": 0.12,
                          "VALUE": 0.64, "RAISE": 0.64}),
        ("  + no commit", {"OPEN": 0.55, "DEFEND": 0.85, "THREE_BET": 0.12,
                            "VALUE": 0.64, "RAISE": 0.64, "COMMIT": False}),
        ("  + no shoveclose", {"OPEN": 0.55, "DEFEND": 0.85, "THREE_BET": 0.12,
                                "VALUE": 0.64, "RAISE": 0.64,
                                "SHOVE_CLOSE": False}),
        ("  + no mdf", {"OPEN": 0.55, "DEFEND": 0.85, "THREE_BET": 0.12,
                         "VALUE": 0.64, "RAISE": 0.64, "USE_MDF": False}),
        ("o70 d90 3b16 v.66", {"OPEN": 0.70, "DEFEND": 0.90, "THREE_BET": 0.16,
                                "VALUE": 0.66, "RAISE": 0.66}),
        ("o45 d75 3b10 v.62", {"OPEN": 0.45, "DEFEND": 0.75, "THREE_BET": 0.10,
                                "VALUE": 0.62, "RAISE": 0.62}),
        ("o55 d95 3b12 v.64", {"OPEN": 0.55, "DEFEND": 0.95, "THREE_BET": 0.12,
                                "VALUE": 0.64, "RAISE": 0.64}),
        ("all off + v.64", {"OPEN": 0.55, "DEFEND": 0.85, "THREE_BET": 0.12,
                             "VALUE": 0.64, "RAISE": 0.64, "COMMIT": False,
                             "SHOVE_CLOSE": False, "USE_MDF": False}),
        ("o55 + bluff.10", {"OPEN": 0.55, "DEFEND": 0.85, "THREE_BET": 0.12,
                             "VALUE": 0.64, "RAISE": 0.64, "BLUFF": 0.10}),
    ]
    for name, params in configs:
        trial(name, params, deals)
