# V10.4 真实代价曲线（计算，非示意）

与 `v10_3_selection_tax_audit.py` 同一套介质相位与门控定义；对 `gate_k` 做线性扫描，
每个点的 `F_gated`、`R_gated` 均由同一份固定样本算出，**未**使用 `plot_f_target_cost_curve.py` 类参数锚点。
并加入随机同保留率对照：`F_random_mean ± 1σ`，用于区分门控选择效应与随机抽样基线。

## 产物
- `V10_4_REAL_COST_CURVE.png`
- `V10_4_REAL_COST_CURVE.csv`
- `V10_4_REAL_COST_CURVE.meta.json`（`type`: `computed_curve`）

- 参考 F_cont（与 gate_k 无关）: 10.071724