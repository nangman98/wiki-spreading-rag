---
title: PDOS는 전체 DOS를 원자와 orbital 성분으로 나눠 transmission peak와 band의 orbital 기원을 판정하게 한다
tags: [method]
status: evergreen
created: 2026-10-06
updated: 2026-10-06
sources: []
---
# PDOS Projection

projected density of states(PDOS)는 각 eigenstate의 weight를 basis orbital에 나눠 담은 DOS이며 원자 중심 basis에서는 원자·각운동량별 합으로 바로 얻음.

## Summary

- 비직교 basis에서는 overlap S를 고려한 Mulliken 방식으로 weight를 나눔.
- 원소별, 원자별, 각운동량(s, p, d)별로 합쳐 그림.
- 접합 계산에서는 device 영역 Green function에서 분자 원자만 골라 PDOS를 얻음.

## Details

주기계에서 orbital μ의 PDOS는 band와 k에 대한 합 Σ_nk Re[c*_μnk (S c_nk)_μ] δ(E − ε_nk)로 쓸 수 있음. 모든 μ를 더하면 전체 DOS가 됨. 비직교 basis의 overlap 항을 반씩 나누는 Mulliken 방식은 단순하지만 basis에 따라 값이 달라지므로, 절대값보다 에너지 위치와 상대 비중을 비교하는 용도로 씀 ([[basis-sets-numerical-atomic-orbitals]]).

δ 함수는 Gaussian 또는 Lorentzian broadening으로 대체함. broadening 폭은 그림의 모양을 바꾸므로 비교하는 그림끼리 같은 값을 씀. 수렴된 [[k-point-sampling]] 위에서 계산해야 함.

NEGF 접합에서는 device Green function으로 PDOS_μ(E) = −(1/π) Im[G S]_μμ를 계산함. 분자 원자의 PDOS peak를 T(E)와 같은 에너지 축(E − E_F)에 겹치면 각 transmission resonance가 어떤 분자 orbital에서 오는지 판정할 수 있음 ([[transmission-function-interpretation]]). PDOS peak가 있는데 T(E) peak가 없으면 전극과 약하게 결합한 국소 상태일 가능성이 있으며 [[eigenchannel-analysis]]로 교차 확인함.

[[dft-sigma-level-correction]]을 적용했다면 보정 전후 분자 PDOS peak 위치를 함께 보고해 shift가 의도대로 들어갔는지 확인함.

## Connections

- [[transmission-function-interpretation]] — PDOS와 T(E)를 겹쳐 peak 기원 판정
- [[eigenchannel-analysis]] — orbital 기원의 교차 확인
- [[basis-sets-numerical-atomic-orbitals]] — Mulliken 분할이 basis에 의존하는 이유
- [[dft-sigma-level-correction]] — 보정 shift 확인

## Refs

- R. S. Mulliken, J. Chem. Phys. 23, 1833 (1955).
- M. Brandbyge, J.-L. Mozos, P. Ordejón, J. Taylor, and K. Stokbro, Phys. Rev. B 65, 165401 (2002).
