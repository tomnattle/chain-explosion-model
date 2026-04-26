# Ripple Quantum Tests（任务目录说明）

## 目录初衷

本目录用于执行一个明确的新任务：  
在**不预设“量子正确/错误”结论**的前提下，给出一组可复现的、可对比的数值测试，检查“涟漪/链式模型”是否能重现 Claude 提出的四类经典量子现象的**关键曲线形状**。

目标不是立刻证明某理论终局胜负，而是：

1. 把争论从口头观点转成可运行代码；
2. 把“是否相似”落到统一指标（归一化 RMSE）；
3. 形成后续可持续扩展的测试基线。

---

## 当前包含的测试

脚本：`scripts/explore/ripple_quantum_tests/ripple_quantum_tests.py`

四个测试模块：

1. 激光阈值行为（Laser Threshold）
2. 半导体吸收截止（Semiconductor Cutoff）
3. MRI 拉莫尔线性关系（MRI Larmor Linearity）
4. 原子钟离散模式可得性（Atomic Clock Mode Discreteness）

每个测试都会输出：

- `qm_curve`：量子教科书型参考曲线（用于比较）
- `ripple_curve`：涟漪模型曲线
- `rmse` 与 `nrmse`（归一化 RMSE）
- `pass/fail`（按统一阈值判定）

严格版脚本：`scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v2.py`

- 在 v1 的基础上增加“双层判定”：
  - `shape_pass`：曲线形状是否匹配（NRMSE）
  - `constant_pass`：关键常数是否也在容差内
- 最终规则：`final_pass = shape_pass AND constant_pass`
- 目的：避免“只靠形状拟合就算通过”。

推导优先版脚本：`scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v3.py`

- 新增 `--constant-mode`：
  - `derived`：MRI/原子钟常数来自模型参数推导（不直接写目标常数）
  - `calibrated`：作为对照，允许近目标常数参考
- 用于明确区分“可拟合通过”和“可推导通过”。

严谨版（v5，双尺度 NRMSE + 可辨识性约束）：`scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v5_rigorous.py`

- 同时报告 `nrmse_x`、`nrmse_y`（按参考曲线 \(y\) 量程归一）、\(R^2\)；默认可用 `--r2-min -1` 关闭 \(R^2\) 硬阈。
- MRI：固定 \(\mu,\rho,\eta\)，由目标 \(\gamma\) **代数解** \(\kappa\)。
- 原子钟：**\(v=c\)** 固定，由 \(f_0\) 与 \(n\) **代数求** \(L\)，仅优化线宽 `bw`。
- 半导体可选 `--semi-tanh`（tanh 贴 logistic 参考，异族压力测试）。
- 作图对照：`scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v4_plot_optimize.py`。

全局联合版（v6）：`scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v6_joint.py`

- **单一介质三元组** `(μ, ρ, η)` + 原子钟线宽 `bw` 经差分进化联合优化；MRI 仍用 **代数 κ** 锁定 γ；腔长按 `L = (n·v/(2f₀))·(ρ/ρ_ref)^α`（α 可调）。默认 **v=c**；可选 **`--wave-speed derived`**：`v=f(μ,ρ,η)`，在 `(μ_ref,ρ_ref,η_ref)` 处标定为 **`--c-ref-m-s`**（默认真空 c），见 `ripple_medium_dispersion.py`。**注意：** `derived` 与 **α>0** 同时开时，ρ 既进色散又进腔长，可行域变窄；可先试 **`--atomic-rho-exponent 0`**。
- 激光/半导体由 **显式 toy bridge** 从 `(μ,ρ,η)` 映射到分段线 / Sigmoid 参数（见脚本 docstring，非第一性原理）。
- 目标函数：四项 **`nrmse_y` 之和** + `f0` 相对误差惩罚；JSON 报告 `joint_pass`（四块 shape 门 + γ 精确 + `f0` 容差）。

---

## 输出位置

