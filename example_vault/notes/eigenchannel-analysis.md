---
title: Eigenchannel 분석은 transmission을 서로 독립인 채널로 분해해 전류가 흐르는 orbital 경로를 실공간에서 보여준다
tags: [method]
status: evergreen
created: 2026-10-06
updated: 2026-10-06
sources: []
---
# Eigenchannel Analysis

transmission 행렬 t†t의 eigenvalue τ_n은 각 채널의 투과율이고 합 Σ_n τ_n이 T(E)임. eigenvector는 해당 채널의 산란 상태를 실공간에 그릴 수 있게 함.

## Summary

- T(E) = Tr[t†t] = Σ_n τ_n, 0 ≤ τ_n ≤ 1.
- 소수의 채널이 T(E)를 지배하는 경우가 많아, 몇 개 채널만 보면 수송 경로를 알 수 있음.
- 채널 파동함수의 orbital 성분과 위상으로 어떤 분자 orbital이 수송을 담당하는지 판정함.

## Details

[[negf-landauer-formula]]의 Γ_L G Γ_R G† 형태는 한 에너지에서 Hermitian 행렬로 바꿔 대각화할 수 있음. Paulsson과 Brandbyge의 방법은 왼쪽 전극에서 들어오는 산란 상태 공간(spectral function A_L = G Γ_L G†)을 먼저 구하고 그 공간에서 Γ_R을 대각화해 eigenchannel을 얻음.

채널 수의 상한은 가장 좁은 단면의 orbital 수가 정함. 예를 들어 단일 원자 금속 접점은 valence orbital 개수만큼의 채널만 가질 수 있고 분자 접합은 보통 한두 채널이 지배적임.

해석 절차는 다음과 같음.

1. T(E)의 관심 peak 또는 E_F에서 τ_n 목록을 구함 ([[transmission-function-interpretation]]).
2. 지배적 채널의 파동함수를 실공간 grid에 그림.
3. 분자 위의 lobe 모양을 분자 orbital과 비교하고 [[pdos-projection]]의 원자·orbital 성분과 대조함.

국소 basis에서는 채널 eigenvector가 orbital 계수로 바로 나오므로 원자별 기여를 쉽게 읽을 수 있음 ([[basis-sets-numerical-atomic-orbitals]]).

## Connections

- [[transmission-function-interpretation]] — 채널 분해의 대상인 T(E)
- [[pdos-projection]] — 같은 에너지에서 orbital 성분 교차 확인
- [[basis-sets-numerical-atomic-orbitals]] — orbital 계수로 채널을 읽는 근거
- [[negf-landauer-formula]] — t†t의 출처

## Refs

- M. Paulsson and M. Brandbyge, Phys. Rev. B 76, 115117 (2007).
- S. Datta, Electronic Transport in Mesoscopic Systems (Cambridge University Press, 1995).
