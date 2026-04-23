# NIST 验证治理总报告

## 输入证据

- 门禁报告: `artifacts/public_validation_pack/NIST_MAPPING_POLICY_CHECK.md`
- 排查报告: `artifacts/public_validation_pack/NIST_E_DELTA_VALIDATION_SANITY.md`

## 一页结论

- 门禁状态: `FAIL`
- 门禁建议: `继续2D加固（先锁映射规范，再进3D）`
- 是否边界问题主导: `NO`
- 指标一致性（NLL vs Brier）: `YES`
- 切分一致性（LOBO vs L2O）: `YES`

## 排查定位

- LOBO赢家（NLL/Brier）: `high` / `high`
- L2O赢家（NLL/Brier）: `high` / `high`
- 解释: 若一致性均为 YES，说明“后期变差”更可能是模型外推稳定性问题，而非评估器偏置。

## 执行建议

- 当前不建议进入3D主线，先完成2D映射规范锁定与压力映射稳健性修复。
- 保持统一口径：所有外部结论均写为“在主映射定义下”。
