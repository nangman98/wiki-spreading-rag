#!/usr/bin/env python3
"""Minimal vault lint: broken [[wikilinks]], notes with no links, notes over the word limit.

    python3 src/lint.py --vault example_vault        # exit 1 if any broken link
"""

import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wikigraph import WIKILINK_RE, FRONT_RE, build_graph  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", default=os.environ.get("WIKI_VAULT", str(Path(__file__).resolve().parent.parent / "example_vault")))
    ap.add_argument("--max-words", type=int, default=800)
    a = ap.parse_args()
    nodes, links = build_graph(a.vault)
    names = {n["id"].rsplit("/", 1)[-1].lower() for n in nodes}
    names |= {x.lower() for n in nodes for x in re.findall(r"^aliases:\s*\[(.*?)\]", n["content"], re.M)
              for x in [y.strip().strip("\"'") for y in x.split(",")]}
    linked = {u for l in links for u in l}
    broken, lonely, long_ = [], [], []
    for n in nodes:
        for t in WIKILINK_RE.findall(n["content"]):
            if t.strip().rsplit("/", 1)[-1].lower().removesuffix(".md") not in names:
                broken.append(f"{n['id']} -> [[{t}]]")
        if n["id"].startswith("notes/"):
            if n["id"] not in linked:
                lonely.append(n["id"])
            words = len(FRONT_RE.sub("", n["content"]).split())
            if words > a.max_words:
                long_.append(f"{n['id']} ({words} words)")
    for title, items in (("broken wikilinks", broken), ("notes with no links", lonely),
                         (f"notes over {a.max_words} words", long_)):
        print(f"## {title}: {len(items)}")
        for x in items:
            print("  -", x)
    sys.exit(1 if broken else 0)


if __name__ == "__main__":
    main()
