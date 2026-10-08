#!/usr/bin/env python3
"""Find superseded values used without a status marker.

Reads every canon-*.md registry (src/canon.py), then scans the vault's notes for
lines that contain a registered *previous* value but no status word on the same
line (이전 판 / 폐기 / 오류 / 구판 / superseded / deprecated / a link to the
registry). Only notes of the registry's project (frontmatter `project`, or a link
to the project hub) are checked. Put `<!-- stale-ok -->` on a line whose number
is a different quantity that happens to look the same. Those lines are where a search or an LLM could hand out an old value
as if it were current.

    python3 src/stale_check.py --vault ~/wiki          # report, exit 1 if any
"""

import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from canon import load_registry, note_projects, numbers_in, superseded_index  # noqa: E402

MARK = re.compile(r"이전\s*판|폐기|오류|오기|오타|구판|\(구\)|정정|대체|superseded|deprecated|obsolete|\[\[canon-|canon-[\w-]+", re.I)
FENCE = re.compile(r"<!-- fig-sync:start -->.*?<!-- fig-sync:end -->", re.S)


def scan(vault):
    rows = load_registry(vault)
    idx = superseded_index(rows)
    proj_of_reg = {r["note"]: r["projects"] for r in rows}
    canon_now = {}
    for r in rows:
        for _, n in numbers_in(r["canonical"], 2):
            canon_now.setdefault(n, set()).add(r["id"])
    hits = []
    for p in sorted((Path(vault).expanduser() / "notes").glob("*.md")):
        if p.stem.startswith("canon-"):
            continue
        raw_text = p.read_text(encoding="utf-8", errors="replace")
        projects = note_projects(raw_text)
        text = FENCE.sub("", raw_text)
        fm = re.match(r"\A---\n.*?\n---\n", text, re.S)          # frontmatter (aliases may list old values on purpose)
        if fm:
            text = "\n" * fm.group(0).count("\n") + text[fm.end():]
        if re.search(r"^status:\s*superseded", raw_text, re.M):
            continue                                   # the whole note is already marked
        for ln, line in enumerate(text.splitlines(), 1):
            if MARK.search(line) or "<!-- stale-ok -->" in line:
                continue
            for raw, n in numbers_in(line, 3):
                if n in idx and n not in canon_now:   # a value that is canonical elsewhere is not stale
                    for rid, canonical, label, note in idx[n]:
                        reg_projects = proj_of_reg.get(note, set())
                        # only notes of the same project (or linking to its hub) can misuse that project's values
                        if reg_projects and not (projects & reg_projects or any(f"[[{h}]]" in raw_text for h in reg_projects)):
                            continue
                        hits.append((p.stem, ln, raw, rid, canonical, label, note, line.strip()[:140]))
    return rows, hits


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--vault", default=os.environ.get("WIKI_VAULT", str(Path(__file__).resolve().parent.parent / "example_vault")))
    a = ap.parse_args()
    rows, hits = scan(a.vault)
    print(f"registry rows: {len(rows)} · previous values: {sum(len(r['previous']) for r in rows)} · unmarked uses: {len(hits)}")
    for note, ln, raw, rid, canonical, label, reg, line in hits:
        print(f"- {note}:{ln}  {raw}  {label}  → 현행 {canonical} ({rid}, [[{reg}]])\n    {line}")
    sys.exit(1 if hits else 0)


if __name__ == "__main__":
    main()
