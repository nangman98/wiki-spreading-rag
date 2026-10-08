"""Read canonical-value registries (notes named canon-*.md).

A registry is a markdown table whose header has an id column, a canonical-value
column and a "previous values" column, e.g.

| id | 양 | 정본 값 | 단위 | 조건 | 출처 | 날짜 | 이전 값 |
|---|---|---|---|---|---|---|---|
| p-tef | T(E_F) | 6.2×10⁻³ | — | ... | site | 2026-01-10 | 0.0041 (v2, 이전 판); 3.9×10⁻³ (old projector, 이전 판) |

English headers work too: id / canonical / previous (or superseded).
"""

import re
from pathlib import Path

NUM_RE = re.compile(r"[−-]?\d+(?:\.\d+)?(?:\s*[×x]\s*10[⁻-]?[⁰¹²³⁴⁵⁶⁷⁸⁹\d]+)?")
SUPERS = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-")


def norm_num(s):
    """'1.2345×10⁻³' -> '1.2345e-3', '−0.5' -> '-0.5' (string form, no float rounding)."""
    s = s.replace("−", "-").replace(" ", "")
    m = re.fullmatch(r"(-?\d+(?:\.\d+)?)(?:[×x]10([⁻\-]?[⁰¹²³⁴⁵⁶⁷⁸⁹\d]+))?", s)
    if not m:
        return s
    return m.group(1) + (("e" + m.group(2).translate(SUPERS)) if m.group(2) else "")


def numbers_in(text, min_digits=3):
    """Distinctive numbers only: at least `min_digits` digits or a ×10^n factor."""
    out = []
    for m in NUM_RE.finditer(text):
        raw = m.group(0)
        if sum(c.isdigit() for c in raw) >= min_digits or "10" in raw and ("×" in raw or "x" in raw):
            out.append((raw, norm_num(raw)))
    return out


def _cols(header):
    h = [c.strip().lower() for c in header.strip().strip("|").split("|")]
    def find(*keys):
        for i, c in enumerate(h):
            if any(k in c for k in keys):
                return i
        return None
    return find("id"), find("정본", "canonical", "current"), find("이전", "previous", "superseded"), find("양", "quantity")


def load_registry(vault):
    """-> list of dicts: id, quantity, canonical, previous [(raw, norm, label)], note"""
    rows = []
    for p in sorted((Path(vault).expanduser() / "notes").glob("canon-*.md")):
        text = p.read_text(encoding="utf-8", errors="replace")
        projects = note_projects(text)
        lines = text.splitlines()
        for i, l in enumerate(lines):
            if not l.lstrip().startswith("|") or i + 1 >= len(lines) or not set(lines[i + 1].replace("|", "").strip()) <= set("-: "):
                continue
            ci, cc, cp, cq = _cols(l)
            if None in (ci, cc, cp):
                continue
            for row in lines[i + 2:]:
                if not row.lstrip().startswith("|"):
                    break
                cells = [c.strip() for c in row.strip().strip("|").split("|")]
                if len(cells) <= max(ci, cc, cp):
                    continue
                prev = []
                for part in re.split(r";", cells[cp]):
                    label = re.sub(r"^[^()]*", "", part).strip()
                    for raw, n in numbers_in(part.split("(")[0], 2):
                        prev.append((raw, n, label))
                rows.append(dict(id=cells[ci], quantity=cells[cq] if cq is not None else "", canonical=cells[cc],
                                 previous=prev, note=p.stem, projects=projects))
    return rows


def note_projects(text):
    """frontmatter `project:` values as a set (empty if missing or unparsable)."""
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not m:
        return set()
    try:
        import yaml
        fm = yaml.safe_load(m.group(1)) or {}
    except Exception:
        return set()
    v = fm.get("project") or []
    return {str(x).strip("[]\"' ") for x in (v if isinstance(v, list) else [v])}


def superseded_index(rows):
    """normalized number -> list of (id, canonical, label, note) for previous values."""
    idx = {}
    for r in rows:
        for raw, n, label in r["previous"]:
            idx.setdefault(n, []).append((r["id"], r["canonical"], label, r["note"]))
    return idx
