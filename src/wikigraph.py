"""Parse an Obsidian-style markdown vault into a link graph.

Nodes are .md files (id = path without .md, relative to the vault root).
Edges come from [[wikilink]] and [text](file.md) links, resolved the way
Obsidian does: exact relative path first, then basename stem, then
frontmatter `aliases`. Links are undirected for search purposes.
"""

import re
from pathlib import Path

EXCLUDE_DIRS = {".git", ".obsidian", ".trash", "node_modules"}
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
MDLINK_RE = re.compile(r"\]\(([^)#:\s]+\.md)(?:#[^)]*)?\)")
FRONT_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def _frontmatter(text):
    m = FRONT_RE.match(text)
    title, tags, aliases = None, [], []
    if m:
        fm = m.group(1)
        if t := re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', fm, re.M):
            title = t.group(1)
        if t := re.search(r"^tags:\s*\[(.*?)\]", fm, re.M):
            tags = [x.strip().strip("\"'") for x in t.group(1).split(",") if x.strip()]
        if t := re.search(r"^aliases:\s*\[(.*?)\]", fm, re.M):
            aliases = [x.strip().strip("\"'") for x in t.group(1).split(",") if x.strip()]
    return title, tags, aliases


def build_graph(vault):
    vault = Path(vault).expanduser()
    nodes, stem, alias = {}, {}, {}
    for p in sorted(vault.rglob("*.md")):
        rel = p.relative_to(vault)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        nid = str(rel.with_suffix(""))
        text = p.read_text(encoding="utf-8", errors="replace")
        title, tags, aliases = _frontmatter(text)
        nodes[nid] = {"id": nid, "name": title or rel.stem, "tags": tags, "content": text,
                      "path": str(p)}
        stem.setdefault(rel.stem.lower(), nid)
        for a in aliases:
            alias.setdefault(a.lower(), nid)

    def resolve(target, src_dir):
        t = target.strip().replace("\\", "/").removesuffix(".md")
        for base in (src_dir, Path(".")):
            if (cand := str(base / t)) in nodes:
                return cand
        key = t.rsplit("/", 1)[-1].lower()
        return stem.get(key) or alias.get(key)

    links = set()
    for nid, n in nodes.items():
        for tgt in WIKILINK_RE.findall(n["content"]) + MDLINK_RE.findall(n["content"]):
            rid = resolve(tgt, Path(nid).parent)
            if rid and rid != nid:
                links.add(tuple(sorted((nid, rid))))
    return list(nodes.values()), sorted(links)
