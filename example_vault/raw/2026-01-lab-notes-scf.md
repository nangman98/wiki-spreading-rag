# 2026-01 실습 메모: 금속 전극 slab의 SCF 수렴

가상의 학습용 메모. 특정 계산 결과는 없음.

- 증상: 금속 slab에서 SCF 잔차가 줄지 않고 진동함.
- 첫 점검: mixing weight를 낮추고 history 길이를 늘림. Pulay/Broyden 계열이 단순 linear mixing보다 안정적이었음.
- 금속에서는 긴 파장의 charge sloshing이 원인일 수 있음. Kerker 형태의 preconditioning 항목을 매뉴얼에서 찾아볼 것.
- Fermi 준위 근처 occupation이 반복마다 뒤집히면 electronic smearing을 켬. smearing 폭을 바꾸면 total energy가 달라지므로 비교 계산끼리 같은 값을 써야 함.
- k-point grid가 너무 성기면 금속의 Fermi surface 표현이 흔들려 수렴이 느려짐. grid 수렴을 먼저 확인함.
- 수렴 기준은 density matrix 변화와 total energy 변화 두 가지를 함께 기록.
- 다음 할 일: transport 계산에서 유한 bias를 걸면 같은 문제가 더 심해지는지 확인.
