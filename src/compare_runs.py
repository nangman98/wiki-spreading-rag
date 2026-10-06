#!/usr/bin/env python3
"""Solo-vs-crew control: compare two ingest runs made from the same source files.

Metrics (all mechanical, no LLM judge):
  fact coverage   share of distinct numbers in the sources (>= 3 digits, e.g. 0.123,
                  −45.67, 8910) that appear verbatim in the run's notes
  unsourced nums  numbers in the notes that appear in neither the sources nor the
                  vault snapshot (HTML decoded first). Candidates for invention; read
                  them — unit conversions and differences also land here
  near-dup pairs  new-note pairs inside one run whose titles share >= 50 % tokens
                  or whose slugs share >= 60 % words
  broken links    [[wikilinks]] resolving neither to the run's notes nor the vault
  notes / words   output size
  tokens / time   from a meta JSON you fill from the agent run logs

    python3 src/compare_runs.py --sources files.txt --vault ~/wiki-snapshot \
        --run solo=staging/solo --run crew=staging/crew --meta meta.json
"""

import argparse
import html
import json
import re
import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spread_search import tokens  # noqa: E402
from staging_merge import jaccard, slug_jaccard, title_of  # noqa: E402
from wikigraph import WIKILINK_RE  # noqa: E402

NUM_RE = re.compile(r"(?<![\w.])[−-]?\d+(?:\.\d+)?(?:\s*[×x]\s*10[⁻-]?[⁰¹²³⁴⁵⁶⁷⁸⁹\d]+)?(?![\w])")
FRONT_RE = re.compile(r"\A---\n.*?\n---\n", re.S)


def numbers(text):
    text = html.unescape(re.sub(r"<[^>]+>", " ", text))     # site pages: &minus;, tags
    out = set()
    for m in NUM_RE.finditer(text):
        x = m.group(0).replace("−", "-").replace(" ", "")
        if sum(c.isdigit() for c in x) >= 3 and not re.fullmatch(r"-?(19|20)\d\d", x):   # skip years
            out.add(x)
    return out


def run_notes(root):
    root = Path(root)
    return sorted(set(root.glob("*/notes/*.md")) | set(root.glob("*/updates/*.md")) | set(root.glob("notes/*.md")))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sources", required=True, help="text file, one source path per line")
    ap.add_argument("--vault", required=True, help="vault snapshot the workers started from")
    ap.add_argument("--run", action="append", required=True, help="name=staging_dir (repeat)")
    ap.add_argument("--meta", help='JSON {"solo": {"tokens": .., "seconds": .., "agents": 1}, ...}')
    a = ap.parse_args()
    src_text = "\n".join(Path(p.strip()).expanduser().read_text(encoding="utf-8", errors="replace")
                         for p in Path(a.sources).read_text().splitlines() if p.strip())
    src_nums = numbers(src_text)
    vault = Path(a.vault).expanduser()
    vault_slugs = {p.stem.lower() for p in vault.rglob("*.md")}
    vault_nums = numbers("\n".join(p.read_text(encoding="utf-8", errors="replace") for p in (vault / "notes").glob("*.md")))
    meta = json.loads(Path(a.meta).read_text()) if a.meta else {}

    rows = []
    for spec in a.run:
        name, d = spec.split("=", 1)
        notes = run_notes(d)
        text = "\n".join(FRONT_RE.sub("", p.read_text(encoding="utf-8", errors="replace")) for p in notes)
        nums = numbers(text)
        slugs = {p.stem.lower() for p in notes}
        broken = sum(1 for p in notes for t in WIKILINK_RE.findall(p.read_text(encoding="utf-8", errors="replace"))
                     if t.strip().rsplit("/", 1)[-1].lower() not in slugs | vault_slugs)
        new = [(p.stem, title_of(p)) for p in notes if "/notes/" in str(p)]
        dups = sum(1 for (s1, t1), (s2, t2) in combinations(new, 2)
                   if jaccard(t1, t2) >= 0.5 or slug_jaccard(s1, s2) >= 0.6)
        m = meta.get(name, {})
        rows.append([name, m.get("agents", "?"), len(notes), len(text.split()),
                     f"{len(nums & src_nums) / max(len(src_nums), 1):.2f}", len(nums - src_nums - vault_nums),
                     dups, broken, m.get("tokens", "?"), m.get("seconds", "?")])
    head = ["run", "agents", "notes", "words", "fact coverage", "unsourced nums", "near-dup pairs",
            "broken links", "tokens", "wall s"]
    print(f"source numbers: {len(src_nums)}")
    print("| " + " | ".join(head) + " |\n|" + "---|" * len(head))
    for r in rows:
        print("| " + " | ".join(map(str, r)) + " |")


if __name__ == "__main__":
    main()
