# NIST E(Delta) 严格2D CV Bootstrap（多映射）

- 数据: `data/17_04_CH_pockel_100kHz.run.completeblind.dat.compressed.build.hdf5`
- mappings: `half_split, parity, quadrant_split`
- bootstrap: `2000`
- seed: `20260422`
- 评估口径: 仅 `Δ` 轴，LOBO-CV，二项neg-loglik，无测试泄漏。

| mapping | point Bell | point LowCos | point HighCos | P(Bell wins) | P(Low wins) | P(High wins) |
|---|---:|---:|---:|---:|---:|---:|
| half_split | 2593.057086 | 21003.996391 | 369.469383 | 0.0000 | 0.0000 | 1.0000 |
| parity | 2519.117750 | 131914.716114 | 3759723.854277 | 1.0000 | 0.0000 | 0.0000 |
| quadrant_split | 299.245691 | 140223.169946 | 3759751.086172 | 1.0000 | 0.0000 | 0.0000 |

## 决策读取

- 若某模型在所有映射下胜率都高，说明2D泛化稳健。
- 若赢家随映射切换，说明结论仍受定义约束，需进入3D前先锁定映射规范。
