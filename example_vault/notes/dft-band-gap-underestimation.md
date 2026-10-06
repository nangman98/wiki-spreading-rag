---
title: Semilocal DFT의 Kohn-Sham gap은 준입자 gap보다 체계적으로 작고 분자 HOMO는 너무 높게 놓인다
tags: [concept]
status: evergreen
created: 2026-10-06
updated: 2026-10-06
sources: ["raw/2026-03-seminar-notes-level-alignment.md"]
---
# DFT Band-Gap Underestimation

LDA·GGA의 Kohn-Sham gap은 측정되는 준입자 gap(IP − EA)보다 작으며 이 오차는 functional 근사와 Kohn-Sham eigenvalue의 해석 두 곳에서 나옴.

## Summary

- 준입자 gap = IP − EA = Kohn-Sham gap + derivative discontinuity Δ_xc.
- semilocal functional은 Δ_xc가 0이고 self-interaction error가 있어 gap을 작게 줌.
- 분자에서는 −ε_HOMO가 IP보다 작게 나와 HOMO가 너무 높게 놓임.

## Details

전자 수 N에 대한 exact 에너지 E(N)은 정수 N 사이에서 직선이고 정수점에서 기울기가 꺾임. 이 꺾임 때문에 exact functional에서도 xc 퍼텐셜이 정수 N을 지날 때 상수 Δ_xc만큼 뜀(Perdew-Levy, Sham-Schlüter). Kohn-Sham gap에 Δ_xc를 더해야 준입자 gap이 됨 ([[kohn-sham-equations]]).

LDA와 GGA의 E(N)은 정수 사이에서 아래로 볼록하게 휘어 Δ_xc를 0으로 만들고 전자가 자기 자신과 상호작용하는 self-interaction error 때문에 점유 준위가 위로 올라감. 결과적으로 −ε_HOMO는 IP보다 작고 LUMO는 EA 기준보다 낮게 놓임 ([[exchange-correlation-functionals]]).

준입자 gap을 직접 계산하려면 GW 근사가 표준이고 분자 기체상에서는 ΔSCF 방식으로 IP = E(N−1) − E(N), EA = E(N) − E(N+1)을 total energy 차이로 구할 수 있음.

분자 접합에서는 이 오차가 HOMO와 LUMO를 E_F 쪽으로 끌어당겨 transmission resonance가 E_F에 너무 가깝게 놓임. 그 결과 zero-bias conductance가 과대평가되기 쉬움 ([[transmission-function-interpretation]]). 전극 표면의 polarization은 이와 반대로 실제 gap을 줄이는데, semilocal DFT는 이 효과도 담지 못함. 두 효과를 함께 다루는 보정이 [[dft-sigma-level-correction]]임.

## Connections

- [[dft-sigma-level-correction]] — 이 오차를 transport 계산에서 보정하는 방법
- [[transmission-function-interpretation]] — 준위 오차가 T(E_F)에 주는 영향
- [[exchange-correlation-functionals]] — self-interaction error의 출처
- [[kohn-sham-equations]] — eigenvalue 해석의 한계

## Refs

- J. P. Perdew and M. Levy, Phys. Rev. Lett. 51, 1884 (1983).
- L. J. Sham and M. Schlüter, Phys. Rev. Lett. 51, 1888 (1983).
- M. S. Hybertsen and S. G. Louie, Phys. Rev. B 34, 5390 (1986).
