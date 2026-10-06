# 2026-03 세미나 메모: 분자 준위 정렬과 DFT+Σ

가상의 학습용 메모. 공개 논문(Neaton, Hybertsen, Louie, PRL 97, 216405, 2006) 내용을 정리함.

- 문제: semilocal DFT로 계산한 분자 접합의 conductance가 실험보다 큰 경향. 원인 후보는 HOMO/LUMO 위치.
- 기체상 분자: Kohn-Sham HOMO 에너지의 절댓값이 ionization potential보다 작음. gap도 작게 나옴.
- 금속 표면 근처: 전극의 polarization(image charge)이 준입자 gap을 줄임. semilocal DFT는 이 효과를 담지 못함.
- 보정 아이디어 두 단계: (1) 기체상 IP/EA에 맞추는 shift, (2) 고전 image-charge 모형으로 gap을 다시 줄이는 shift.
- image plane 위치와 분자-전극 거리에 보정량이 민감함. 이 값의 선택 근거를 반드시 기록할 것.
- 다음 할 일: 보정 전후 T(E)에서 peak가 E_F로부터 어떻게 멀어지는지 비교하는 절차 정리.
