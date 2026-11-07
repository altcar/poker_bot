"""Turn `python -m evals` output into a single 0-100 score.

Mapping (fixed, so runs are comparable):

    per-opponent = clip(50 + bb_per_100, 0, 100)
    score        = mean of the six per-opponent values

So 0 bb/100 is 50, +20 is 70, +50 is 100, and -50 is 0.  The "hard" score
uses only tight / equity / shove.

Usage:
    python -m evals > run.txt
    python eval_score.py run.txt
    python eval_score.py eval_results.txt        # parses every variant block
"""

import re
import sys

LINE = re.compile(
    r"^\s*(?P<name>[A-Za-z][\w .-]*?)\s+"
    r"(?P<bb>[+-]?\d+(?:\.\d+)?)\s*[±+-]\s*(?P<ci>\d+(?:\.\d+)?)\s+"
    r"(?P<verdict>ahead|behind|unclear)\s+"
    r"(?P<hands>\d+)\s+(?P<faults>\d+)\s+(?P<slow>[\d.]+)s\s*$"
)
HARD = {"tight", "equity", "shove"}


def clip(x):
    return max(0.0, min(100.0, x))


def score_rows(rows):
    per = {name: clip(50.0 + bb) for name, (bb, _, _, _) in rows.items()}
    overall = sum(per.values()) / len(per)
    hard = [per[n] for n in per if n in HARD]
    hard_score = sum(hard) / len(hard) if hard else 0.0
    faults = sum(row[2] for row in rows.values())
    slowest = max(row[3] for row in rows.values())
    return overall, hard_score, faults, slowest


def parse(text):
    """Returns [(label, rows)] for one or more evals tables."""
    blocks = []
    label = "run"
    rows = {}
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("===="):
            if rows:
                blocks.append((label, rows))
            label = stripped.strip("= ").strip()
            rows = {}
            continue
        match = LINE.match(line)
        if not match:
            continue
        name = match.group("name").strip()
        rows[name] = (
            float(match.group("bb")),
            float(match.group("ci")),
            int(match.group("faults")),
            float(match.group("slow")),
        )
    if rows:
        blocks.append((label, rows))
    return blocks


def main(argv):
    path = argv[1] if len(argv) > 1 else None
    text = open(path, encoding="utf-8", errors="replace").read() if path \
        else sys.stdin.read()
    blocks = parse(text)
    if not blocks:
        print("no evals rows found")
        return 1
    for label, rows in blocks:
        overall, hard, faults, slow = score_rows(rows)
        mark = "PASS" if overall > 70 else "FAIL"
        print(f"{label:<24} score {overall:6.1f}/100  hard {hard:6.1f}  "
              f"faults {faults}  slowest {slow:.2f}s  [{mark}]")
        for name, (bb, ci, _, _) in rows.items():
            print(f"    {name:<10} {bb:+8.1f} ± {ci:<6.1f}  "
                  f"-> {clip(50.0 + bb):5.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
