---
title: NEGF는 전극에 연결된 device의 transmission을 Green function과 self-energy로 계산하고 Landauer 공식으로 전류를 준다
tags: [concept]
status: evergreen
created: 2026-10-06
updated: 2026-10-06
sources: ["raw/2026-02-reading-notes-negf.md"]
---
# NEGF and the Landauer Formula

coherent 수송 영역에서 전류는 전극 사이 에너지별 transmission T(E)의 적분이며 NEGF는 T(E)를 device Green function으로 계산하는 틀임.

## Summary

- 계를 left electrode / device(scattering region) / right electrode로 나눔.
- retarded Green function: G(E) = [ES − H − Σ_L(E) − Σ_R(E)]⁻¹.
- transmission: T(E) = Tr[Γ_L G Γ_R G†], Γ_α = i(Σ_α − Σ_α†).
- 0 bias, 저온 conductance: G = G0 T(E_F), G0 = 2e²/h (spin 축퇴 포함).

## Details

반무한 전극의 영향은 [[electrode-self-energy]] Σ_L, Σ_R로 device 부분 행렬에 들어감. Σ의 실수부는 device 준위를 이동시키고 허수부에서 나오는 Γ는 준위의 broadening(전극으로 빠져나가는 비율)을 나타냄.

유한 bias V에서 전류는 Landauer-Büttiker 공식 I = (2e/h) ∫ T(E, V) [f_L(E) − f_R(E)] dE로 계산함. f_L과 f_R은 각 전극의 화학 퍼텐셜 μ_L, μ_R을 가진 Fermi 분포이고 μ_L − μ_R = eV임. 계산 절차와 bias window의 의미는 [[finite-bias-iv-curves]]에 정리함.

이 공식은 전자가 device 안에서 위상을 잃지 않는 coherent, elastic 수송을 가정함. 전자-포논 산란이나 강한 전자 상관은 별도 self-energy가 필요하며 이 노트의 범위 밖임.

DFT-NEGF에서 H는 Kohn-Sham Hamiltonian이므로, T(E)의 peak 위치는 Kohn-Sham 준위의 오차를 그대로 물려받음 ([[dft-band-gap-underestimation]]). 계산 자체는 [[basis-sets-numerical-atomic-orbitals]]처럼 국소 basis에서 효율적임. 읽기 메모 [[2026-02-reading-notes-negf]]에 유도 과정을 정리함.

## Connections

- [[electrode-self-energy]] — Σ와 Γ의 계산 방법
- [[transmission-function-interpretation]] — 계산된 T(E) 읽는 법
- [[finite-bias-iv-curves]] — bias window 적분으로 전류 계산
- [[kpoints-in-transport-direction]] — 전극과 device 계산의 k-point 규칙

## Refs

- R. Landauer, IBM J. Res. Dev. 1, 223 (1957).
- C. Caroli, R. Combescot, P. Nozières, and D. Saint-James, J. Phys. C 4, 916 (1971).
- M. Büttiker, Phys. Rev. Lett. 57, 1761 (1986).
- Y. Meir and N. S. Wingreen, Phys. Rev. Lett. 68, 2512 (1992).
- S. Datta, Electronic Transport in Mesoscopic Systems (Cambridge University Press, 1995).
- M. Brandbyge, J.-L. Mozos, P. Ordejón, J. Taylor, and K. Stokbro, Phys. Rev. B 65, 165401 (2002).
