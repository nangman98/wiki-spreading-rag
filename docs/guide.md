# 가이드 — 자기 연구 위키에 적용하기

**순서는 규약 → ingest → 점검 → 검색·질의 → 시각화 → 평가다.** 검색 품질은 알고리즘보다 노트 형식과 링크 밀도가 결정하므로 앞의 세 단계가 가장 중요하다.

## 1. Vault 규약

| 경로 | 내용 | 쓰기 |
|---|---|---|
| `raw/` | 원본 문서 사본 (보고서, STATUS, 계산 provenance, 사이트 페이지) | 읽기 전용 |
| `archive/` | ingest가 끝난 raw, 통합으로 흡수된 노트 | 이동만 |
| `notes/` | 모든 노트, 하위 폴더 없음 (flat) | 노트 작성 |
| `Index.md` | MOC 목록 | 갱신 |

노트 한 개 = 주장 한 개, 300–600단어(800 넘으면 분할). slug는 소문자-하이픈 ASCII. 노트 종류는 파일명으로 구분한다: `moc-<주제>` (주제 허브, 링크와 한 줄 설명만), `proj-<이름>` 또는 `tags: [project]` (프로젝트 허브), 그 외 atomic note.

```yaml
---
title: <주장 한 문장>
aliases: [<대응어, 영어/한국어 표기>]     # 검색 seed가 동의어를 잇는 유일한 통로
tags: [concept|method|material|project|error|infra]
status: solved | open | wip | evergreen
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: ["<원본 경로 또는 DOI>"]
---
# <제목>
<한 줄 주장>
## Summary
## Details
## Connections
- [[slug]] — 왜 관련 있는지 한 줄      # ← 확산 검색의 간선. 가장 중요한 절
## Open questions
## Refs
```

규칙 세 가지가 검색 품질을 좌우한다.

- **수치는 원본 그대로 + 단위 + 출처.** 추론은 `?? ` 접두, 원본끼리 값이 다르면 지우지 말고 양쪽을 남긴다.
- **`## Connections`를 비우지 않는다.** 링크 없는 노트는 확산에서 고립된다(`build_neural.py`의 별 배경이 그 노트들이다).
- **판이 바뀐 결과는 시점과 상태를 적는다.** "v5는 이전 판, 2026-09-10부터 정본은 X"처럼. 사람과 검색에는 이것으로 충분하지만 저자 시험에서는 표에 상태 열(정본/폐기)이 있어도 8B 모델이 폐기된 값을 골랐다(README). 수치는 근거 줄에서 직접 확인한다.

## 2. LLM으로 ingest (격리형 crew)

원본 문서를 노트로 옮기는 일은 LLM 에이전트에 맡기고 사람은 결과를 검수한다. 구조는 Kim et al.(Google Research·DeepMind·MIT, arXiv:2512.08296)의 결과를 따른다. 병렬로 나눌 수 있는 과제에서는 중앙 조정형 multi-agent가 단일 에이전트보다 80.9 % 나았고 검증 단계 없는 독립형은 오류를 17.2배까지 키웠으며(중앙형 4.4배), 단일 에이전트가 이미 약 45 % 이상 성공하면 이득이 0 이하로 떨어졌다.

1. 변경분만 모은다: `find <project> -newermt <지난 ingest 날짜> -name '*.md'`.
2. 디렉토리 단위로 묶어 워커마다 파일 목록 하나를 준다. 같은 주제를 두 워커에 나누지 않는다.
3. **워커는 서로의 초안을 보지 않는다.** 각자 `staging/<worker>/notes/`(새 노트)와 `staging/<worker>/updates/`(기존 노트 수정본 전체)에만 쓰고 vault는 읽기만 한다. 브리프는 [`ingest-brief-template.md`](ingest-brief-template.md).
4. **병합은 supervisor 한 곳에서.** `python3 src/staging_merge.py --vault ~/my-vault --staging staging/` 가 같은 새 slug, 이미 있는 slug, 제목이 비슷한 노트(token Jaccard ≥ 0.5), 같은 노트 이중 수정, 깨진 링크를 `MERGE_REPORT.md`로 낸다. 충돌은 손으로 합치고 나머지는 `--apply`.
5. **단독 대조군을 둔다.** 처음 쓰는 분할이거나 모델이 바뀐 뒤에는 같은 입력을 단독 에이전트 1개로도 돌리고 `python3 src/compare_runs.py`로 비교한다. crew가 이기지 못하면 그 규모는 단독으로 한다. 저자 환경의 비교 결과는 README에 있다.

