# 2026-02 읽기 메모: NEGF와 Landauer 공식

가상의 학습용 메모. Datta 교재와 Brandbyge et al. (2002) 읽으면서 정리.

- 계를 left electrode / device / right electrode로 나눔. 전극은 반무한이고 주기적.
- 전극의 영향은 self-energy Σ_L, Σ_R로 device Hamiltonian에 더해짐. Σ의 허수부에서 broadening Γ = i(Σ − Σ†)가 나옴.
- retarded Green function G = [ES − H − Σ_L − Σ_R]^(-1).
- transmission T(E) = Tr[Γ_L G Γ_R G†]. 0 bias, 저온 극한에서 conductance G = G0 T(E_F), G0 = 2e²/h.
- 전극 surface Green function은 반복 decimation으로 구함 (Lopez Sancho 방식).
- 질문: 전극 계산의 k-point를 transport 방향으로 얼마나 촘촘히 잡아야 하는가? device 계산과 어떻게 맞추는가?
- 질문: 유한 bias에서는 density를 equilibrium contour와 non-equilibrium window로 나눠 적분한다고 함. 다음 달에 정리.
