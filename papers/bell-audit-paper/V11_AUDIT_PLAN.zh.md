# v11 反质疑审计立项（GHZ threshold 分支）

## 目标

v11 的目标不是追求更高 `F`，而是系统回应四类核心质疑，给出可复现、可审计、可写入论文的方法学证据。

## 工作包

- `A1 多种子稳定性`：跨 seed 重采样，输出 `F_context` 分布、标准差、分位区间。
- `A2 全局扰动鲁棒性`：围绕运行点做全局扰动，统计达到目标阈值 `|F|>=F*` 的体积占比。
- `A3 严格量子对照口径`：在同口径报告下给出 `context/QM` 的效率比，避免口径混淆。
- `A4 零模型防作弊`：完全随机输入经过同流程，统计“伪高值”概率。

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
