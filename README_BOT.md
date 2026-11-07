# Poker bot — A–E build (handoff)

Fork: https://github.com/altcar/poker_bot (fork of
Manchester-AI-Society/poker_bot).

Everything here is additive: `model.py` and the engine files are untouched.
The bots live in `model_a.py` … `model_e.py` on a shared engine
(`botcore.py` + `policy.py`).

## Why these five

| File | Plan | What it is |
|---|---|---|
| `model_a.py` | A – conservative | Category heuristic, no Monte-Carlo, no opponent model. Cheapest and safest. |
| `model_b.py` | B – workhorse | 25 bb preflop ranges + Monte-Carlo equity vs random hands + pot odds. |
| `model_c.py` | C – adaptive | B plus per-team counters (VPIP/PFR/aggression) driving a range filter and archetypes. |
| `model_d.py` | D – mixed | C plus board texture, MDF defence, blocker bluffs, mixed frequencies. |
| `model_e.py` | E – max aggression | D plus population exploits, overbet shoves, hero calls, thin value. |

Shared engine:

- `botcore.py` — own 7-card evaluator (12× faster than `card_utils.evaluate`,
  12.5 µs vs 150 µs), Monte-Carlo equity, 169-class preflop percentiles,
  opponent counters, sizing/texture helpers. Pure stdlib, no numpy.
- `policy.py` — the decision engine. `TIER` selects the sophistication;
  ranges/thresholds/sizings are class attributes.

## Quantified score

`score_bots.py` is the fixed rubric (0–100):

- 50 pts — mean bb/100 across all six dummies, mapped −10 → 0 and +60 → 50
- 15 pts — mean bb/100 vs `tight`, `equity`, `shove`, mapped −10 → 0, +40 → 15
- 20 pts — round-robin bb/100 among A–E, mapped −20 → 0, +20 → 20
- 10 pts — zero faults and slowest move < 2 s
- 5 pts — reserved for a council review score

Run:

```sh
.venv/bin/python score_bots.py --deals 60
.venv/bin/python score_bots.py --deals 200 --only b
```

### Latest measurement (60 duplicate deals per pairing, seed 0)

| bot | fold | call | random | shove | tight | equity | mean | hard | faults | score |
|---|---|---|---|---|---|---|---|---|---|---|
| a | +41.7 | +84.2 | +320.9 | +88.0 | +22.4 | −7.4 | +91.6 | +34.3 | 0 | 81.0 |
| b | +51.7 | +304.0 | +380.0 | +105.2 | +58.8 | +45.2 | +157.5 | +69.7 | 0 | **94.7** |
| c | +55.0 | +285.4 | +406.6 | +62.5 | +60.8 | +15.2 | +147.6 | +46.1 | 0 | 82.5 |
| d | +61.7 | +317.3 | +184.9 | +98.5 | +65.8 | +29.9 | +126.4 | +64.8 | 0 | 84.8 |
| e | +65.8 | +372.0 | +414.3 | +120.2 | +57.5 | −10.5 | +169.9 | +55.7 | 0 | 80.2 |

Cross-play: B is the only bot with a positive record against every other
variant (about +27 to +32 bb/100). B is the recommended submission.

**Caveat:** 60 deals is noisy (±20–40 bb/100 is normal). Re-run with
`--deals 300 --times 3` before trusting small differences. The council
stage (5 pts) has not been run yet, so the scores above are out of 95.

## Legality

`check_legal.py` mirrors `tests/test_model.py`: heads-up against every
dummy, a 6-handed table, and a short-stack table. **All five variants
report zero faults.** `python -m submit` also reports “played legally
against every dummy” for B.

## How to submit

Any variant, e.g. B:

```sh
python -m submit --team <yourteam> --model model_b:Model --out dist
```

Upload every file it lists. For B that is:

- `dist/altcar-b.pkl`
- `botcore.py`
- `model_b.py`
- `policy.py`

Pre-built pickles are in `dist/altcar-{a..e}.pkl`. A pickle only records the
class; the `.py` files must be uploaded with it (flat, no folders).

## What is not done

- **Council loop not executed.** The plan was three independent judges
  scoring strategy, robustness, exploitability and code-review safety, then
  iterate. The 5 reserved points are therefore unclaimed.
- **No large-sample evaluation.** 60 deals per pairing; the close scores
  (80–95) are inside the noise band. The B > C > D > E ordering is not yet
  established.
- **No real `python -m evals` run** (the organiser's exact worker/time-limit
  path). Only the in-process harness and `submit`'s legality check were run.
  `pytest tests/test_model.py` tests `model.py`, not the variants, so it was
  not used.
- **Model E is under-tested.** Its overrides are the least validated and it
  lost to B in cross-play.
- **No opponent-range solver / CFR.** Plan D here is a practical
  mixed-strategy approximation, not an equilibrium solve. A real solver was
  out of scope for the 2-hour budget.
- **`tune.py` sweep was interrupted** (the process was stopped). The applied
  numbers come from the completed first sweep: `OPEN .55 / DEFEND .85 /
  THREE_BET .12 / VALUE .64` was the best single configuration found.
- **Not pushed to `main` of the upstream repo** — only to the fork.
- **No README/plan file inside the fork before this commit**; the plan lives
  in the session transcript.

## Suggested next steps (in order)

1. Re-run `score_bots.py --deals 300` for B, D, E and keep the winner.
2. Build a small local pool from other teams' pickles (`evals --opponents`).
3. Run `python -m evals --model model_b:Model --deals 1000 --times 3` for
   the organiser's exact bb/100 and CI.
4. Council review of the winning variant, then spend the remaining time on
   preflop range accuracy, not extra features.
5. Fix E or drop it; do not submit an unvalidated aggressive variant.
