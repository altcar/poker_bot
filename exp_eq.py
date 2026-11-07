"""Fast sweep aimed at the `equity` dummy (the current leak)."""
import sys

import tune
import score_bots as s

CONFIGS = [
    ("baseline", {}),
    ("defend 1.0", {"DEFEND": 1.0, "CALL_FOUR": 1.0}),
    ("open .0 defend 1.0", {"OPEN": 0.0, "DEFEND": 1.0, "CALL_FOUR": 1.0}),
    ("open .8 defend 1.0", {"OPEN": 0.8, "DEFEND": 1.0, "CALL_FOUR": 1.0}),
    ("margin 0", {"MARGIN": 0.0, "DEFEND": 1.0, "CALL_FOUR": 1.0}),
    ("value .55", {"VALUE": 0.55, "RAISE": 0.55, "DEFEND": 1.0,
                   "CALL_FOUR": 1.0}),
    ("iters 400", {"ITERATIONS": 400, "DEFEND": 1.0, "CALL_FOUR": 1.0}),
    ("no bluff, v.58", {"BLUFF": 0.0, "VALUE": 0.58, "RAISE": 0.58,
                        "DEFEND": 1.0, "CALL_FOUR": 1.0}),
    ("defend 1.0 3bet .05", {"DEFEND": 1.0, "CALL_FOUR": 1.0,
                              "THREE_BET": 0.05}),
]

deals = int(sys.argv[1]) if len(sys.argv) > 1 else 40
for name, params in CONFIGS:
    s.build = tune.build_with(params)
    bb, faults, secs = s.pair("tune", "equity", deals, 0)
    print(f"{name:<24} equity {bb:+8.1f}  faults {faults}  {secs:.2f}s",
          flush=True)
