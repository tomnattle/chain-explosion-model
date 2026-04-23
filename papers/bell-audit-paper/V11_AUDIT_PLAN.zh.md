# v11 审计增强立项（GHZ threshold 分支）

## 目标

v11 的目标不是追求更高 `F`，而是系统回应四类核心质疑，给出可复现、可审计、可写入论文的方法学证据。

## 工作包

- `A1 多种子稳定性`：跨 seed 重采样，输出 `F_context` 分布、标准差、分位区间。
- `A2 全局扰动鲁棒性`：围绕运行点做全局扰动，统计达到目标阈值 `|F|>=F*` 的体积占比。
- `A3 严格量子对照口径`：在同口径报告下给出 `context/QM` 的效率比，避免口径混淆。
- `A4 零模型对照`：完全随机输入经过同流程，统计“伪高值”概率。

## 产出文件

- `artifacts/ghz_threshold_experiment/GHZ_THRESHOLD_RESULTS.json`
- `artifacts/ghz_threshold_experiment/GHZ_THRESHOLD_SUMMARY.md`
- `artifacts/ghz_threshold_experiment/AUDIT_REPORT.md`
- `artifacts/ghz_threshold_experiment/TOP20_AUDIT_CANDIDATES.md`

## 建议运行命令

```bash
python scripts/explore/ghz_threshold/explore_ghz_threshold_pipeline.py \
  --samples 80000 \
  --search --fine-search \
  --compute-backend numba_cpu \
  --audit-seeds 0,1,2,3,4,5,6,7,8,9,10,11 \
  --audit-seed-samples 80000 \
  --audit-perturb-draws 500 \
  --audit-perturb-target-abs-f 0.08 \
  --audit-null-draws 300 \
  --audit-null-samples 25000 \
  --audit-null-target-abs-f 0.08
```

## 验收门槛（建议）

- 多种子：`seed_sweep_context_f_sd` 不应与均值同量级失控。
- 全局扰动：`success_ratio` 若接近 0，判定参数窗口脆弱。
- 零模型：`false_positive_ratio` 必须保持低水平，否则流程存在统计伪阳性风险。
- 量子口径：`context_to_qm_efficiency` 与 `context_best_to_qm_efficiency` 需显式报告。

## 结论模板

若上述审计显示低效率、弱稳健或较高伪阳性风险，则结论应写为：

“在当前审计口径下，机制难以复现实验所需的 GHZ 级关联，且未发现可稳定复现的参数体积。”

## 当前状态（封存说明）

- `v11` 已完成一次方法学审计落地，并产出完整脚本与结果文件。
- 当前状态：已封存为“仓库内可复核资产”，不纳入 Bell 主论文正文主结果。
- 原因：现阶段 GHZ 审计结果主要用于风险暴露与流程校验，尚不足以支撑物理论证层面的主张。

## 后续接手建议（留给后续贡献者）

- 若要继续推进，请优先做中等规模复核（更大 `samples`、更多 `seed`、更多 `perturb/null draws`）。
- 若复核后仍显示窗口脆弱或零模型伪阳性偏高，可直接保留为负结果案例，不必强行转主结论。
- 若复核显著改善，再考虑将其迁移至独立 GHZ 论文线，而非并入 Bell 主线。
