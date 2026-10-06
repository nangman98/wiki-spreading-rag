#!/usr/bin/env python3
"""Local web app: ask your wiki in the browser, no agent in the loop.

The model is loaded once at start-up; each question runs spreading-activation
search, sends only the relevant lines of the top notes to the model, streams
the answer token by token, then runs the grounding check. Evidence notes open
in Obsidian with one click.

    python3 src/wiki_app.py --vault ~/wiki            # then open http://localhost:8765
    python3 src/wiki_app.py --model mlx-community/Qwen3-4B-4bit --budget 500
    python3 src/wiki_app.py --backend openai --base-url http://localhost:11434/v1 --model qwen3:8b   # Ollama
"""

import argparse
import json
import re
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from spread_search import DEFAULT_VAULT, FRONT_RE, load_index, search, tokens  # noqa: E402
from wiki_ask import MODEL, SYSTEM, check  # noqa: E402

ARGS = None
MODEL_OBJ = None
LOCK = threading.Lock()


def snippet(text, qtok, budget):
    """Title + claim line + the units that share the most tokens with the question.

    A markdown table (with the heading line right above it) is one unit, so a
    matching table header brings its value rows along.
    """
    body = FRONT_RE.sub("", text).strip()
    lines = [l.rstrip() for l in body.splitlines() if l.strip()]
    head, rest = lines[:2], lines[2:]
    units, i = [], 0
    while i < len(rest):
        if rest[i].lstrip().startswith("|"):
            j = i
            while j < len(rest) and rest[j].lstrip().startswith("|"):
                j += 1
            cap = units.pop() if units and rest[i - 1].startswith("#") else None
            units.append("\n".join(([cap] if cap else []) + rest[i:j]))
            i = j
        else:
            units.append(rest[i])
            i += 1
    scored = []
    for k, u in enumerate(units):
        if u.startswith("## ") or u.startswith("- [["):
            continue
        hit = len(qtok & set(tokens(u)))
        if hit:
            scored.append((hit, k, u))
    keep, used = [], sum(map(len, head))
    for hit, k, u in sorted(scored, key=lambda x: (-x[0], x[1])):
        if used + len(u) > budget and keep:
            continue
        keep.append((k, u))
        used += len(u)
    return "\n".join(head + [u for _, u in sorted(keep)])


