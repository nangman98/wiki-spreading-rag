# wiki-spreading-rag

**연구 위키(markdown + `[[wikilink]]`)를 그래프 확산 검색과 로컬 LLM으로 질의하는 최소 구성.** 학습(fine-tuning)·강화학습 없이, 노트끼리의 링크를 검색 신호로 쓰고 답은 노트 인용으로만 하게 만든다. 모든 단계가 노트북 한 대에서 돈다.

*English summary — A minimal, fully local setup to ask questions of a personal research wiki. BM25 seeds a spreading-activation search over the wiki's link graph; a small local LLM (MLX) answers only from the retrieved notes, and a mechanical check flags numbers, units and citations that do not appear in the evidence. No fine-tuning or RL.*

<p align="center"><img src="docs/figures/fig1-pipeline.png" width="860" alt="pipeline"></p>

**Fig. 1.** 구축(A)과 질의(B) 흐름. 위키 링크 그래프 하나가 검색(B-2)과 시각화(A, layered network view)에 함께 쓰인다.

<p align="center"><img src="docs/figures/fig2-neural-example.png" width="860" alt="layered network view"></p>

**Fig. 2.** 예시 vault의 층 신경망 시각화(`build_neural.py`). 왼쪽부터 원본(Sources) → atomic notes → 프로젝트 허브 → MOC → Index이고, 강조된 흰 곡선은 한 노트의 링크 전체다. 학습된 가중치가 아니라 `[[wikilink]]`를 그린 은유다.

---

## 무엇이 들어 있나

| 파일 | 역할 |
|---|---|
| `src/wikigraph.py` | vault → 노드·링크 그래프 (Obsidian 방식 링크 해석: 상대경로 → 파일명 → `aliases`) |
| `src/spread_search.py` | BM25 seed + 그래프 확산(personalized-PageRank식) 검색 |
| `src/wiki_ask.py` | 검색 결과를 로컬 LLM에 넣어 답하고, 숫자·단위·인용을 근거와 기계 대조 |
| `src/build_neural.py` + `templates/` | vault를 층 신경망 모양 HTML 한 장으로 렌더 (제목 AES 암호화 옵션) |
| `example_vault/` | 가상의 DFT·전자수송 학습 위키 (바로 돌려 볼 수 있는 예시) |
| `docs/guide.md` | 자기 위키에 적용하는 단계별 가이드 (vault 규약, LLM ingest, 평가) |
| `src/lint.py`, `src/eval.py`, `eval/questions.md` | 링크 점검, 평가 질문과 Recall@k 측정 (평가 파일은 vault 밖에 둔다) |
| `docs/example-output.txt`, `docs/wiki-neural-example.html` | 예시 vault로 실제 실행한 답변 출력과 시각화 결과 |
| `docs/ingest-brief-template.md` | 원본 문서를 위키 노트로 정리시키는 LLM 에이전트 브리프 템플릿 |

## 빠른 시작

```bash
git clone https://github.com/nangman98/wiki-spreading-rag && cd wiki-spreading-rag

# 1) 검색만 (의존성 없음, Python 3.9+)
python3 src/spread_search.py "band gap 과소평가가 transmission에 주는 영향"

# 2) 로컬 LLM 답변 (Apple Silicon)
pip install mlx-lm
python3 src/wiki_ask.py "band gap 과소평가가 transmission에 주는 영향은?"   # 첫 실행 때 모델(약 4–5 GB) 다운로드

# 3) 신경망 모양 시각화
python3 src/build_neural.py --out wiki-neural.html && open wiki-neural.html
```

자기 위키에 쓰려면 `--vault ~/my-vault` 또는 환경변수 `WIKI_VAULT`를 준다.

## 작동 방식

1. **Seed.** 질문과 각 노트(제목 3배 가중 + 본문)의 BM25 점수 상위 8개가 출발점이다. 한국어는 형태소 분석 없이 글자 bigram으로 쪼갠다(조사가 붙어도 매칭).
2. **Spread.** 대칭 정규화 인접행렬 Â 위에서 `a ← (1−α)s + α·Â·a`를 20회 반복한다(α = 0.5). 질문 단어가 없어도 링크로 이어진 노트가 따라 올라오고, 링크만 많은 허브는 √degree 정규화로 눌린다. 결과마다 "seed" 또는 "via 어느 노트"가 붙는다.
3. **Answer.** 상위 k개 노트 본문(frontmatter 제거, 노트당 1,800자)만 프롬프트에 넣고, 규칙(노트에 없으면 "모르겠다", 수치 그대로, `[slug]` 인용)을 시스템 프롬프트로 고정한다.
4. **Check.** 답의 숫자, "숫자+단위" 쌍, 인용 slug가 근거 노트에 실제로 있는지 정규식으로 대조해 경고를 붙인다. 작은 모델의 대표 오류(단위 창작, 없는 노트 인용)를 여기서 잡는다.

