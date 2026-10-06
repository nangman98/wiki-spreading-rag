---
title: DFT+Σ는 기체상 IP/EA 보정과 전극 image-charge 보정으로 분자 준위를 옮겨 transmission resonance 위치를 고친다
tags: [method]
status: evergreen
created: 2026-10-06
updated: 2026-10-06
sources: ["raw/2026-03-seminar-notes-level-alignment.md"]
---
# DFT+Σ Level Correction

Neaton, Hybertsen, Louie(2006)는 금속 표면 근처 분자의 준입자 gap이 기체상보다 작아지는 것을 보였고 이 아이디어를 semilocal DFT 분자 준위에 적용하는 보정이 DFT+Σ임.

## Summary

- 1단계 (기체상 보정): 점유 준위를 −IP에, 비점유 준위를 −EA에 맞추도록 이동함.
- 2단계 (image-charge 보정): 전극 polarization이 gap을 줄이는 양을 고전 image-charge 모형으로 추정해 되돌림.
- 결과적으로 HOMO는 내려가고 LUMO는 올라가 resonance가 E_F에서 멀어짐.

## Details

semilocal DFT는 기체상 분자의 gap을 작게 줌 ([[dft-band-gap-underestimation]]). 1단계에서는 기체상 계산으로 IP와 EA를 따로 구하고 (ΔSCF 또는 GW), HOMO에 Σ_occ = −IP − ε_HOMO, LUMO에 Σ_unocc = −EA − ε_LUMO 크기의 shift를 줌.

분자가 금속 표면에 가까워지면 전자를 더하거나 뺀 상태가 금속의 image charge로 안정화됨. 이 효과는 점유 준위를 올리고 비점유 준위를 내려 gap을 줄임. 점전하가 완전 도체 평면에서 거리 d만큼 떨어져 있을 때 image 상호작용 에너지는 e²/(16πε0 d)이고 분자에서는 이 값을 분자 전하 분포와 image plane 위치로 계산함. 2단계는 이 양만큼 1단계 shift를 되돌림.

실제 구현에서는 분자 orbital에 projector를 걸어 Kohn-Sham Hamiltonian의 분자 블록에 shift를 더한 뒤 transmission을 다시 계산함 ([[negf-landauer-formula]]). 보정량은 image plane 위치와 분자-전극 거리에 민감하므로, 그 선택 근거와 흡착 기하 ([[van-der-waals-corrections]])를 함께 기록해야 함. 세미나 메모 [[2026-03-seminar-notes-level-alignment]]에 절차를 정리함.

보정 후 T(E)를 보정 전과 같은 축에 겹쳐 resonance가 얼마나 이동했는지 확인함 ([[transmission-function-interpretation]]).

## Connections

- [[dft-band-gap-underestimation]] — 보정이 필요한 원인
- [[transmission-function-interpretation]] — 보정 결과를 T(E)에서 읽는 법
- [[van-der-waals-corrections]] — 흡착 거리가 image-charge 보정량을 정함
- [[pdos-projection]] — 보정 전후 분자 준위 위치 확인

## Refs

- J. B. Neaton, M. S. Hybertsen, and S. G. Louie, Phys. Rev. Lett. 97, 216405 (2006).
- S. Y. Quek et al., Nano Lett. 7, 3477 (2007).
