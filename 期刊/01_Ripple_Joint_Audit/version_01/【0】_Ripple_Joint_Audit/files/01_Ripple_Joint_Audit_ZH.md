# Bell 审计补充材料：局域涟漪介质框架下四项量子样式基准的联合一致性审计（v6）

**版本**：v6-joint supplement draft  
**定位**：Bell 主稿补充材料 / 后续方法学注记（非独立首投主稿）  
**仓库**：`chain-explosion-model`

---

## 摘要

在 Bell 配对窗口敏感性审计完成后，我们将问题从“统计协议是否改变结论”推进到“单一局域介质参数能否同时覆盖多类量子样式曲线”。本文定位为 **Bell 主稿的补充证据链**，基于 `ripple_quantum_tests_v6_joint.py`，在四项玩具基准（激光阈值、半导体截止、MRI 拉莫尔线性、原子钟谱线）上执行联合优化与应力扫描。核心设置是同一组 \((\mu,\rho,\eta)\) 贯穿四项门禁，并以 `nrmse_x`、`nrmse_y`、\(R^2\) 作为形状指标，叠加常数侧约束。

在默认联合分支中，归档结果显示：`joint_pass = True`，最优点约为 \(\mu=1.549500,\rho=2.350000,\eta=0.079989\)，`joint loss = 4.158e-05`，四项均为 `shape_ok = Y`。同时我们保留负分支：在 derived-wave-speed 且 \(\alpha>0\) 的耦合下，原子钟分支可失配（`joint_pass = False`），说明可行域对色散闭合与几何耦合结构敏感。本文贡献是方法学层面的“联合一致性审计脚手架”，用于支撑 Bell 主稿后的模型层讨论；不宣称硬件复刻，也不宣称色散指数已由第一性原理推导完成。

---

## 1. 问题与边界

### 1.1 问题

我们关注的不是“单项拟合能否过线”，而是：

\[
\text{同一组介质参数三元组 }(\mu,\rho,\eta)\ \text{是否可在四项指标上同时满足门禁。}
\]

### 1.2 边界

1. 参考曲线为 **QM-like 解析曲线**，非硬件原始事件流；  
2. \((\mu,\rho,\eta)\) 在当前脚本内是无量纲旋钮，尚未建立 SI 映射；  
3. `--wave-speed derived` 的闭合函数是现象学形式，参考点标定到 \(c_{\text{ref}}\)；  
4. 本文定位为“方法与可复现审计”，不是“替代量子理论裁决”。

---

## 2. 方法

### 2.1 四项子实验

- `laser_threshold`：阈值前弱响应、阈值后陡增  
- `semiconductor_cutoff`：吸收边截止形状  
- `mri_larmor`：\(\omega \propto B\) 线性主项  
- `atomic_clock_modes`：Cs 附近谱线形状

### 2.2 指标与门禁

- 形状：`nrmse_x`, `nrmse_y`, \(R^2\)  
- v6 汇总门：`joint_pass`（四项 `shape_ok` + 常数侧约束）

### 2.3 联合优化

脚本：`scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v6_joint.py`  
优化向量：

\[
\theta = (\mu,\rho,\eta,\mathrm{bw})
\]

目标函数为四项 `nrmse_y` 之和并加权常数项惩罚（详见脚本）。

### 2.4 应力扫描

通过 `--stress` 与 `--stress-2d` 扫描 \(\alpha\) 与 \(w_{f0}\) 的网格，输出相图与 CSV，并可用 `--stress-refine` 减少粗迭代假阴性。

---

## 3. 结果（归档锚点）

### 3.1 主结果：v6 默认联合分支

来源：`artifacts/ripple_quantum_tests_v6/RIPPLE_QUANTUM_TESTS_V6_SUMMARY.md`