默认输出到：

- `artifacts/ripple_quantum_tests/RIPPLE_QUANTUM_TESTS_RESULTS.json`
- `artifacts/ripple_quantum_tests/RIPPLE_QUANTUM_TESTS_SUMMARY.md`
- `artifacts/ripple_quantum_tests/RIPPLE_QUANTUM_TESTS_PLOTS.png`

严格版输出：

- `artifacts/ripple_quantum_tests_v2/RIPPLE_QUANTUM_TESTS_V2_RESULTS.json`
- `artifacts/ripple_quantum_tests_v2/RIPPLE_QUANTUM_TESTS_V2_SUMMARY.md`

推导优先版输出：

- `artifacts/ripple_quantum_tests_v3/RIPPLE_QUANTUM_TESTS_V3_RESULTS.json`
- `artifacts/ripple_quantum_tests_v3/RIPPLE_QUANTUM_TESTS_V3_SUMMARY.md`

严谨版（v5）输出：

- `artifacts/ripple_quantum_tests_v5/RIPPLE_QUANTUM_TESTS_V5_RESULTS.json`
- `artifacts/ripple_quantum_tests_v5/RIPPLE_QUANTUM_TESTS_V5_SUMMARY.md`
- `artifacts/ripple_quantum_tests_v5/RIPPLE_V5_RIGOROUS_2x2.png`

联合版（v6）输出：

- `artifacts/ripple_quantum_tests_v6/RIPPLE_QUANTUM_TESTS_V6_RESULTS.json`
- `artifacts/ripple_quantum_tests_v6/RIPPLE_QUANTUM_TESTS_V6_SUMMARY.md`
- `artifacts/ripple_quantum_tests_v6/RIPPLE_V6_JOINT_2x2.png`

---

## 使用方式

```bash
python scripts/explore/ripple_quantum_tests/ripple_quantum_tests.py
```

可选参数示例：

```bash
python scripts/explore/ripple_quantum_tests/ripple_quantum_tests.py --seed 2026 --threshold 0.18
```

严格版：

```bash
python scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v2.py --shape-threshold 0.18 --mri-const-rel-tol 0.02 --clock-center-tol-hz 20000
```

推导优先版（建议先跑 derived）：

```bash
python scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v3.py --constant-mode derived
```

严谨版 v5：

```bash
python scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v5_rigorous.py --maxiter 120 --seed 42
python scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v5_rigorous.py --semi-tanh
```

联合优化 v6：

```bash
python scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v6_joint.py --maxiter 200 --seed 7
python scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v6_joint.py --wave-speed derived --atomic-rho-exponent 0 --maxiter 220 --seed 7
```

应力扫描（观察 `joint_pass` 在 α 或 α×`w_f0` 网格上何时失效；每格用 `--stress-maxiter`，比正式 `--maxiter` 小以省时间）：

```bash
python scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v6_joint.py --stress --stress-alpha-max 1.2 --stress-alpha-steps 25 --stress-maxiter 72 --out-dir artifacts/ripple_quantum_tests_v6_stress
python scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v6_joint.py --stress --stress-2d --stress-alpha-steps 12 --stress-wf0-steps 10 --stress-maxiter 48

# 粗网格未过线时，对该点用更大迭代复跑（减轻假阴性）
python scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v6_joint.py --stress --stress-refine --stress-refine-maxiter 240 --stress-maxiter 48
```

对照模式：

```bash
python scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v3.py --constant-mode calibrated
```

---

## 解释边界（当前版本）

- 这个任务当前优先比较“曲线形状是否可重现”，不是直接要求 first-principles 推导出所有常数。
- 对 MRI 的 `42.577 MHz/T` 与原子钟精确频率，本脚本会标注“线性/离散结构是否成立”与“绝对常数是否被模型内生解释”为不同层级。
- 后续若要提高可信度，需要把常数来源从“拟合参数”提升为“模型可推导参数”。
