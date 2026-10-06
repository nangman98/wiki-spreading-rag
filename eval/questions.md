# 평가 질문 (예시)

질문마다 정답 노트(gold)는 답에 필요한 노트들이다. `python3 src/eval.py --vault example_vault`가 BM25만(α=0)과 확산(α=0.5)의 Recall@k를 잰다.

| # | 질문 | gold |
|---|---|---|
| 1 | PBE로 계산한 분자 접합의 zero-bias conductance가 실험보다 크게 나오는 이유와 보정 방법은? | dft-band-gap-underestimation, dft-sigma-level-correction, transmission-function-interpretation |
| 2 | 1D 나노와이어 전극의 transport 계산에서 전극 계산과 device 계산의 k-point를 각각 어떻게 잡고, 그 이유는? | kpoints-in-transport-direction, electrode-self-energy, k-point-sampling, negf-landauer-formula |
| 3 | transmission peak가 어느 원자의 어떤 orbital에서 오는지 판정하려면 무엇을 계산하나? | transmission-function-interpretation, pdos-projection, eigenchannel-analysis, basis-sets-numerical-atomic-orbitals |
| 4 | bias를 올렸더니 SCF가 수렴하지 않는다. 무엇을 바꿔야 하나? | finite-bias-iv-curves, scf-mixing-convergence |
