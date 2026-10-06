---
title: 유한 bias I-V 곡선은 bias마다 non-equilibrium density를 self-consistent하게 다시 구하고 bias window의 transmission을 적분해서 얻는다
tags: [method]
status: evergreen
created: 2026-10-06
updated: 2026-10-06
sources: ["raw/2026-01-lab-notes-scf.md", "raw/2026-02-reading-notes-negf.md"]
---
# Finite-Bias I-V Curves

bias V를 걸면 두 전극의 화학 퍼텐셜이 eV만큼 벌어지고 device의 density와 Hamiltonian이 함께 바뀌므로 T(E)는 V마다 다시 계산해야 함.

## Summary

- 전류: I(V) = (2e/h) ∫ T(E, V) [f_L(E) − f_R(E)] dE.
- 적분은 사실상 bias window [μ_R, μ_L] 안의 T(E, V)만 기여함 (저온 극한).
- density는 equilibrium contour 적분과 bias window의 non-equilibrium 적분을 합쳐 구함.

## Details

0 bias에서는 density를 복소 에너지 평면의 contour 적분으로 효율적으로 계산함. 유한 bias에서는 μ_R과 μ_L 사이 에너지 구간에서 occupation이 전극마다 달라 실수 축 근처 적분이 추가로 필요함. 이 구간은 Green function이 날카로운 구조를 가져 촘촘한 에너지 grid가 필요함 ([[negf-landauer-formula]]).

bias에 따른 퍼텐셜 강하는 Poisson 방정식으로 self-consistent하게 정해짐. 전극 경계에서 퍼텐셜이 bulk 값으로 돌아오도록 device 버퍼 층을 충분히 넣어야 함 ([[electrode-self-energy]]).

표준 절차는 다음과 같음.

1. 0 V 계산을 수렴시키고 density matrix를 저장함.
2. 작은 bias 간격으로 V를 올리며 직전 bias의 density matrix를 초기값으로 씀.
3. 각 bias에서 T(E, V)를 구하고 bias window에서 적분해 I를 얻음.

bias가 커질수록 SCF 수렴이 어려워지므로 mixing weight를 낮추는 조정이 자주 필요함 ([[scf-mixing-convergence]], [[2026-01-lab-notes-scf]]). 결과를 해석할 때는 resonance가 bias window 안에 들어오는 bias에서 전류가 빠르게 늘어나는지 보고 그 resonance의 정체를 [[transmission-function-interpretation]]과 [[pdos-projection]]으로 확인함. 준위 위치 오차가 있으면 전류가 오르는 bias도 틀리므로 [[dft-sigma-level-correction]]의 영향을 함께 고려함.

## Connections

- [[negf-landauer-formula]] — 전류 공식의 출처
- [[scf-mixing-convergence]] — 유한 bias SCF의 수렴 전략
- [[transmission-function-interpretation]] — bias window 안 resonance 해석
- [[dft-sigma-level-correction]] — 준위 오차가 I-V에 주는 영향

## Refs

- M. Brandbyge, J.-L. Mozos, P. Ordejón, J. Taylor, and K. Stokbro, Phys. Rev. B 65, 165401 (2002).
- J. Taylor, H. Guo, and J. Wang, Phys. Rev. B 63, 245407 (2001).
- S. Datta, Electronic Transport in Mesoscopic Systems (Cambridge University Press, 1995).