- Optimum: \(\mu=1.549500,\rho=2.350000,\eta=0.079989,\mathrm{bw}=2.999586\times10^{-5}\) GHz  
- Joint loss: \(4.158\times10^{-5}\)  
- `joint_pass = True`  
- 四项 `shape_ok = Y`

### 3.2 负分支：derived-wave-speed + 耦合失败示例

来源：`artifacts/ripple_quantum_tests_v6_derived_v2/RIPPLE_QUANTUM_TESTS_V6_SUMMARY.md`

- `joint_pass = False`  
- 原子钟分支失配（`shape_ok = N`）  
- 提示：色散闭合与几何耦合并非自动可行

### 3.3 可行修复示例：derived-wave-speed + \(\alpha=0\)

来源：`artifacts/ripple_quantum_tests_v6_derived_alpha0/RIPPLE_QUANTUM_TESTS_V6_SUMMARY.md`

- `joint_pass = True`  
- 说明 derived 分支可行性依赖耦合结构选择

### 3.4 图示总览（读图优先）

> 下列图均已放在同目录 `figures/`。若后续导出 PDF，可直接按文件名插图。

1. `fig_joint_2x2_default.png`：v6 默认联合分支（通过）  
2. `fig_joint_2x2_derived_fail.png`：derived + \(\alpha>0\) 失配示例（失败）  
3. `fig_joint_2x2_derived_alpha0.png`：derived + \(\alpha=0\) 可行示例（通过）  
4. `fig_branch_metrics.png`：三分支四实验的 `nrmse_y` 与 `shape_ok` 对照  
5. `fig_shared_parameter_drift.png`：共享参数相对默认分支的偏移  
6. `fig_stress_2d_demo.png`：\(\alpha \times w_{f0}\) 应力相图  
7. `fig_stress_refine_effect.png`：1D 扫描中 refine 对假阴性修复效果  
8. `fig_v6_pipeline_schematic.png`：v6 审计管线示意图

---

## 4. 讨论

### 4.1 这项工作证明了什么

本文证明的是：在已声明的 toy 协议和门禁下，单一参数族可以通过联合约束，且可用应力扫描观察可行域塌缩/恢复。这比“四项独立拟合各自过线”信息量更高。其用途是为 Bell 主稿提供“模型层补充背景”，而非替代真实数据证据。

### 4.2 这项工作没有证明什么

1. 没有证明量子力学错误；  
2. 没有证明 \((\mu,\rho,\eta)\) 已具备 SI 对应；  
3. 没有证明色散指数来自格点第一性原理；  
4. 没有进行硬件级原始事件复刻。

### 4.3 与 Bell 审计的关系

Bell 审计是**真实数据上的协议敏感性审计**；本文是**模型联合一致性审计**。两者可并行构成“数据审计 + 模型脚手架”的双轨，但证据类型不同，不能互相替代。

---

## 5. 复现清单

在仓库根目录执行：

```bash
python scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v6_joint.py --maxiter 200 --seed 7
python scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v6_joint.py --stress --stress-2d --stress-alpha-steps 12 --stress-wf0-steps 10 --stress-maxiter 48
python scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v6_joint.py --wave-speed derived --atomic-rho-exponent 0 --maxiter 220 --seed 7
```

---

## 6. 结论与下一步

当前 v6 的价值是：把“单项过线”提升为“联合过线 + 可行域审计”。这是 Bell 主稿之后的方法学补强。下一阶段若要从“现象学闭合”进入“物理理论主张”，关键任务是把色散关系从格点动力学推导出来，并建立 \((\mu,\rho,\eta)\) 的 SI 映射及独立可测预测。

---

## 附录 A：图生成脚本

图包由以下脚本自动生成：

```bash
python "期刊/01_Ripple_Joint_Audit/version_01/【0】_Ripple_Joint_Audit/files/generate_figures.py"
```

脚本会读取 `artifacts/ripple_quantum_tests_v6*` 归档 JSON/PNG/CSV，并在 `figures/` 下输出论文友好图集。

