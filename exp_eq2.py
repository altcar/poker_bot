"""Second sweep: no bluff, thinner value, bigger sizes vs the equity bot."""
import sys

import tune
import score_bots as s

BASE = {"BLUFF": 0.0, "DEFEND": 1.0, "CALL_FOUR": 1.0, "OPEN": 0.8}

CONFIGS = [
    ("v.58 size .75", {**BASE, "VALUE": 0.58, "RAISE": 0.58}),
    ("v.58 size 1.0", {**BASE, "VALUE": 0.58, "RAISE": 0.58,
                       "VALUE_SIZE": 1.0}),
    ("v.58 size 1.25", {**BASE, "VALUE": 0.58, "RAISE": 0.58,
                        "VALUE_SIZE": 1.25}),
    ("v.55 size 1.0 r.55", {**BASE, "VALUE": 0.55, "RAISE": 0.55,
                            "VALUE_SIZE": 1.0}),
    ("v.60 size 1.0 r.60", {**BASE, "VALUE": 0.60, "RAISE": 0.60,
                            "VALUE_SIZE": 1.0}),
    ("v.50 size 1.2 r.55", {**BASE, "VALUE": 0.50, "RAISE": 0.55,
                            "VALUE_SIZE": 1.2}),
    ("v.58 size 1.0 it300", {**BASE, "VALUE": 0.58, "RAISE": 0.58,
                             "VALUE_SIZE": 1.0, "ITERATIONS": 300}),
]

deals = int(sys.argv[1]) if len(sys.argv) > 1 else 60
for name, params in CONFIGS:
    s.build = tune.build_with(params)
    bb, faults, secs = s.pair("tune", "equity", deals, 0)
    print(f"{name:<24} equity {bb:+8.1f}  faults {faults}  {secs:.2f}s",
          flush=True)
