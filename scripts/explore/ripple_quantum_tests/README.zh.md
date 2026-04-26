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

对照模式：

```bash
python scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v3.py --constant-mode calibrated
```

---

## 解释边界（当前版本）

- 这个任务当前优先比较“曲线形状是否可重现”，不是直接要求 first-principles 推导出所有常数。
- 对 MRI 的 `42.577 MHz/T` 与原子钟精确频率，本脚本会标注“线性/离散结构是否成立”与“绝对常数是否被模型内生解释”为不同层级。
- 后续若要提高可信度，需要把常数来源从“拟合参数”提升为“模型可推导参数”。
