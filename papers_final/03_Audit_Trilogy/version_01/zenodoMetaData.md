# Zenodo Metadata: The Audit Trilogy — Bell + GHZ V10.4 Computed Curve
# Zenodo 元数据：审计三部曲 —— 贝尔审计 + GHZ V10.4 计算曲线

## Published record / 已发布记录（当前引用）
- **Zenodo record:** https://zenodo.org/records/19785083  
- **DOI:** https://doi.org/10.5281/zenodo.19785083  
- **Companion code / 配套代码:** https://github.com/tomnattle/chain-explosion-model  

## Title / 标题
[EN] The Audit Trilogy: NIST CHSH Denominator Audit + GHZ V10.4 Computed Cost Curve (medium-v10)
[中] 审计三部曲：NIST CHSH 分母审计 + GHZ V10.4 计算代价曲线（medium-v10）

## Description / 描述
[EN]
This deposit summarizes **two frozen workflows** in one methodological bundle.

**(1) Bell / CHSH (real public data):** Binary CHSH on the NIST complete-blind CSV. Pairing uses tolerances in **NIST grid-index units** on the exported `t` axis (not calibrated seconds in this repository). Frozen snapshot: `battle_results/nist_completeblind_2015-09-19/battle_result.json` (`S_strict = 2.336276` at tolerance 0.0 vs `S_standard = 2.839387` at 15.0; pair counts 136632 vs 148670). Reproduce the window scan via `python scripts/explore/chsh_denominator_audit.py`.

**(2) GHZ-style statistic (simulation, V10.4 only):** The GHZ leg is **not** tied to `ghz_loop_explosion_v19.py`. It is anchored to **`scripts/explore/ghz_medium_v10/v10_4_real_cost_curve.py`**, which emits a **`computed_curve`** (`type` in `V10_4_REAL_COST_CURVE.meta.json`): a **fixed RNG phase sample** (`medium_phase_states`), **soft amplitude gating** with parameter **`gate_k`**, reported **`F_gated`**, mean simultaneous-hit retention **`R_gated`**, and a **matched-retention random control** (`F_random_mean`, `F_random_std`). Canonical outputs live under `artifacts/ghz_medium_v10/` (`V10_4_REAL_COST_CURVE.png`, `.csv`, `.meta.json`, `V10_4_REAL_COST_CURVE_REPORT.md`).

**Scope statement:** This is **methodological reproducibility** documentation — not a claim that either pipeline certifies a specific hardware Bell or GHZ experiment.

[中]
本归档将**两条冻结工作流**合并为一条方法论叙述。

**（1）贝尔 / CHSH（真实公开数据）：** 在 NIST complete-blind CSV 上做二元 CHSH。配对容差取导出列 `t` 上的 **NIST 网格指数单位**（本仓库**不**标定为秒）。冻结快照：`battle_results/nist_completeblind_2015-09-19/battle_result.json`（容差 0.0 时 `S_strict = 2.336276`，15.0 时 `S_standard = 2.839387`；配对数 136632 / 148670）。窗口扫描复现：`python scripts/explore/chsh_denominator_audit.py`。

**（2）GHZ 型统计量（仿真，仅 V10.4）：** GHZ 侧**不再**绑定 `ghz_loop_explosion_v19.py`。唯一锚点为 **`scripts/explore/ghz_medium_v10/v10_4_real_cost_curve.py`**，产出 **`computed_curve`**（见 `V10_4_REAL_COST_CURVE.meta.json` 中 `type`）：**固定 RNG 相位样本**（`medium_phase_states`）、参数为 **`gate_k`** 的**软振幅门控**、报告 **`F_gated`**、同时触中平均保留 **`R_gated`**，以及**同保留率随机对照**（`F_random_mean`、`F_random_std`）。规范产物位于 `artifacts/ghz_medium_v10/`（`V10_4_REAL_COST_CURVE.png`、`.csv`、`.meta.json`、`V10_4_REAL_COST_CURVE_REPORT.md`）。

**范围声明：** 本文为**方法论与可复现性**文档——**不**声称任一脚本对某一具体硬件贝尔或 GHZ 实验作出鉴定。

**Reproducibility (repository):** Bell: `python scripts/explore/chsh_denominator_audit.py` (needs `data/nist_completeblind_side_streams.csv`). GHZ V10.4: `python scripts/explore/ghz_medium_v10/v10_4_real_cost_curve.py`.

**可复现（配套仓库）：** Bell：`python scripts/explore/chsh_denominator_audit.py`（需 `data/nist_completeblind_side_streams.csv`）。GHZ V10.4：`python scripts/explore/ghz_medium_v10/v10_4_real_cost_curve.py`。

## Keywords / 关键词
- Audit Trilogy / 审计三部曲
- Bell Inequality / 贝尔不等式
- CHSH Denominator Audit / CHSH 分母审计
- NIST Grid Index Pairing / NIST 网格指数配对
- GHZ V10.4 / GHZ V10.4
- medium-v10 / medium-v10
- Computed Cost Curve / 计算代价曲线
- Post-Selection Audit / 后选择审计
- Reproducibility / 可复现性
