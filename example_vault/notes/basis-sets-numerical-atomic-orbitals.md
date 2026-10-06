---
title: Numerical atomic orbital basis는 국소성 덕분에 큰 계와 NEGF transport 계산에 적합하지만 수렴을 체계적으로 점검하기 어렵다
tags: [concept]
status: evergreen
created: 2026-10-06
updated: 2026-10-06
sources: []
---
# Basis Sets: Numerical Atomic Orbitals

numerical atomic orbital(NAO)은 원자 중심의 유한 범위 함수로, Hamiltonian을 sparse하게 만들어 큰 계와 [[negf-landauer-formula]] 기반 transport 계산을 가능하게 함.

## Summary

- 각 orbital은 radial 함수와 spherical harmonic의 곱이며 cutoff radius 밖에서 정확히 0임.
- single-ζ(SZ) → double-ζ(DZ) → DZ + polarization(DZP)으로 basis를 키움.
- 원자 중심 basis이므로 basis set superposition error(BSSE)와 Pulay force가 생김.

## Details

radial 함수는 confinement 조건 아래 원자 문제를 풀어 얻음. confinement를 정하는 기준으로 energy shift를 쓰며 값이 작을수록 orbital 범위가 길어져 정확도와 비용이 함께 올라감. 두 번째 ζ는 split-valence 방식으로 만들고 polarization orbital은 각운동량이 하나 더 높은 함수를 추가함.

국소 basis에서는 Hamiltonian H와 overlap S가 이웃 원자 사이에서만 0이 아니므로 device를 주층(principal layer) 단위로 나누기 쉬움. 이 구조 덕분에 [[electrode-self-energy]] 계산과 Green function 역행렬 계산이 효율적임.

basis가 원자를 따라 움직이므로 힘 계산에 Pulay 항이 들어감. 분자 흡착 에너지처럼 두 조각의 에너지를 빼는 경우 BSSE가 결합을 과대평가하므로 counterpoise 보정을 고려함.

orbital이 원자에 붙어 있다는 점은 분석에도 유리함. [[pdos-projection]]과 [[eigenchannel-analysis]]는 basis 지표를 원자와 orbital 종류로 바로 묶어 해석함. 반대로 basis 완전성을 [[plane-wave-cutoff-convergence]]처럼 숫자 하나로 수렴시킬 수는 없음.

## Connections

- [[pdos-projection]] — orbital 지표를 원자·각운동량별로 묶는 분석
- [[electrode-self-energy]] — sparse H, S가 전극 계산을 효율화함
- [[plane-wave-cutoff-convergence]] — 체계적 수렴이 가능한 plane-wave basis와의 대비
- [[pseudopotentials]] — 원소별 basis와 짝을 이루는 퍼텐셜

## Refs

- J. M. Soler et al., J. Phys.: Condens. Matter 14, 2745 (2002).
- J. Junquera, Ó. Paz, D. Sánchez-Portal, and E. Artacho, Phys. Rev. B 64, 235111 (2001).
- S. F. Boys and F. Bernardi, Mol. Phys. 19, 553 (1970).
