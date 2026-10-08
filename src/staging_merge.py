#!/usr/bin/env python3
"""Supervisor merge for parallel ingest workers that never see each other's drafts.

Each worker writes only inside its own staging folder:

    <staging>/<worker>/notes/<slug>.md     new notes
    <staging>/<worker>/updates/<slug>.md   full proposed replacement of an existing vault note

This script is the single place where drafts meet. It reports conflicts and,
with --apply, copies every conflict-free draft into <vault>/notes/. Conflicts
stay in staging for the supervisor (human or lead agent) to merge by hand:

  * the same new slug proposed by two workers
  * a "new" note whose slug already exists in the vault (should have been an update)
  * near-duplicate titles (token Jaccard >= --dup) across workers or against the vault
  * one existing note updated by two workers
  * [[wikilinks]] that resolve neither to the vault nor to staged notes

    python3 src/staging_merge.py --vault ~/wiki --staging ~/wiki/raw/staging-20261006
    python3 src/staging_merge.py ... --apply
"""

import argparse
import re
import shutil
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spread_search import tokens  # noqa: E402
from wikigraph import WIKILINK_RE  # noqa: E402

TITLE_RE = re.compile(r'^title:\s*["\']?(.+?)["\']?\s*$', re.M)


def title_of(path):
    m = TITLE_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    return m.group(1) if m else path.stem


def jaccard(a, b):
    a, b = set(tokens(a)), set(tokens(b))
    return len(a & b) / max(len(a | b), 1)


def slug_jaccard(a, b):
    a, b = set(a.split("-")), set(b.split("-"))
    return len(a & b) / max(len(a | b), 1)


def similar(s1, t1, s2, t2, dup, slug_dup):
    """Near-duplicate if either the titles or the slugs overlap enough.

    Slugs that differ only in numeric tokens (meeting-2026-03-05 vs meeting-2026-03-16)
    are distinct notes, not duplicates.
    """
    diff = set(s1.split("-")) ^ set(s2.split("-"))
    if diff and all(x.isdigit() for x in diff):
        return False, "numeric-only slug difference"
    j, js = jaccard(t1, t2), slug_jaccard(s1, s2)
    return (j >= dup or js >= slug_dup), f"title J={j:.2f} slug J={js:.2f}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--vault", required=True)
    ap.add_argument("--staging", required=True)
    ap.add_argument("--dup", type=float, default=0.5, help="title Jaccard threshold for near-duplicates")
    ap.add_argument("--slug-dup", type=float, default=0.6, help="slug word Jaccard threshold")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    vault, staging = Path(a.vault).expanduser(), Path(a.staging).expanduser()
    vault_notes = {p.stem: p for p in (vault / "notes").glob("*.md")}

    new, upd = defaultdict(list), defaultdict(list)          # slug -> [(worker, path)]
    for w in sorted(p for p in staging.iterdir() if p.is_dir()):
        for p in (w / "notes").glob("*.md"):
            new[p.stem].append((w.name, p))
        for p in (w / "updates").glob("*.md"):
            upd[p.stem].append((w.name, p))

    conflicts = defaultdict(list)                            # (kind, slug) -> details
    for s, xs in new.items():
        if len(xs) > 1:
            conflicts[("same-new-slug", s)] = [w for w, _ in xs]
        if s in vault_notes:
            conflicts[("new-but-exists", s)] = [w for w, _ in xs]
    for s, xs in upd.items():
        if len(xs) > 1:
            conflicts[("double-update", s)] = [w for w, _ in xs]
        if s not in vault_notes:
            conflicts[("update-missing-target", s)] = [w for w, _ in xs]

    staged = [(s, w, p, title_of(p)) for s, xs in new.items() for w, p in xs]
    for (s1, w1, _, t1), (s2, w2, _, t2) in combinations(staged, 2):
        hit, why = similar(s1, t1, s2, t2, a.dup, a.slug_dup)
        if s1 != s2 and hit:
            conflicts[("near-duplicate", f"{s1} ~ {s2}")] = [w1, w2, why]
    vault_titles = {vs: title_of(vp) for vs, vp in vault_notes.items()}
    for s, w, _, t in staged:
        for vs, vt in vault_titles.items():
            hit, why = similar(s, t, vs, vt, a.dup, a.slug_dup)
            if vs != s and hit:
                conflicts[("near-duplicate-vault", f"{s} ~ {vs}")] = [w, why]

    known = {k.lower() for k in vault_notes} | {s.lower() for s in new}
    for s, w, p, _ in staged + [(s, w, p, None) for s, xs in upd.items() for w, p in xs]:
        for t in WIKILINK_RE.findall(p.read_text(encoding="utf-8", errors="replace")):
            if t.strip().rsplit("/", 1)[-1].lower() not in known:
                conflicts[("broken-link", f"{s} -> [[{t.strip()}]]")] = [w]

    blocked = {k[1].split(" ")[0] for k in conflicts}            # broken links block their draft too
    blocked |= {k[1].split(" ~ ")[1] for k in conflicts if k[0] == "near-duplicate"}
    lines = [f"# merge report — {staging.name}", "",
             f"workers: {len({w for xs in list(new.values()) + list(upd.values()) for w, _ in xs})} · "
             f"new drafts: {sum(map(len, new.values()))} · update drafts: {sum(map(len, upd.values()))} · "
             f"conflicts: {len(conflicts)}", "", "| kind | target | workers / detail |", "|---|---|---|"]
    lines += [f"| {k} | {t} | {', '.join(d)} |" for (k, t), d in sorted(conflicts.items())]
    applied = []
    if a.apply:
        for s, xs in new.items():
            if s not in blocked and len(xs) == 1:
                shutil.copy2(xs[0][1], vault / "notes" / f"{s}.md")
                applied.append(f"new {s}")
        for s, xs in upd.items():
            if s not in blocked and len(xs) == 1:
                shutil.copy2(xs[0][1], vault / "notes" / f"{s}.md")
                applied.append(f"update {s}")
        lines += ["", f"applied: {len(applied)}", *[f"- {x}" for x in applied]]
    (staging / "MERGE_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:4]))
    print(f"report -> {staging / 'MERGE_REPORT.md'}")


if __name__ == "__main__":
    main()
