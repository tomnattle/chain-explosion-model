# V9 红队自审

## 结论先行
- best D: 1.072680 (F=3.753542, R=0.285778, off=18.000)
- bootstrap D CI95: [1.065974, 1.079975]
- train D: 1.073217, valid D: 1.070957

## 重点风险
- boundary adhesion: True
- low R at best D: True
- D drop(train->valid): 0.002260

## 图
- `V9_GATE_SENSITIVITY.png`
- `V9_SEED_STABILITY.png`
- `V9_BOUNDARY_ADHESION.png`