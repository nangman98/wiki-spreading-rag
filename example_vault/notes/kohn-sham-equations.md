---
title: Kohn-Sham 방정식은 상호작용 전자의 ground-state density를 비상호작용 보조계의 단일입자 방정식으로 재현한다
tags: [concept]
status: evergreen
created: 2026-10-06
updated: 2026-10-06
sources: []
---
# Kohn-Sham Equations

Kohn-Sham 방정식은 다전자 문제를 effective potential 속 단일입자 문제로 바꾸고 근사는 exchange-correlation 항 하나에 모은다.

## Summary

- Hohenberg-Kohn 정리: 외부 퍼텐셜과 ground-state density는 일대일 대응이고 에너지 functional의 최솟값이 ground-state energy임.
- Kohn-Sham 방식: 같은 density를 갖는 가상의 비상호작용 전자계를 도입함.
- 미지의 다체 효과는 exchange-correlation energy E_xc[n]에 모두 들어감.

## Details

Kohn-Sham 방정식은 [−(1/2)∇² + v_ext(r) + v_H(r) + v_xc(r)] φ_i(r) = ε_i φ_i(r) 형태임 (atomic units). density는 occupied orbital의 합 n(r) = Σ_i |φ_i(r)|²로 구함. v_H와 v_xc가 n에 의존하므로 방정식은 self-consistent하게 풀어야 하며 이 반복 과정의 안정성은 [[scf-mixing-convergence]]에서 다룸.

orbital을 전개하는 basis 선택이 실제 계산의 정확도와 비용을 정함. plane wave는 [[plane-wave-cutoff-convergence]], 국소 basis는 [[basis-sets-numerical-atomic-orbitals]]에 정리함. core 전자는 보통 [[pseudopotentials]]로 대체함.

Kohn-Sham eigenvalue ε_i는 원칙적으로 보조계의 Lagrange multiplier임. exact functional에서도 최고 점유 준위만 ionization potential과 일치하며 나머지 eigenvalue를 준입자 에너지로 읽으면 체계적 오차가 생김. 이 점이 [[dft-band-gap-underestimation]]의 출발점임.

주기계에서는 Bloch 정리로 orbital에 k 지표가 붙고 density 계산은 Brillouin zone 적분이 됨 ([[k-point-sampling]]).

## Connections

- [[exchange-correlation-functionals]] — 유일한 근사 항 E_xc의 선택지
- [[scf-mixing-convergence]] — self-consistent 해를 찾는 반복 절차
- [[dft-band-gap-underestimation]] — eigenvalue를 준입자 에너지로 해석할 때의 한계
- [[k-point-sampling]] — 주기계에서 density를 구하는 BZ 적분

## Refs

- P. Hohenberg and W. Kohn, Phys. Rev. 136, B864 (1964).
- W. Kohn and L. J. Sham, Phys. Rev. 140, A1133 (1965).
