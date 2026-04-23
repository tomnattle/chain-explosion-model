# NIST 2D 映射策略门禁检查

- 输入报告: `artifacts/public_validation_pack/NIST_E_DELTA_CV_BOOTSTRAP_MULTIMAPPING.md`
- 主映射: `half_split`
- 压力映射: `parity, quadrant_split`
- 主门槛: `P(wins) >= 0.90`
- 灾难退化阈值: `P(wins) <= 0.05` and `point > 2.00 x best`

## 主映射结果

- 主映射赢家模型: `high`
- 赢家概率: `1.0000`
- 主映射门槛: `PASS`

## 压力映射检查

| mapping | primary model prob | primary point | best point | best model | catastrophic |
|---|---:|---:|---:|---|---|
| parity | 0.0000 | 3759723.854277 | 2519.117750 | bell | YES |
| quadrant_split | 0.0000 | 3759751.086172 | 299.245691 | bell | YES |

## Gate 结论

- 总体门禁: `FAIL`
- 决策建议: `继续2D加固（先锁映射规范，再进3D）`