저자 환경에서 처음에는 워커 6개가 같은 vault에 동시에 썼고 그 결과 중복 노트 5쌍과 노트마다 엇갈린 판정이 생겨 사후 통합이 필요했다. 3–5번은 그 경험에서 나온 규칙이다.

## 3. 점검과 정리

```bash
python3 src/lint.py --vault ~/my-vault      # broken wikilink, 고립 노트, 800단어 초과
```

- broken wikilink는 0이어야 한다.
- 병렬 ingest 뒤에는 중복 노트가 생긴다. 하나로 합치고 흡수된 파일은 `archive/merged-YYYYMMDD/`로 옮긴 뒤 옛 slug 링크를 일괄 치환한다(삭제하지 않는다).
- 새 노트가 허브 노트에서 한 번 이상 링크되는지 확인한다. 허브에 안 걸린 노트는 확산에서 거의 안 켜진다.

## 3b. 정본 값 등록부와 이전 판

**정정 전 값과 정정 후 값이 위키에 함께 남으면 검색과 LLM은 이전 값을 정본처럼 내줄 수 있다.** 나중에 들어온 값이 항상 맞는 것도 아니다. 그래서 값마다 정본을 명시하고 이전 값에는 상태를 붙인다.

- **등록부**: 프로젝트마다 `notes/canon-<project>.md` 하나. 표 `| id | 양 | 정본 값 | 단위 | 조건 | 출처 | 날짜 | 이전 값 |`, 이전 값 칸은 `값 (판 이름, 이전 판/폐기/오류)`를 `;`로 나열한다. 정하지 못한 쌍은 `## 상충` 표로 따로 둔다.
- **판단 순위**: 사용자 확정 > 게재·제출용 정본 문서 > 계산 기록 > 보고서·미팅노트 > 계획·초기 설계. 같은 순위에서는 나중 문서가 정정·대체·폐기를 **명시**할 때만 나중 값을 따르고 아니면 상충으로 남긴다.
- **노트 표시**: 이전 값은 지우지 않고 같은 줄에 `(이전 판 …)` 등을 붙인다. 노트 전체가 대체되면 frontmatter `status: superseded`, `superseded_by: [[현행]]`.
- **기계 점검**: `python3 src/stale_check.py --vault ~/my-vault`가 등록부의 이전 값이 상태 표시 없이 쓰인 줄을 보고한다(push 전 0).
- **검색·답변**: `spread_search`는 `status: superseded` 노트의 순위를 낮추고 표시한다. `check()`는 답에 등록부의 이전 값이 나오면 근거 노트에 그 값이 있어도 "이전 값, 현행 X" 경고를 낸다. 8B 모델이 판별 표에서 폐기된 값을 고르던 실패(README)를 이 단계가 잡는다.

## 4. 검색과 질의

```bash
python3 src/wiki_app.py --vault ~/my-vault                               # 브라우저 앱 http://localhost:8765
python3 src/spread_search.py "질문" --vault ~/my-vault -k 12            # 순위 + seed/via
python3 src/spread_search.py "질문" --alpha 0                          # BM25만 (비교용)
python3 src/wiki_ask.py "질문" --vault ~/my-vault -n 6                 # 로컬 LLM 답
```

