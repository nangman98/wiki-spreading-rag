#!/usr/bin/env python3
"""Render a markdown wiki as a layered "neural network" page (single HTML file).

Layers follow how knowledge flows through the vault (left -> right):
  L0 sources (raw/, archive/) -> L1 atomic notes -> L2 project hubs
  -> L3 MOC hubs (moc-*) -> L4 index (root-level md).
Unlinked files become the background star field. The picture is a metaphor:
there are no learned weights, only your [[wikilinks]].

    python3 src/build_neural.py --vault example_vault --out docs/wiki-neural.html
    python3 src/build_neural.py --vault ~/wiki --password '...'   # titles AES-256-GCM encrypted
"""

import argparse
import base64
import gzip
import hashlib
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from wikigraph import build_graph  # noqa: E402

NAMES = ["Sources", "Atomic notes", "Project hubs", "MOC", "Index"]


def layer_of(n):
    nid = n["id"]
    if nid.startswith(("raw/", "archive/")):
        return 0
    if "/" not in nid:
        return 4
    stem = nid.rsplit("/", 1)[-1]
    if stem.startswith("moc-"):
        return 3
    if "project" in n["tags"] or stem.startswith("proj-"):
        return 2
    return 1


def encrypt(password, payload, iters=600_000):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    salt = hashlib.sha256(b"wiki-graph-salt|" + password.encode()).digest()[:16]
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iters, dklen=32)
    iv = hashlib.sha256(key + payload).digest()[:12]
    b64 = lambda b: base64.b64encode(b).decode()
    return {"salt": b64(salt), "iv": b64(iv), "ct": b64(AESGCM(key).encrypt(iv, payload, None)),
            "iter": iters, "gz": True}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--vault", default=os.environ.get("WIKI_VAULT", str(HERE.parent / "example_vault")))
    ap.add_argument("--out", default="wiki-neural.html")
    ap.add_argument("--password", help="encrypt titles; omit to embed them in clear")
    a = ap.parse_args()

    nodes, links = build_graph(a.vault)
    lay = {n["id"]: layer_of(n) for n in nodes}
    nbrs = {n["id"]: set() for n in nodes}
    for u, v in links:
        nbrs[u].add(v)
        nbrs[v].add(u)
    cols = [[] for _ in NAMES]
    for n in nodes:
        if nbrs[n["id"]]:
            cols[lay[n["id"]]].append(n["id"])
    stars = sum(1 for n in nodes if not nbrs[n["id"]])

    pos = {nid: i / max(len(c) - 1, 1) for c in cols for i, nid in enumerate(c)}
    for s in range(12):                                   # barycentric crossing reduction
        for li in (range(len(cols)) if s % 2 == 0 else reversed(range(len(cols)))):
            bary = {n: (sum(pos[m] for m in nbrs[n]) / len(nbrs[n])) for n in cols[li]}
            cols[li].sort(key=lambda n: (bary[n], n))
            for i, n in enumerate(cols[li]):
                pos[n] = i / max(len(cols[li]) - 1, 1)

    idx, layers = {}, []
    for li, c in enumerate(cols):
        layers.append({"name": NAMES[li], "nodes": [idx.setdefault(n, len(idx)) for n in c]})
    plinks = sorted({tuple(sorted((idx[u], idx[v]))) for u, v in links if u in idx and v in idx})
    deg = [0] * len(idx)
    for u, v in plinks:
        deg[u] += 1
        deg[v] += 1
    title = {n["id"]: n["name"] for n in nodes}
    secret = {"names": [title[n] for n in sorted(idx, key=idx.get)]}

    html = (HERE.parent / "templates" / "neural_template.html").read_text(encoding="utf-8")
    pub = {"layers": layers, "links": plinks, "deg": deg, "stars": stars}
    if a.password:
        enc = encrypt(a.password, gzip.compress(json.dumps(secret, ensure_ascii=False).encode(), 9, mtime=0))
        plain = "null"
    else:
        enc, plain = None, json.dumps(secret, ensure_ascii=False)
    html = (html.replace("/*__DATA_PUB__*/null", json.dumps(pub, separators=(",", ":")))
                .replace("/*__ENC__*/null", json.dumps(enc))
                .replace("/*__PLAIN__*/null", plain))
    Path(a.out).write_text(html, encoding="utf-8")
    print(" ".join(f"L{i}={len(c)}" for i, c in enumerate(cols)), f"links={len(plinks)} stars={stars} -> {a.out}")


if __name__ == "__main__":
    main()
