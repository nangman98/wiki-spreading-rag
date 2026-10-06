---
title: k-point grid는 Brillouin zone 적분 오차를 정하며 금속일수록 더 촘촘한 grid를 요구한다
tags: [method]
status: evergreen
created: 2026-10-06
updated: 2026-10-06
sources: ["raw/2026-01-lab-notes-scf.md"]
---
# k-Point Sampling

주기계의 density와 total energy는 Brillouin zone(BZ) 적분이며 유한한 k-point grid의 수렴은 cutoff와 별도로 확인해야 함.

## Summary

- Monkhorst-Pack grid는 BZ를 균일하게 나눈 특수 점 집합임.
- 절연체는 성긴 grid로도 수렴이 빠르고 금속은 Fermi surface 때문에 촘촘한 grid가 필요함.
- 금속에서는 electronic smearing을 함께 써서 occupation의 불연속을 완화함.

## Details

Bloch 정리에 따라 Kohn-Sham orbital은 k로 표지되고 ([[kohn-sham-equations]]), 물리량은 BZ 평균으로 계산됨. Monkhorst-Pack 방식은 역격자 방향마다 n개의 점을 균일하게 배치하고 대칭으로 기약 점만 남김.

grid 크기는 실공간 cell 길이에 반비례하게 잡음. 긴 축은 적은 점으로 충분하고 vacuum이 들어간 비주기 방향은 1점(Γ)만 씀. 1D 나노와이어라면 와이어 축 방향만 여러 점을 쓰고 나머지 두 방향은 1점으로 둠.

금속에서는 Fermi 준위를 지나는 band 때문에 적분 피적분함수가 불연속임. Methfessel-Paxton, Fermi-Dirac 등의 smearing으로 이 불연속을 매끄럽게 하며 smearing 폭과 k-grid는 함께 수렴시켜야 함. 성긴 grid는 SCF 수렴도 늦출 수 있음 ([[2026-01-lab-notes-scf]], [[scf-mixing-convergence]]).

transport 계산에서는 전극 방향과 수직 방향의 k-point가 서로 다른 역할을 하므로 별도 규칙이 있음 ([[kpoints-in-transport-direction]]).

## Connections

- [[plane-wave-cutoff-convergence]] — 함께 수렴시켜야 하는 다른 수치 축
- [[kpoints-in-transport-direction]] — 전극·device 계산에서 방향별 설정
- [[scf-mixing-convergence]] — 금속의 SCF 안정성과 연결
- [[electrode-self-energy]] — 수직 방향 k-point가 self-energy 계산에 들어가는 방식

## Refs

- H. J. Monkhorst and J. D. Pack, Phys. Rev. B 13, 5188 (1976).
- M. Methfessel and A. T. Paxton, Phys. Rev. B 40, 3616 (1989).
