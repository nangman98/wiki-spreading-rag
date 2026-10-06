---
title: 전극 self-energy는 반무한 주기 전극을 device 경계의 유한 행렬로 접어 넣는다
tags: [method]
status: evergreen
created: 2026-10-06
updated: 2026-10-06
sources: ["raw/2026-02-reading-notes-negf.md"]
---
# Electrode Self-Energy

반무한 전극은 직접 다룰 수 없으므로, 전극의 surface Green function으로 self-energy Σ_α(E)를 만들어 device Hamiltonian의 경계 블록에 더함.

## Summary

- Σ_α(E) = (ES_dα − H_dα) g_α(E) (ES_αd − H_αd), g_α는 전극 surface Green function.
- g_α는 주층(principal layer)을 반복 결합하는 decimation 방식으로 구함 (Lopez Sancho 등).
- 전극 H와 S는 별도의 bulk 전극 계산에서 가져오므로 전극 계산과 device 계산의 설정이 일관되어야 함.

## Details

전극은 transport 방향으로 같은 주층이 반복된다고 가정함. 주층은 가장 가까운 이웃 주층하고만 결합하도록 충분히 길게 잡아야 함. 국소 basis에서는 orbital 범위가 유한하므로 이 조건을 맞추기 쉬움 ([[basis-sets-numerical-atomic-orbitals]]).

surface Green function은 decimation 반복으로 주층 개수를 두 배씩 늘려 가며 수렴시킴. 수렴은 E에 작은 허수부 η를 더한 E + iη에서 계산하며 η는 수치 안정성용 broadening임.

Σ의 허수부에서 broadening Γ_α = i(Σ_α − Σ_α†)가 나오며 이는 [[negf-landauer-formula]]의 T(E) 공식에 직접 들어감. Γ가 크면 분자 준위가 전극과 강하게 결합해 넓은 peak를 만듦 ([[transmission-function-interpretation]]).

transport 방향에 수직인 방향이 주기적이면 Σ는 수직 k마다 따로 계산하고 transport 방향 k는 surface Green function 계산에 이미 적분되어 있음. 전극 bulk 계산에서는 transport 방향 k-point를 촘촘히 잡아야 함 ([[kpoints-in-transport-direction]]).

device 영역은 전극 쪽 버퍼 층을 충분히 포함해 경계에서 퍼텐셜이 bulk 전극 값으로 돌아오게 해야 함. 이 조건이 깨지면 경계에서 인공적인 산란이 생김.

## Connections

- [[negf-landauer-formula]] — Σ와 Γ가 들어가는 공식
- [[kpoints-in-transport-direction]] — 전극 계산의 k-point 규칙
- [[k-point-sampling]] — 수직 방향 k 평균의 일반 원리
- [[transmission-function-interpretation]] — Γ가 peak 폭을 정함

## Refs

- M. P. Lopez Sancho, J. M. Lopez Sancho, and J. Rubio, J. Phys. F 15, 851 (1985).
- M. Brandbyge, J.-L. Mozos, P. Ordejón, J. Taylor, and K. Stokbro, Phys. Rev. B 65, 165401 (2002).
- S. Datta, Electronic Transport in Mesoscopic Systems (Cambridge University Press, 1995).
