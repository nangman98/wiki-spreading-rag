---
title: Plane-wave cutoff는 목표 물리량의 차이가 허용 오차 안에 들어올 때까지 올려서 정한다
tags: [method]
status: evergreen
created: 2026-10-06
updated: 2026-10-06
sources: []
---
# Plane-Wave Cutoff Convergence

plane-wave basis의 크기는 kinetic energy cutoff 하나로 정해지며 cutoff는 total energy 자체가 아니라 비교하려는 에너지 차이·힘·응력의 수렴으로 판정함.

## Summary

- basis는 |k+G|²/2 < E_cut 조건을 만족하는 plane wave 전부임.
- cutoff를 올리면 total energy는 단조 감소하지만 에너지 차이는 더 빨리 수렴하는 경우가 많음.
- 필요한 cutoff는 [[pseudopotentials]]의 hardness가 정함.

## Details

plane wave는 원자 위치와 무관한 basis라 Pulay force가 없고 cutoff 하나로 체계적 수렴이 가능함. 이 점이 [[basis-sets-numerical-atomic-orbitals]]와 비교되는 장점임.

수렴 절차는 다음과 같음.

1. 고정된 구조와 [[k-point-sampling]] 조건에서 cutoff만 단계적으로 올림.
2. 목표 물리량(흡착 에너지, 격자 상수, 원자 힘)의 변화를 기록함.
3. 변화가 허용 오차 이하가 되는 가장 낮은 cutoff를 고르고 같은 프로젝트의 비교 계산에 모두 같은 값을 씀.

cell 크기를 바꾸는 relaxation에서는 plane wave 개수가 고정되어 유효 cutoff가 바뀜 (Pulay stress). 이 경우 수렴된 값보다 높은 cutoff를 쓰거나 cell을 바꾼 뒤 다시 계산함.

local orbital 코드에서도 real-space grid의 미세도를 같은 방식으로 수렴시킴. 예를 들어 SIESTA의 mesh cutoff는 Hartree·XC 퍼텐셜을 표현하는 grid를 정하며 basis 크기와는 별개로 점검해야 함.

## Connections

- [[pseudopotentials]] — 필요한 cutoff를 정하는 요인
- [[k-point-sampling]] — cutoff와 함께 수렴시켜야 하는 다른 축
- [[basis-sets-numerical-atomic-orbitals]] — 국소 basis와의 비교

## Refs

- M. C. Payne, M. P. Teter, D. C. Allan, T. A. Arias, and J. D. Joannopoulos, Rev. Mod. Phys. 64, 1045 (1992).
