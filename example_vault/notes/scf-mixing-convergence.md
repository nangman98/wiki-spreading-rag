---
title: SCF 수렴은 mixing 방식과 금속의 charge sloshing 억제에 좌우된다
tags: [method]
status: evergreen
created: 2026-10-06
updated: 2026-10-06
sources: ["raw/2026-01-lab-notes-scf.md"]
---
# SCF Mixing and Convergence

Kohn-Sham 방정식의 self-consistent 해는 입력 density(또는 density matrix)를 반복 갱신해 찾으며 갱신 규칙인 mixing이 수렴 속도와 안정성을 정함.

## Summary

- linear mixing: 새 입력 = 이전 입력 + α × 잔차. 단순하지만 느리고 금속에서 진동하기 쉬움.
- Pulay(DIIS)·Broyden: 이전 여러 step의 잔차 history로 다음 입력을 외삽함.
- Kerker preconditioning: 긴 파장 성분의 mixing을 줄여 금속의 charge sloshing을 억제함.

## Details

반복 k에서 출력 density와 입력 density의 차이가 잔차 R_k임. linear mixing의 mixing weight α가 크면 진동하고 작으면 수렴이 느림. Pulay 방식은 최근 history의 잔차를 선형 결합해 잔차 norm이 최소가 되는 입력을 고르고 Broyden 방식은 Jacobian 역행렬을 반복마다 근사 갱신함.

큰 cell의 금속에서는 작은 wave vector q의 density 요동이 Hartree 항에서 1/q²로 증폭되어 charge sloshing이 생김. Kerker preconditioning은 작은 q 성분의 mixing을 줄여 이를 억제함. 실습 메모 [[2026-01-lab-notes-scf]]의 진동 증상이 이 경우에 해당함.

수렴이 나쁠 때의 점검 순서는 다음과 같음.

1. mixing weight를 낮추고 history 길이를 늘림.
2. 금속이면 electronic smearing을 확인함 ([[k-point-sampling]]).
3. 초기 density를 수렴된 근처 계산에서 가져옴 (restart).

transport 계산에서는 open boundary 때문에 device density가 전극 Fermi 준위에 묶이며 유한 bias에서는 non-equilibrium 항이 추가되어 수렴이 더 어려워짐 ([[finite-bias-iv-curves]]). 이전 bias의 density matrix를 다음 bias의 초기값으로 쓰는 방법이 표준임.

수렴 판정은 density matrix 변화와 total energy 변화 두 기준을 함께 보는 것이 안전함.

## Connections

- [[kohn-sham-equations]] — self-consistency가 필요한 이유
- [[k-point-sampling]] — smearing과 k-grid가 금속 SCF 안정성에 주는 영향
- [[finite-bias-iv-curves]] — bias를 걸었을 때 SCF가 어려워지는 이유

## Refs

- P. Pulay, Chem. Phys. Lett. 73, 393 (1980).
- G. P. Kerker, Phys. Rev. B 23, 3082 (1981).
- D. D. Johnson, Phys. Rev. B 38, 12807 (1988).
