---
title: Exchange-correlation functional의 선택이 DFT 결과의 정확도와 체계적 오차를 정한다
tags: [concept]
status: evergreen
created: 2026-10-06
updated: 2026-10-06
sources: []
---
# Exchange-Correlation Functionals

DFT의 근사는 E_xc[n] 하나에 모이며 functional 위계(LDA → GGA → hybrid)를 올라갈수록 비용과 정확도가 함께 올라감.

## Summary

- LDA: 각 지점의 density만 사용하는 균일 전자 기체 근사.
- GGA(PBE 등): density gradient를 추가함. 고체·분자 구조 계산의 표준 선택.
- hybrid(HSE 등): Hartree-Fock exchange 일부를 섞음. gap과 준위 위치를 개선하지만 비용이 큼.

## Details

LDA는 균일 전자 기체의 correlation energy(quantum Monte Carlo 결과)를 parametrize해서 씀. 결합 길이를 짧게, 결합 에너지를 크게 주는 경향이 알려져 있음.

GGA는 gradient 의존성을 넣어 LDA의 overbinding을 줄임. PBE는 실험 데이터에 fitting하지 않고 exact 조건으로 만든 non-empirical functional임. 다만 LDA와 GGA 모두 self-interaction error를 가지며 이 때문에 분자 HOMO가 너무 높게 놓이고 gap이 작게 나옴 ([[dft-band-gap-underestimation]]).

LDA와 GGA는 국소적 functional이라 멀리 떨어진 전하 요동 사이의 dispersion 상호작용을 담지 못함. 분자와 전극 사이 흡착 기하에서는 [[van-der-waals-corrections]]를 따로 더함.

hybrid functional은 HF exchange를 일부 섞어 self-interaction을 부분적으로 상쇄함. HSE는 exchange를 short-range와 long-range로 나누고 short-range에만 HF를 섞어 금속·고체 계산 비용을 낮춤. 그러나 큰 transport 계산에 hybrid를 쓰기는 어렵고 대신 사후 준위 보정 [[dft-sigma-level-correction]]이 자주 쓰임.

## Connections

- [[kohn-sham-equations]] — E_xc가 들어가는 자리
- [[dft-band-gap-underestimation]] — semilocal functional의 gap 오차
- [[van-der-waals-corrections]] — semilocal functional이 놓치는 분산 상호작용
- [[dft-sigma-level-correction]] — 큰 계에서 hybrid 대신 쓰는 준위 보정

## Refs

- D. M. Ceperley and B. J. Alder, Phys. Rev. Lett. 45, 566 (1980).
- J. P. Perdew and A. Zunger, Phys. Rev. B 23, 5048 (1981).
- J. P. Perdew, K. Burke, and M. Ernzerhof, Phys. Rev. Lett. 77, 3865 (1996).
- J. Heyd, G. E. Scuseria, and M. Ernzerhof, J. Chem. Phys. 118, 8207 (2003).
