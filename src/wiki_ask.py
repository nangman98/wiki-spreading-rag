#!/usr/bin/env python3
"""Ask the brain wiki a question with a local model (no data leaves the Mac).

Pipeline: spread_search.py (BM25 seed + wikilink spreading activation) picks the
evidence notes -> their bodies (frontmatter stripped, truncated) go into the
prompt -> a local MLX model answers citing [slug], or says "모르겠다".

Usage:
    python3 src/wiki_ask.py "DFT band gap 과소평가가 transmission에 주는 영향은?"
    python3 src/wiki_ask.py "..." --vault ~/my-vault -n 8 --model mlx-community/Qwen3-4B-4bit
"""

import argparse
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from spread_search import search, DEFAULT_VAULT  # noqa: E402
MODEL = "mlx-community/Qwen3-8B-4bit"
FRONT_RE = re.compile(r"\A---\n.*?\n---\n", re.S)

SYSTEM = (
    "너는 주어진 연구 위키 노트만 근거로 답하는 조수다.\n"
    "규칙:\n"
    "1. 아래 [노트] 안에 있는 내용만 쓴다. 노트에 없으면 그 부분은 '모르겠다'라고 쓴다. 추측 금지.\n"
    "2. 수치는 노트에 적힌 그대로 옮긴다. 단위는 노트에 그 수치와 함께 적힌 단위만 쓰고, 노트에 단위가 없으면 붙이지 않는다(transmission T(E) 등은 무차원).\n"
    "3. 각 주장 문장 끝에 근거 노트를 [slug] 형식으로 붙인다.\n"
    "4. 결론을 첫 문장에 쓰고, 한국어로 짧게 답한다. 기술 용어는 영어 그대로 둔다.\n"
    "5. 노트끼리 값이 다르면 둘 다 적고 어느 노트 값인지 밝힌다."
)


def retrieve(q, n, vault):
    res = search(q, vault, k=n)
    if not res:
        sys.exit("no lexical match — rephrase (try English terms or note names)")
    return res


NUM_RE = re.compile(r"[−-]?\d+(?:\.\d+)?(?:\s*[×x]\s*10[⁻-]?[⁰¹²³⁴⁵⁶⁷⁸⁹\d]+)?")
UNIT_RE = re.compile(r"([−-]?\d+(?:\.\d+)?(?:\s*[×x]\s*10[⁻-]?[⁰¹²³⁴⁵⁶⁷⁸⁹\d]+)?)\s*(meV/atom|meV/f\.u\.|eV/Å|eV|meV|Å|e/f\.u\.|e|K|GPa|%)(?![A-Za-z])")


def check(ans, hits, blocks, superseded=None):
    """Mechanical guardrail: numbers, number+unit pairs and cited slugs must appear in the evidence;
    numbers registered as previous values in canon-*.md are flagged even when the evidence contains them."""
    ev = "\n".join(blocks)
    ev_n = ev.replace("−", "-")
    slugs = {h["id"].split("/", 1)[-1] for h in hits}
    out = []
    for m in NUM_RE.finditer(ans):
        x = m.group(0).replace("−", "-").strip()
        if len(x.lstrip("-")) >= 3 and x not in ev_n:
            out.append(f"숫자 {m.group(0)} 가 근거 노트에 없음")
    for v, u in UNIT_RE.findall(ans):
        vv = v.replace("−", "-")
        if vv in ev_n and not re.search(re.escape(vv) + r"\s*" + re.escape(u), ev_n):
            out.append(f"{v} 뒤의 단위 '{u}' 는 노트에 없음 (노트에는 다른 단위이거나 무차원)")
    for c in re.findall(r"\[\[?([a-z0-9][a-z0-9\-]+)\]?\]", ans):
        if c not in slugs:
            out.append(f"인용 [{c}] 는 근거 노트 목록에 없음")
    if superseded:
        from canon import numbers_in
        for raw, n in numbers_in(ans, 2):
            for rid, canonical, label, note in superseded.get(n, []):
                out.append(f"{raw} 는 이전 값 {label} — 현행 {canonical} ({rid}, [[{note}]])")
    for h in hits:
        if h.get("superseded"):
            out.append(f"근거 노트 [{h['id'].split('/', 1)[-1]}] 는 이전 판(status: superseded)")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("question")
    ap.add_argument("--vault", default=DEFAULT_VAULT)
    ap.add_argument("-n", type=int, default=6, help="evidence notes")
    ap.add_argument("--chars", type=int, default=1800, help="max chars per note")
    ap.add_argument("--max-tokens", type=int, default=700)
    ap.add_argument("--think", action="store_true", help="enable Qwen3 thinking mode (slower)")
    ap.add_argument("--model", default=MODEL)
    a = ap.parse_args()

    hits = retrieve(a.question, a.n, a.vault)
    blocks = []
    for h in hits:
        slug = h["id"].split("/", 1)[-1]
        body = FRONT_RE.sub("", Path(h["path"]).read_text(encoding="utf-8", errors="replace")).strip()
        blocks.append(f"[노트 {slug}]\n제목: {h['title']}\n{body[:a.chars]}")
    user = "[노트]\n\n" + "\n\n---\n\n".join(blocks) + f"\n\n[질문]\n{a.question}"

    from mlx_lm import load, generate
    t0 = time.time()
    model, tok = load(a.model)
    prompt = tok.apply_chat_template([{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
                                     add_generation_prompt=True, tokenize=False, enable_thinking=a.think)
    n_in = len(tok.encode(prompt))
    t1 = time.time()
    ans = generate(model, tok, prompt=prompt, max_tokens=a.max_tokens)
    t2 = time.time()
    ans = re.sub(r"<think>.*?</think>\s*", "", ans, flags=re.S).strip()

    print(ans)
    from canon import load_registry, superseded_index
    warn = check(ans, hits, blocks, superseded_index(load_registry(a.vault)))
    if warn:
        print("\n[검사 경고] 근거 노트와 대조해 확인되지 않은 항목:")
        for w in warn:
            print(" -", w)
    print("\n근거 노트 (확산 활성화 순):")
    for i, h in enumerate(hits, 1):
        tag = "seed" if h["seed"] else f"via {h['via'].split('/')[-1]}"
        print(f" {i}. {h['id'].split('/', 1)[-1]}  [{tag}]")
    print(f"\n(model {a.model.split('/')[-1]} · prompt {n_in} tok · load {t1 - t0:.1f}s · gen {t2 - t1:.1f}s)")


if __name__ == "__main__":
    main()
