---
title: Transport 계산에서 전극 bulk 계산은 transport 방향 k-point를 촘촘히 잡고 device 계산은 그 방향을 1점으로 둔다
tags: [method]
status: evergreen
created: 2026-10-06
updated: 2026-10-06
sources: ["raw/2026-02-reading-notes-negf.md"]
---
# k-Points in the Transport Direction

DFT-NEGF 계산의 k-point 설정은 방향마다 역할이 다르며 전극 계산·device 계산·transmission 계산을 서로 맞춰야 함.

## Summary

- 전극 bulk 계산: transport 방향은 주기적이므로 촘촘한 k-grid로 Hamiltonian을 수렴시킴.
- device(scattering region) 계산: transport 방향은 open boundary라 k-point 1점만 씀.
- 수직 방향: 전극과 device가 같은 수직 k-grid를 써야 함.

## Details

전극은 transport 방향으로 무한히 반복되는 bulk 결정이므로, 일반적인 [[k-point-sampling]] 원리대로 그 방향의 BZ 적분을 수렴시켜야 함. 전극 주층이 짧을수록 그 방향 역격자가 길어져 더 많은 k-point가 필요함. 금속 전극은 Fermi surface 때문에 수렴이 특히 느림.

device 계산에서는 transport 방향의 무한성이 [[electrode-self-energy]]로 들어가므로, 같은 방향 k-point를 여러 개 쓰는 것은 의미가 없음. 그 방향은 1로 고정함.

transport 방향에 수직인 방향이 주기적인 slab 전극이면 수직 k-grid는 전극과 device에서 같아야 Σ(k⊥)와 device H(k⊥)가 같은 k⊥에서 결합됨. transmission은 k⊥별로 계산한 T(E, k⊥)를 평균해서 얻으며 transmission 계산용 k⊥ grid는 SCF용보다 더 촘촘하게 잡는 경우가 많음.

1D 나노와이어 전극은 수직 두 방향이 vacuum이므로 k⊥는 Γ 1점이고 와이어 축 방향만 전극 계산에서 여러 점을 씀. 이 경우 k-point 문제는 전극 bulk 수렴 하나로 줄어듦 ([[proj-example-nanowire-transport]]).

## Connections

- [[k-point-sampling]] — BZ 적분 수렴의 일반 원리
- [[electrode-self-energy]] — transport 방향 무한성이 들어가는 자리
- [[negf-landauer-formula]] — k⊥ 평균 transmission이 들어가는 공식
- [[proj-example-nanowire-transport]] — 1D 전극에서 설정이 단순해지는 예

## Refs

- M. Brandbyge, J.-L. Mozos, P. Ordejón, J. Taylor, and K. Stokbro, Phys. Rev. B 65, 165401 (2002).
- N. Papior, N. Lorente, T. Frederiksen, A. García, and M. Brandbyge, Comput. Phys. Commun. 212, 8 (2017).
- H. J. Monkhorst and J. D. Pack, Phys. Rev. B 13, 5188 (1976).
