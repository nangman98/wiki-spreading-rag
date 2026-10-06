# Ingest 워커 브리프 템플릿 (격리형)

워커(LLM sub-agent) 한 개에 파일 목록 하나와 함께 넘긴다. `VAULT`, `STAGING`, 날짜, 비공개 범주만 바꾼다. 워커끼리는 서로의 초안을 보지 않고 초안이 만나는 곳은 supervisor의 `src/staging_merge.py` 하나다.

목적: 담당 원본 문서를 위키 atomic note 초안으로 만든다. 다음 세션의 LLM이 노트 검색만으로 프로젝트의 사실·수치·결정을 찾아 쓸 수 있어야 한다.

## 읽기·쓰기 범위 (가장 중요)
- 읽기: 담당 파일 목록의 원본, 그리고 기준 vault `VAULT` (읽기 전용 스냅샷).
- 쓰기: 오직 `STAGING/notes/` (새 노트)와 `STAGING/updates/` (기존 vault 노트의 수정본 전체)만.
- 다른 워커의 staging 폴더, 원본 프로젝트 파일, vault 파일은 절대 쓰지 않는다. 다른 워커의 존재를 가정하지 않는다.

## 선행
1. `VAULT/notes/`에서 관련 기존 노트를 찾는다 (`ls`, `grep -ril`). 같은 주제의 기존 노트가 있으면 새 노트를 만들지 말고 그 노트 전체를 복사해 고친 판을 `STAGING/updates/<같은 slug>.md`로 쓴다.
2. 노트 형식:
```
---
title: <주장 한 문장>
aliases: [...]
tags: [concept|method|material|project|error|infra]
status: solved | open | wip | evergreen
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: ["<원본 경로>"]
---
# <제목>
<한 줄 주장>
## Summary
## Details
## Connections
- [[slug]] — 이유 한 줄
## Open questions
## Refs
```

## 작성 규칙
- 주제로 묶는다. 소스 1:1 변환 금지. 노트 하나에 주장 하나, 300–600단어, 800 초과 시 분할.
- 수치는 소스 그대로 + 단위 + 출처 경로. 창작 금지. 추론은 `?? ` 접두. 소스끼리 상충하면 양쪽을 남긴다.
- 판이 바뀐 값은 시점과 상태(정본/이전 판/폐기)를 붙인다.
- `[[wikilink]]`는 `VAULT/notes/`에 실존하는 slug, 또는 내가 이번에 STAGING에 만든 slug만.
- 소스 언어 유지, 기술 용어는 영어. 이모지 금지.

## 금지
- 허브·MOC·Index 수정 (supervisor가 병합 후 처리)
- git 명령
- `<비공개 범주: 예) 특허, 미발표 협업 정보>`

## 반환 (최종 메시지)
1. 표: `slug | new/update | 한 줄 내용 | 주요 소스`
2. 처리 못 한 파일과 이유. `done + skipped = 담당 파일 수`
