---
title: LDA와 GGA는 dispersion 상호작용을 담지 못하므로 분자 흡착 기하에는 van der Waals 보정이 필요하다
tags: [method]
status: evergreen
created: 2026-10-06
updated: 2026-10-06
sources: []
---
# Van der Waals Corrections

dispersion은 떨어진 두 전하 분포의 상관된 요동에서 생기는 비국소 상관 효과라서, 국소 또는 semilocal [[exchange-correlation-functionals]]로는 재현되지 않음.

## Summary

- 원자쌍 보정(DFT-D2, DFT-D3): −C6/R⁶ 형태 항을 damping 함수와 함께 total energy에 더함.
- 비국소 functional(vdW-DF): correlation에 두 지점 density를 잇는 비국소 kernel을 넣음.
- Tkatchenko-Scheffler: C6 계수를 Hirshfeld 분할로 원자 환경에 맞게 조정함.

## Details

원자쌍 보정은 계산 비용이 거의 없고 기존 functional에 그대로 덧붙일 수 있음. D2는 원소별 고정 C6 계수를 쓰고 D3는 배위수에 따라 C6를 바꾸며 three-body 항을 선택적으로 포함함. 짧은 거리에서는 functional 자체가 이미 일부 상관을 담으므로 damping 함수로 이중 계산을 피함.

vdW-DF 계열은 dispersion을 functional 안에서 self-consistent하게 다루며 층상 물질과 표면 흡착에 널리 쓰임. 짝을 이루는 exchange functional의 선택에 따라 결과가 달라짐.

분자 접합에서 vdW 보정은 주로 분자-전극 거리와 흡착 기하를 바꿈. 거리 변화는 전극과의 coupling(T(E) peak 폭)과 image-charge 보정량에 직접 영향을 주므로, transport 계산 전 구조 relaxation 단계에서 어떤 보정을 썼는지 기록해야 함 ([[dft-sigma-level-correction]], [[transmission-function-interpretation]]).

vdW 보정은 Kohn-Sham eigenvalue 자체를 크게 바꾸지 않으므로 [[dft-band-gap-underestimation]] 문제를 해결하지 않음.

## Connections

- [[exchange-correlation-functionals]] — semilocal functional이 dispersion을 놓치는 이유
- [[dft-sigma-level-correction]] — 흡착 거리가 image-charge 보정량을 바꿈
- [[transmission-function-interpretation]] — 흡착 기하가 peak 폭을 바꿈
- [[proj-example-nanowire-transport]] — 접합 구조 relaxation 단계에서 사용

## Refs

- S. Grimme, J. Comput. Chem. 27, 1787 (2006).
- S. Grimme, J. Antony, S. Ehrlich, and H. Krieg, J. Chem. Phys. 132, 154104 (2010).
- M. Dion, H. Rydberg, E. Schröder, D. C. Langreth, and B. I. Lundqvist, Phys. Rev. Lett. 92, 246401 (2004).
- A. Tkatchenko and M. Scheffler, Phys. Rev. Lett. 102, 073005 (2009).