def sse(handler, event, data):
    handler.wfile.write(f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n".encode())
    handler.wfile.flush()


def stream_openai(messages):
    """Stream from any OpenAI-compatible server (Ollama, LM Studio, llama.cpp, mlx_lm.server)."""
    import urllib.request
    req = urllib.request.Request(ARGS.base_url.rstrip("/") + "/chat/completions",
                                 data=json.dumps({"model": ARGS.model, "messages": messages, "stream": True,
                                                  "max_tokens": ARGS.max_tokens, "temperature": 0.2}).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        for raw in r:
            line = raw.decode("utf-8", "replace").strip()
            if not line.startswith("data:") or line.endswith("[DONE]"):
                continue
            delta = json.loads(line[5:])["choices"][0].get("delta", {})
            if delta.get("content"):
                yield delta["content"]


def answer(handler, q, use_llm=True):
    t0 = time.time()
    hits = search(q, ARGS.vault, k=ARGS.notes)
    if not hits:
        sse(handler, "error", "검색어와 맞는 노트가 없습니다. 영어 용어나 노트 이름으로 바꿔 보세요.")
        return
    vault_name = Path(ARGS.vault).expanduser().name
    qtok = set(tokens(q))
    blocks = []
    for h in hits:
        slug = h["id"].rsplit("/", 1)[-1]
        h["slug"] = slug
        h["obsidian"] = f"obsidian://open?vault={quote(vault_name)}&file={quote(h['id'])}"
        text = Path(h["path"]).read_text(encoding="utf-8", errors="replace")
        h["snippet"] = snippet(text, qtok, ARGS.budget)
        blocks.append(f"[노트 {slug}]\n{h['snippet']}")
    sse(handler, "hits", [{k: h[k] for k in ("slug", "title", "seed", "via", "obsidian", "snippet")} for h in hits])
    if not use_llm:
        sse(handler, "stats", {"seconds": round(time.time() - t0, 2)})
        return
    user = "[노트]\n\n" + "\n\n---\n\n".join(blocks) + f"\n\n[질문]\n{q}"
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]
    out, last, in_think = "", None, False
    if ARGS.backend == "mlx":
        from mlx_lm import stream_generate
        model, tok = MODEL_OBJ
        prompt = tok.apply_chat_template(messages, add_generation_prompt=True, tokenize=False, enable_thinking=False)
        gen = stream_generate(model, tok, prompt, max_tokens=ARGS.max_tokens)
    else:
        if "qwen3" in ARGS.model.lower():          # Qwen3 thinks by default; soft switch turns it off
            messages[-1]["content"] += " /no_think"
        gen = stream_openai(messages)
    with LOCK:
        for r in gen:
            if ARGS.backend == "mlx":
                last, piece = r, r.text
            else:
                piece = r
            out += piece
            if "<think>" in out and "</think>" not in out:
                in_think = True
                continue
            if in_think:
                in_think = False
                piece = out.split("</think>", 1)[1].lstrip()
            if piece:
                sse(handler, "token", piece)
    clean = re.sub(r"<think>.*?</think>\s*", "", out, flags=re.S).strip()
    sse(handler, "check", check(clean, hits, blocks))
    if last is not None:
        sse(handler, "stats", {"prompt_tokens": last.prompt_tokens, "prompt_tps": round(last.prompt_tps),
                               "gen_tps": round(last.generation_tps, 1), "seconds": round(time.time() - t0, 1)})
    else:
        sse(handler, "stats", {"seconds": round(time.time() - t0, 1), "backend": ARGS.model})


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/":
            body = PAGE.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif u.path == "/ask":
            qs = parse_qs(u.query)
            q = qs.get("q", [""])[0].strip()
            use_llm = qs.get("llm", ["1"])[0] != "0"
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            try:
                answer(self, q, use_llm) if q else sse(self, "error", "질문이 비어 있습니다.")
            except (BrokenPipeError, ConnectionResetError):
                return
            sse(self, "done", "")
        elif u.path == "/reload":
            load_index(ARGS.vault, refresh=True)
            self.send_response(204)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()


PAGE = """<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Wiki Ask</title>
<style>
:root{--bg:#f7f7f5;--card:#fff;--ink:#1d1d1f;--mute:#6b6b70;--line:#e3e3e0;--acc:#0b63ce;--warn:#b54708}
@media (prefers-color-scheme:dark){:root{--bg:#121316;--card:#1b1d22;--ink:#e8e8ea;--mute:#9a9aa2;--line:#2c2f36;--acc:#6ea8ff;--warn:#f0a35e}}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.6 -apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo",sans-serif}
main{max-width:860px;margin:0 auto;padding:28px 16px 60px}
h1{font-size:20px;font-weight:600;margin:0 0 4px}.sub{color:var(--mute);font-size:13px;margin-bottom:18px}
form{display:flex;gap:8px}input{flex:1;font:inherit;padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--ink)}
button{font:inherit;padding:10px 16px;border:0;border-radius:10px;background:var(--acc);color:#fff;cursor:pointer}button:disabled{opacity:.5}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin-top:14px}
#ans{white-space:pre-wrap;min-height:1.6em}.lbl{font-size:12px;color:var(--mute);margin-bottom:6px;letter-spacing:.02em}
#hits a{color:var(--acc);text-decoration:none}#hits pre{white-space:pre-wrap;font:12.5px/1.5 ui-monospace,Menlo,monospace;color:var(--ink);background:var(--bg);border-radius:8px;padding:8px 10px;margin:4px 0 10px}#hits li{margin:2px 0}#hits .tag{color:var(--mute);font-size:12px}
#warn{color:var(--warn)}#stats{color:var(--mute);font-size:12px;margin-top:8px}.hide{display:none}
</style></head><body><main>
<h1>Wiki Ask</h1><div class="sub">위키 링크 그래프 확산 검색 + 로컬 모델. 답은 근거 노트에서만, 확인 안 된 숫자·단위·인용은 경고로 표시.</div>
<form id="f"><input id="q" placeholder="질문을 입력하세요" autofocus autocomplete="off"><button id="b">묻기</button></form>
<label style="font-size:13px;color:var(--mute);display:block;margin-top:8px"><input type="checkbox" id="llm" checked style="flex:none"> 로컬 모델 요약도 생성 (끄면 검색 결과만, 1초 이내)</label>
<div class="card hide" id="hbox"><div class="lbl">근거 노트와 해당 줄 (확산 활성화 순, 제목을 누르면 Obsidian에서 열림) — 수치는 여기서 확인</div><ol id="hits"></ol><div id="stats"></div></div>
<div class="card hide" id="abox"><div class="lbl">로컬 모델 요약 (참고용 — 판이 여러 개인 수치를 잘못 고를 수 있음)</div><div id="ans"></div></div>
<div class="card hide" id="wbox"><div class="lbl">검사 경고</div><ul id="warn"></ul></div>
<script>
const $=id=>document.getElementById(id);
$("f").onsubmit=e=>{e.preventDefault();const q=$("q").value.trim();if(!q)return;
 const useLLM=$("llm").checked;$("ans").textContent="";$("abox").classList.toggle("hide",!useLLM);$("stats").textContent="";$("hits").innerHTML="";$("warn").innerHTML="";
 $("wbox").classList.add("hide");$("hbox").classList.add("hide");$("b").disabled=true;let first=true;
 const es=new EventSource("/ask?q="+encodeURIComponent(q)+(useLLM?"":"&llm=0"));
 es.addEventListener("hits",ev=>{const hs=JSON.parse(ev.data);$("hbox").classList.remove("hide");
  if(useLLM)$("ans").textContent="모델이 노트 "+hs.length+"개를 읽는 중… (첫 글자까지 10–40 s)";
  for(const h of hs){const li=document.createElement("li");const a=document.createElement("a");a.href=h.obsidian;a.textContent=h.slug;
   const t=document.createElement("span");t.className="tag";t.textContent=" "+(h.seed?"seed":"via "+String(h.via).split("/").pop())+" · "+h.title;
   const pre=document.createElement("pre");pre.textContent=h.snippet;li.append(a,t,pre);$("hits").append(li);}});
 es.addEventListener("token",ev=>{if(first){$("ans").textContent="";first=false;}$("ans").textContent+=JSON.parse(ev.data);});
 es.addEventListener("check",ev=>{const w=JSON.parse(ev.data);if(w.length){$("wbox").classList.remove("hide");
  for(const x of w){const li=document.createElement("li");li.textContent=x;$("warn").append(li);}}});
 es.addEventListener("stats",ev=>{const s=JSON.parse(ev.data);$("stats").textContent=s.prompt_tokens?`${s.seconds}s · prompt ${s.prompt_tokens} tok @ ${s.prompt_tps} tok/s · 생성 ${s.gen_tps} tok/s`:(s.backend?`${s.seconds}s · ${s.backend}`:`검색 ${s.seconds}s`);});
 es.addEventListener("error",ev=>{if(ev.data)$("ans").textContent=JSON.parse(ev.data);});
 es.addEventListener("done",()=>{es.close();$("b").disabled=false;});
 es.onerror=()=>{es.close();$("b").disabled=false;};};
</script></main></body></html>"""


def main():
    global ARGS, MODEL_OBJ
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--vault", default=DEFAULT_VAULT)
    ap.add_argument("--backend", choices=["mlx", "openai"], default="mlx",
                    help="mlx = load the model in-process (Apple Silicon); openai = any OpenAI-compatible server")
    ap.add_argument("--base-url", default="http://localhost:11434/v1",
                    help="for --backend openai (Ollama 11434, LM Studio 1234, llama.cpp 8080)")
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--notes", type=int, default=6, help="evidence notes per question")
    ap.add_argument("--budget", type=int, default=700, help="max characters taken from each note")
    ap.add_argument("--max-tokens", type=int, default=600)
    ARGS = ap.parse_args()
    if ARGS.backend == "mlx":
        from mlx_lm import load
        print(f"loading {ARGS.model} …", flush=True)
        MODEL_OBJ = load(ARGS.model)
    else:
        print(f"using {ARGS.base_url} model={ARGS.model}", flush=True)
    nodes, _, _ = load_index(ARGS.vault)
    print(f"vault {ARGS.vault}: {len(nodes)} notes indexed", flush=True)
    print(f"open http://localhost:{ARGS.port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", ARGS.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
