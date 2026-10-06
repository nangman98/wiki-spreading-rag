---
title: Pseudopotential은 core 전자를 제거하고 valence 전자의 산란 성질만 재현해 계산 비용을 줄인다
tags: [concept]
status: evergreen
created: 2026-10-06
updated: 2026-10-06
sources: []
---
# Pseudopotentials

pseudopotential은 화학 결합에 거의 참여하지 않는 core 전자를 유효 퍼텐셜로 바꾸고 cutoff radius 밖에서 all-electron 결과와 같은 valence 파동함수를 주도록 만듦.

## Summary

- norm-conserving: cutoff radius 안의 전하량을 all-electron 값과 맞춤 (Hamann-Schlüter-Chiang, Troullier-Martins).
- ultrasoft: norm 조건을 풀어 더 부드러운 파동함수를 허용함 (Vanderbilt).
- PAW: all-electron 파동함수를 재구성할 수 있는 projector 방식 (Blöchl).

## Details

core 근처의 valence 파동함수는 core orbital과 직교하기 위해 빠르게 진동함. 이 진동을 표현하려면 큰 [[plane-wave-cutoff-convergence]]가 필요하므로, pseudopotential은 cutoff radius 안쪽 파동함수를 노드 없는 매끄러운 함수로 바꿈.

cutoff radius가 클수록 pseudopotential은 부드러워지고 필요한 cutoff가 줄지만 이웃 원자와 core 영역이 겹치는 짧은 결합에서는 transferability가 떨어짐. semicore 상태(예: 전이금속의 상위 s, p 껍질)를 valence에 포함할지도 같은 trade-off임.

Kleinman-Bylander 형태는 nonlocal 부분을 separable projector로 써서 계산을 효율화함. 이 형태에서는 ghost state가 생길 수 있으므로 새 pseudopotential은 원자 계산과 간단한 결정 계산으로 검증함.

pseudopotential은 생성 시 사용한 [[exchange-correlation-functionals]]와 같은 functional로 써야 일관성이 유지됨. 국소 basis 코드에서는 pseudopotential과 [[basis-sets-numerical-atomic-orbitals]]가 원소별로 짝을 이룸.

## Connections

- [[plane-wave-cutoff-convergence]] — pseudopotential hardness가 cutoff를 정함
- [[exchange-correlation-functionals]] — 생성 functional과 사용 functional의 일치
- [[basis-sets-numerical-atomic-orbitals]] — 국소 basis 코드에서 원소별 짝

## Refs

- D. R. Hamann, M. Schlüter, and C. Chiang, Phys. Rev. Lett. 43, 1494 (1979).
- L. Kleinman and D. M. Bylander, Phys. Rev. Lett. 48, 1425 (1982).
- D. Vanderbilt, Phys. Rev. B 41, 7892 (1990).
- N. Troullier and J. L. Martins, Phys. Rev. B 43, 1993 (1991).
- P. E. Blöchl, Phys. Rev. B 50, 17953 (1994).