앱에서는 근거 노트와 해당 줄이 먼저 뜨고 모델 요약이 뒤따른다. 수치는 근거 줄에서 확인한다(8B 모델은 판별 표에서 폐기된 값을 고른 사례가 있다, README 참고). 조정 손잡이: `--budget` (노트당 글자 수, 앱), `--seeds` (출발 노트 수, 기본 8), `--alpha` (확산 세기, 0–1), `-n` (LLM에 넣는 노트 수), `--chars` (노트당 글자 수). 프롬프트 길이가 생성 시간을 정한다 — 8B 모델, M4 16 GB에서 7,680 tokens에 약 67 s.

Claude Code 같은 에이전트에서 쓰려면 `spread_search.py --json` 결과의 `path`를 읽게 하면 된다. 로컬 LLM 대신 에이전트가 근거 노트를 읽고 답하는 구성이다.

## 5. 시각화와 공개

```bash
python3 src/build_neural.py --vault ~/my-vault --out wiki-neural.html                  # 제목 평문 (로컬용)
python3 src/build_neural.py --vault ~/my-vault --out site/wiki-neural/index.html \
        --password "$WIKI_GRAPH_PASSWORD"                                             # 공개용
```

공개용은 층 구조·링크·개수만 평문이다. 노트 제목과 본문(노트당 6,000자까지)은 AES-256-GCM(PBKDF2-SHA256 600k)으로 암호화되어, 브라우저에서 비밀번호를 넣어야 풀리고 뉴런을 누르면 본문이 렌더된다. 정적 사이트(GitHub Pages 등)에 올리고 위키 저장소가 바뀔 때 CI에서 다시 빌드하면 된다. `?embed=1`을 붙이면 UI 없이 강조가 자동 순환하는 카드 모드가 된다.

## 6. 평가와 다음 단계

측정 없이 모델을 키우거나 학습을 붙이지 않는다. 단계마다 같은 평가셋으로 잰다.

| 단계 | 할 일 | 넘어가는 기준 |
|---|---|---|
| 0 | 실제로 물을 질문 30–50개 + 정답 노트 slug 짝 (한 노트로 답하는 질문과 여러 노트를 거치는 질문을 섞는다) | 질문마다 정답 노트 ≥ 1 |
| 1 | `--alpha 0` (BM25만) vs 기본 확산의 Recall@10 | 확산이 다중 노트 질문에서 올라가는지 |
| 2 | seed를 embedding(예: BGE-M3, arXiv:2402.03216)으로 교체하거나 BM25와 합침 | 동의어·번역어 질문의 recall |
| 3 | 답 정답률과 인용 정확도 (4단계 검사 경고 수 포함) | 기준선 확보 |
| 4 (조건부) | 검색은 맞는데 답이 틀리는 비율이 높을 때만 RAFT식 LoRA(arXiv:2403.10131) | 학습 전후 정답률 |

예시 vault의 평가 질문은 `eval/questions.md`에 있다. 평가 파일은 반드시 vault 밖에 둔다 — 안에 두면 질문 문장이 그대로 들어 있는 그 파일이 검색 1위가 된다.

## 참고문헌

- Gutiérrez et al., HippoRAG, 2024, arXiv:2405.14831 · HippoRAG 2, 2025, arXiv:2502.14802
- Edge et al., GraphRAG, 2024, arXiv:2404.16130 · Guo et al., LightRAG, 2024, arXiv:2410.05779
- Ovadia et al., Fine-Tuning or Retrieval?, 2023, arXiv:2312.05934
- Gekhman et al., Does Fine-Tuning LLMs on New Knowledge Encourage Hallucinations?, 2024, arXiv:2405.05904
- Zhang et al., RAFT, 2024, arXiv:2403.10131 · Jin et al., Search-R1, 2025, arXiv:2503.09516
- Ramsauer et al., Hopfield Networks is All You Need, 2020, arXiv:2008.02217
- Chen et al., BGE M3-Embedding, 2024, arXiv:2402.03216
