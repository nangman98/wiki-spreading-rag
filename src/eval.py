#!/usr/bin/env python3
"""Recall@k of BM25-only (alpha=0) vs spreading activation on eval/questions.md.

Keep the question file OUTSIDE the vault, or it becomes a search hit itself.

    python3 src/eval.py --vault example_vault -k 5
"""

import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spread_search import search  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", default=os.environ.get("WIKI_VAULT", str(Path(__file__).resolve().parent.parent / "example_vault")))
    ap.add_argument("-k", type=int, default=5)
    ap.add_argument("--alphas", default="0,0.5")
    ap.add_argument("--questions", default=str(Path(__file__).resolve().parent.parent / "eval" / "questions.md"))
    a = ap.parse_args()
    rows = []
    for line in Path(a.questions).read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|$", line)
        if m:
            rows.append((m.group(1), m.group(2), [g.strip() for g in m.group(3).split(",")]))
    alphas = [float(x) for x in a.alphas.split(",")]
    print(f"| # | " + " | ".join(f"Recall@{a.k} α={al}" for al in alphas) + " |")
    print("|---|" + "---|" * len(alphas))
    tot = [0.0] * len(alphas)
    for qid, q, gold in rows:
        cells = []
        for i, al in enumerate(alphas):
            got = {r["id"].rsplit("/", 1)[-1] for r in search(q, a.vault, k=a.k, alpha=al)}
            rec = len(got & set(gold)) / len(gold)
            tot[i] += rec
            cells.append(f"{rec:.2f}")
        print(f"| {qid} | " + " | ".join(cells) + " |")
    print("| mean | " + " | ".join(f"{t / len(rows):.2f}" for t in tot) + " |")


if __name__ == "__main__":
    main()
