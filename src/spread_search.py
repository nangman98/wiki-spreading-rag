#!/usr/bin/env python3
"""Spreading-activation search over a markdown wiki's link graph.

1. Seed  : BM25 over title (x3) + aliases + body. Tokens are ASCII words/numbers
           plus Korean character bigrams, so no morphological analyzer is needed.
2. Spread: personalized-PageRank-style iteration on the symmetric-normalized
           link graph,  a <- (1 - alpha) * s + alpha * A_hat @ a  (s = seed vector).
3. Rank  : by activation; non-seed hits report the neighbor they came through.

    python3 src/spread_search.py "question" --vault example_vault
    python3 src/spread_search.py "question" --json          # for an LLM front end
"""

import argparse
import json
import math
import os
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wikigraph import build_graph  # noqa: E402

ASCII_RE = re.compile(r"[a-z0-9][a-z0-9_.+\-]*[a-z0-9]|[a-z0-9]")
HANGUL_RE = re.compile(r"[가-힣]+")
FRONT_RE = re.compile(r"\A---\n.*?\n---\n", re.S)
DEFAULT_VAULT = os.environ.get("WIKI_VAULT", str(Path(__file__).resolve().parent.parent / "example_vault"))


def tokens(text):
    t = text.lower()
    out = ASCII_RE.findall(t)
    for run in HANGUL_RE.findall(t):
        out += [run[i:i + 2] for i in range(len(run) - 1)] if len(run) > 1 else [run]
    return out


def bm25(docs, query, k1=1.2, b=0.75):
    n = len(docs)
    avg = sum(map(len, docs)) / max(n, 1)
    tfs = [Counter(d) for d in docs]
    df = Counter(w for tf in tfs for w in tf)
    q = set(tokens(query))
    scores = []
    for tf, d in zip(tfs, docs):
        s = 0.0
        for w in q & tf.keys():
            idf = math.log(1 + (n - df[w] + 0.5) / (df[w] + 0.5))
            s += idf * tf[w] * (k1 + 1) / (tf[w] + k1 * (1 - b + b * len(d) / avg))
        scores.append(s)
    return scores


_CACHE = {}


def load_index(vault=DEFAULT_VAULT, include_sources=False, refresh=False):
    """Parse the vault once and keep nodes, tokenized docs and links in memory."""
    key = (str(Path(vault).expanduser()), include_sources)
    if refresh or key not in _CACHE:
        nodes, links = build_graph(vault)
        if not include_sources:
            nodes = [x for x in nodes if not x["id"].startswith(("raw/", "archive/"))]
        docs = [tokens((x["name"] + " ") * 3 + FRONT_RE.sub("", x["content"])) for x in nodes]
        _CACHE[key] = (nodes, links, docs)
    return _CACHE[key]


def search(query, vault=DEFAULT_VAULT, k=10, n_seeds=8, alpha=0.5, include_sources=False, iters=20):
    nodes, links, docs = load_index(vault, include_sources)
    idx = {x["id"]: i for i, x in enumerate(nodes)}
    lex = bm25(docs, query)
    seeds = [i for i in sorted(range(len(nodes)), key=lambda i: -lex[i])[:n_seeds] if lex[i] > 0]
    if not seeds:
        return []
    tot = sum(lex[i] for i in seeds)
    s = [0.0] * len(nodes)
    for i in seeds:
        s[i] = lex[i] / tot
    nb = [[] for _ in nodes]
    for u, v in links:
        if u in idx and v in idx:
            nb[idx[u]].append(idx[v])
            nb[idx[v]].append(idx[u])
    deg = [max(len(x), 1) for x in nb]
    act = s[:]
    for _ in range(iters):
        new = [(1 - alpha) * x for x in s]
        for i, x in enumerate(act):
            if x:
                share = alpha * x / math.sqrt(deg[i])
                for j in nb[i]:
                    new[j] += share / math.sqrt(deg[j])
        act = new
    sup = [bool(re.search(r"^status:\s*superseded", x["content"], re.M)) for x in nodes]
    act = [a * (0.3 if s else 1.0) for a, s in zip(act, sup)]      # superseded notes stay findable, ranked lower
    seedset = set(seeds)
    out = []
    for i in sorted(range(len(nodes)), key=lambda i: -act[i])[:k]:
        via = None if i in seedset or not nb[i] else nodes[max(nb[i], key=lambda j: act[j])]["id"]
        out.append({"id": nodes[i]["id"], "title": nodes[i]["name"], "activation": round(act[i], 4),
                    "seed": i in seedset, "bm25": round(lex[i], 2), "via": via, "path": nodes[i]["path"],
                    "superseded": sup[i]})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query")
    ap.add_argument("--vault", default=DEFAULT_VAULT)
    ap.add_argument("-k", type=int, default=10)
    ap.add_argument("--seeds", type=int, default=8)
    ap.add_argument("--alpha", type=float, default=0.5, help="0 = BM25 only")
    ap.add_argument("--all", action="store_true", help="also search raw/ and archive/")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    res = search(a.query, a.vault, a.k, a.seeds, a.alpha, a.all)
    if not res:
        sys.exit("no lexical match — rephrase (try English terms or note names)")
    if a.json:
        print(json.dumps({"query": a.query, "results": res}, ensure_ascii=False, indent=1))
        return
    for r, x in enumerate(res, 1):
        tag = "seed" if x["seed"] else f"via {x['via'].split('/')[-1]}"
        tag += ", 이전 판" if x["superseded"] else ""
        print(f"{r:2d}. {x['activation']:.4f}  {x['id']:<48.48}  [{tag}]")


if __name__ == "__main__":
    main()
