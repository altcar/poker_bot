from pathlib import Path

src = Path("model_b.py").read_text()
body = src[src.index("from policy import PokerBot"):]
for name, title in (("c", "C"), ("d", "D"), ("e", "E")):
    header = '"""Plan ' + title + " - tuned profile (same core as B after the equity fix)." + '"""'
    Path(f"model_{name}.py").write_text(header + "\n\n" + body)
print("cde aligned to B")
