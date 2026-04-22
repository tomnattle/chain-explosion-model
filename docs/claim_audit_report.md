# Claim Audit Report

- risk_score: **0**
- summary: 高风险：指标定义差异足以改变结论，发布前需强制标注统计对象。
- abs_S: binary=2.000000, raw=1.194216, ncc=2.389139

## Risk Items
- `RISK_METRIC_DIVERGENCE` (high): 跨统计口径结果分歧显著
- `RISK_OBJECT_MISMATCH` (high): 标准 CHSH 与 NCC 指标对象不一致
- `RISK_CLAIM_OVERREACH` (medium): 结论外推风险

## Recommendations
- 在报告中明确区分 E_binary / E_raw / E_ncc，不混用符号 E。
- 若使用 NCC 指标，需单列其物理测量映射与适用边界。
- 结论声明前附上同一样本的多指标对照表。
