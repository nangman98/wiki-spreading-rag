---
title: 1D 나노와이어 전극 사이 분자 접합의 transmission 계산을 전극 수렴부터 I-V까지 순서대로 익히는 예시 프로젝트
tags: [project]
status: evergreen
created: 2026-10-06
updated: 2026-10-06
sources: ["raw/2026-01-lab-notes-scf.md", "raw/2026-02-reading-notes-negf.md", "raw/2026-03-seminar-notes-level-alignment.md"]
---
# Example Project: Nanowire-Molecule Junction Transport

가상의 학습 프로젝트. 두 개의 반무한 1D 금속 나노와이어 전극 사이에 작은 유기 분자를 끼운 접합에서 T(E)와 I-V를 계산하는 절차를 익힘. 결과 수치는 기록하지 않음.

## Summary

- 목표: DFT-NEGF 계산의 각 단계를 순서대로 수행하고 단계마다 어떤 수렴·보정을 점검하는지 익힘.
- 구성: 1D 전극 bulk → 기체상 분자 → 접합 relaxation → 0 V transport → 분석 → 준위 보정 → 유한 bias.
- 필요 개념: [[moc-dft-basics]], [[moc-quantum-transport]].

## Details

1. **전극 bulk 계산**: 와이어 축 방향 k-grid와 basis·mesh 수렴을 확인함 ([[kpoints-in-transport-direction]], [[basis-sets-numerical-atomic-orbitals]], [[plane-wave-cutoff-convergence]]). SCF가 진동하면 [[scf-mixing-convergence]]를 참고함.
2. **기체상 분자 계산**: 같은 functional과 [[pseudopotentials]]로 분자를 relax하고 ΔSCF로 IP와 EA를 구함 ([[dft-band-gap-underestimation]]).
3. **접합 구조 relaxation**: 분자와 양쪽 전극 끝 원자를 relax하고 dispersion 보정 여부를 기록함 ([[van-der-waals-corrections]]).
4. **0 V transport 계산**: 전극 [[electrode-self-energy]]를 붙여 device density를 수렴시키고 T(E)를 구함 ([[negf-landauer-formula]]).
5. **분석**: T(E)를 log 축으로 그리고 분자 [[pdos-projection]]과 [[eigenchannel-analysis]]로 peak의 orbital 기원을 판정함 ([[transmission-function-interpretation]]).
6. **준위 보정**: 2단계의 IP/EA와 image-charge 모형으로 [[dft-sigma-level-correction]]을 적용하고 보정 전후 T(E)를 비교함.
7. **유한 bias**: 0 V density matrix에서 시작해 bias를 단계적으로 올리며 I-V를 계산함 ([[finite-bias-iv-curves]]).

참고 원본 메모: [[2026-01-lab-notes-scf]], [[2026-02-reading-notes-negf]], [[2026-03-seminar-notes-level-alignment]].

## Connections

- [[moc-quantum-transport]] — transport 개념 목차
- [[moc-dft-basics]] — DFT 기초 목차
- [[kpoints-in-transport-direction]] — 1D 전극에서 k-point 설정
- [[dft-sigma-level-correction]] — 6단계 보정의 근거
- [[finite-bias-iv-curves]] — 7단계 절차

## Refs

- M. Brandbyge, J.-L. Mozos, P. Ordejón, J. Taylor, and K. Stokbro, Phys. Rev. B 65, 165401 (2002).
- J. B. Neaton, M. S. Hybertsen, and S. G. Louie, Phys. Rev. Lett. 97, 216405 (2006).
- S. Datta, Electronic Transport in Mesoscopic Systems (Cambridge University Press, 1995).