이 구조는 HippoRAG(Gutiérrez et al. 2024, arXiv:2405.14831)의 Personalized PageRank 검색과 같은 계열이다. 차이는 LLM으로 지식 그래프를 추출하지 않고, 사람이 이미 만든 `[[wikilink]]`를 그대로 쓴다는 점이다(인덱싱 비용 0).

## 실측 (저자 환경)

| 항목 | 값 |
|---|---|
| 기기 | Apple M4, RAM 16 GB |
| 모델 | `mlx-community/Qwen3-8B-4bit` (thinking off) |
| 위키 규모 | notes 약 490개, 링크 약 2,800개 (무방향) |
| 질의 1회 | 프롬프트 7,680 tokens, 모델 로드 5.2 s, 생성 66.6 s |
| 관찰된 오류 | 무차원 값에 "eV"를 붙임(2/2회), 존재하지 않는 노트 인용(1회) — 둘 다 4단계 검사가 검출 |

예시 vault(노트 24개, 링크 92개)에서 평가 질문 4개(`eval/questions.md`, `python3 src/eval.py`)로 잰 검색 recall:

| | BM25만 (α=0) | 확산 (α=0.5) |
|---|---|---|
| Recall@3 평균 | 0.73 | 0.67 |
| Recall@5 평균 | 0.85 | 0.85 |

이 작은 vault에서는 확산의 이득이 없다. 노트가 적고 링크가 촘촘해 BM25 상위권이 이미 정답 근처를 덮기 때문으로 보이며 [잠정], 질문 4개는 판정에 부족하다. 확산이 효과를 내는지는 자기 위키의 평가셋으로 재야 한다(guide §6). 수치를 맞추려고 α를 조정하지 않았다.

메모리별 권장 모델: 8 GB → `Qwen3-4B-4bit`, 16 GB → `Qwen3-8B-4bit`, 32 GB 이상 → 14B급 4-bit. `--model`로 바꾼다.

## 왜 학습시키지 않나

개인 지식을 모델 가중치에 넣는 fine-tuning은 사실 지식 주입에서 RAG보다 성능이 낮고(Ovadia et al. 2023, arXiv:2312.05934), 새 지식을 SFT로 학습할수록 환각 경향이 늘어난다(Gekhman et al. 2024, arXiv:2405.05904). 노트가 바뀔 때마다 재학습해야 하는 부담도 있다. 검색 정책을 RL로 학습하는 Search-R1(arXiv:2503.09516)은 H100 8장 규모로, 개인 위키 규모에서는 정당화가 어렵다. 그래서 이 저장소는 **검색 품질을 먼저 재고(평가셋), 그다음에만 학습을 검토**하는 순서를 권한다 — `docs/guide.md` §6.

Transformer와의 관계: attention의 갱신식은 modern Hopfield network의 연상 기억 검색과 같다(Ramsauer et al. 2020, arXiv:2008.02217). 그래프 확산은 같은 연상 검색을 명시적 링크 위에서 여러 단계로 하는 것으로 볼 수 있다 — 해석 수준의 대응이다. 층 신경망 그림(`build_neural.py`)도 은유이며 학습된 가중치는 없다.

## 한계

- BM25 seed는 동의어·번역어를 못 잇는다("열전도도" ↔ "thermal conductivity"). 노트 `aliases`에 대응어를 적거나, embedding seed(예: BGE-M3)로 바꾼다 — guide §6.
- 링크가 적은 위키에서는 확산 효과가 작다. 노트마다 `## Connections`를 채우는 습관이 검색 품질을 결정한다.
- 4단계 검사는 정규식 기반이라 "숫자 표기는 맞는데 의미가 틀린" 답은 못 잡는다. 근거 노트를 같이 열어 보는 것이 최종 확인이다.

## 라이선스

MIT. 예시 vault 노트는 교과서 수준의 일반 지식으로 새로 작성했다.
