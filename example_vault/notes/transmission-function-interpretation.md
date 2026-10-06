---
title: 분자 접합의 transmission peak 위치는 분자 준위 정렬을, peak 폭은 전극 coupling을 나타낸다
tags: [concept]
status: evergreen
created: 2026-10-06
updated: 2026-10-06
sources: ["raw/2026-03-seminar-notes-level-alignment.md"]
---
# Interpreting the Transmission Function

약하게 결합된 분자 접합의 T(E)는 분자 orbital마다 하나씩 Lorentzian 모양 resonance를 보이며 zero-bias conductance는 E_F에서 그 꼬리의 높이로 정해짐.

## Summary

- peak 위치 ≈ 전극 결합으로 이동된 분자 준위 (HOMO, LUMO 등).
- peak 폭 ≈ Γ_L + Γ_R, 분자와 두 전극의 coupling 세기.
- E_F가 HOMO-LUMO gap 안에 있으면 conductance는 가까운 resonance의 꼬리가 정함 (off-resonant tunneling).

## Details

단일 준위 모형에서 T(E) = Γ_L Γ_R / [(E − ε0)² + ((Γ_L + Γ_R)/2)²]임. 대칭 결합(Γ_L = Γ_R)이면 peak 높이가 1이고 비대칭이면 1보다 낮아짐. 이 모형은 [[negf-landauer-formula]]의 일반식을 준위 하나와 에너지 무관한 Γ로 줄인 것임.

E_F가 gap 안에 있으면 T(E_F)는 대략 Γ²/(E_F − ε0)²에 비례함. 준위가 E_F에 얼마나 가까운지가 conductance를 크게 좌우함. semilocal DFT는 분자 준위를 E_F에 너무 가깝게 놓는 경향이 있어 T(E_F)를 과대평가하기 쉬움 ([[dft-band-gap-underestimation]]). 이를 보정한 뒤 resonance가 E_F로부터 멀어지는지 확인하는 것이 [[dft-sigma-level-correction]]의 목적임.

어느 orbital이 어떤 peak를 만드는지는 T(E)만으로는 알 수 없음. 같은 에너지 축에서 분자 [[pdos-projection]]을 겹쳐 보거나, [[eigenchannel-analysis]]로 채널의 공간 분포를 그려 확인함.

peak 폭은 분자-전극 거리와 anchoring 기하에 민감하므로 relaxation 조건 ([[van-der-waals-corrections]])을 함께 기록함. 여러 자릿수에 걸친 T(E)는 log 축으로 그려야 꼬리와 peak를 함께 볼 수 있음.

## Connections

- [[negf-landauer-formula]] — T(E)의 정의와 계산식
- [[dft-sigma-level-correction]] — peak 위치를 보정하는 방법
- [[pdos-projection]] — peak의 orbital 기원 확인
- [[eigenchannel-analysis]] — peak를 채널별로 공간 분해
- [[electrode-self-energy]] — 폭을 정하는 Γ의 출처

## Refs

- S. Datta, Electronic Transport in Mesoscopic Systems (Cambridge University Press, 1995).
- J. C. Cuevas and E. Scheer, Molecular Electronics: An Introduction to Theory and Experiment (World Scientific, 2010).
