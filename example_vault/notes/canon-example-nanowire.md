---
title: "정본 값 등록부 — 예시 나노와이어 transport 프로젝트 (가상 값)"
tags: [project]
project: ["proj-example-nanowire-transport"]
status: evergreen
created: 2026-10-08
updated: 2026-10-08
related: ["[[proj-example-nanowire-transport]]"]
sources: ["예시 — 실제 계산 값이 아니다"]
---
# 정본 값 등록부 — 예시 나노와이어 transport 프로젝트

이 프로젝트에서 인용할 때 기준이 되는 값과 그 이전 값들이다. 모든 수치는 형식을 보여 주기 위한 가상 값이다.

## 판단 기준

사용자 확정 > 게재·제출용 문서 > 계산 기록 > 보고서·미팅노트 > 계획. 같은 순위에서는 정정을 명시한 나중 문서를 따른다.

## 정본 값

| id | 양 | 정본 값 | 단위 | 조건 | 출처 | 날짜 | 이전 값 |
|---|---|---|---|---|---|---|---|
| ex-tef | zero-bias T(E_F) | 2.468×10⁻³ | — | 보정 후, η 0.005 eV | 예시 결과 페이지 | 2026-02-01 | 0.0135 (보정 전 판, 이전 판) |
| ex-kz | 전극 k_z | 120 | — | 수렴 테스트 후 | 예시 provenance | 2026-01-20 | 48 (초기 계획, 이전 판) |

## 상충

| id | 양 | 값 A | 값 B | 왜 못 정했나 |
|---|---|---|---|---|
| ex-gap | 분자 gap | 1.234 eV (보고서) | 1.278 eV (계산 기록) | 기하 판이 달라 같은 순위에서 정정 명시가 없음 |

## Connections

- [[proj-example-nanowire-transport]] — 이 등록부가 기준이 되는 프로젝트
