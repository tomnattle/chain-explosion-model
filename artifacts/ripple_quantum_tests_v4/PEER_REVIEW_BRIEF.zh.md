# Ripple Quantum Tests v4 — 原理说明与数值汇总（供外部审阅）

本文档用于转发给其他模型或审稿人做批判性审阅。实现与完整曲线见仓库脚本与 JSON。

- **脚本路径：** `scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v4_plot_optimize.py`
- **完整数值与曲线：** `artifacts/ripple_quantum_tests_v4/RIPPLE_QUANTUM_TESTS_V4_RESULTS.json`
- **图示：** 同目录下 `RIPPLE_V4_*_2x2.png`、`RIPPLE_V4_NRMSE_BEFORE_AFTER.png`、各 `*_baseline.png` / `*_optimized.png`

---

## 0. 这套程序在做什么（以及刻意不声称什么）

这是一组 **玩具级、可复现** 的数值实验：在四条独立的一维扫描轴上，各定义一条 **“QM-like 参考曲线”**（教科书式形状）和一条 **“Ripple 侧模型曲线”**（由少量参数生成），用 **归一化 RMSE（NRMSE）** 衡量形状接近程度；MRI 与原子钟还额外要求 **由给定公式从介质/腔体参数“推导”出的常数** 落在容差内。

**不声称：** 已从第一性原理推出 Cs 超精细频率或核旋比；不声称与真实激光器/PN 结/MRI 硬件一一对应。  
**声称层级：** 在给定函数族与判定规则下，基线参数与优化后参数各自能否通过阈值；优化使用 **有界域上的差分进化（`scipy`）**。

---

## 1. 公共指标与通过规则

**NRMSE（形状）：**

\[
\mathrm{NRMSE}(y_\mathrm{ref}, y_\mathrm{rip}) = \frac{\sqrt{\mathrm{mean}\bigl((y_\mathrm{ref}-y_\mathrm{rip})^2\bigr)}}{\max(x)-\min(x)}
\]

（分母为自变量 \(x\) 的全局跨度；若跨度过小则退化为 1。）

**本轮固定阈值（与 JSON `meta` 一致）：**

| 项目 | 取值 |
|------|------|
| `shape_threshold` | 0.18 |
| MRI `γ` 相对误差容差 | 0.02 |
| 原子钟中心频率误差容差 | 20000 Hz（相对 9.19 GHz 量级） |

**判定：**

- **激光 / 半导体：** `constant_pass` 恒为真（无数值常数关卡）；`final_pass = (NRMSE ≤ 0.18)`。
- **MRI：** \(\gamma_\mathrm{derived} = \mu\kappa/(\rho(1+\eta))\)；`constant_pass = |\gamma_\mathrm{derived}-\gamma_\mathrm{QM}|/\gamma_\mathrm{QM} ≤ 0.02`；`final_pass = shape_pass ∧ constant_pass`。
- **原子钟：** \(f_0\)（GHz）由驻波腔公式 \(f = n v / (2L)\) 换算；Ripple 曲线为高斯 \(\exp(-\tfrac12((x-f_0)/\sigma)^2)\)，\(\sigma\) 为可调线宽；`constant_pass = |f_{0,\mathrm{rip}}-f_{0,\mathrm{QM}}|×10^9 ≤ 20000` Hz；`final_pass = shape_pass ∧ constant_pass`。

---

## 2. 四个子程序的原理（模型定义）

### 2.1 `laser_threshold`（激光阈值）

- **自变量 \(x\)：** `[0, 1]` 上均匀采样（240 点），语义上可理解为泵浦/激励强度一类无量纲轴。
- **QM-like 参考：** 分段线性：\(x \le 0.5\) 时为 `0.02·x`；\(x > 0.5\) 时为 `2.2·(x-0.5)`（阈值 0.5，上支斜率 2.2）。
- **Ripple：** 同结构分段线性，参数化为阈值 `th`、上支斜率 `a_hi`、下支斜率 `a_lo`。
- **意图：** 对比“阈值以下弱响应、阈值以上陡增”的 **阈值行为** 是否可被同一函数族逼近。

### 2.2 `semiconductor_cutoff`（半导体吸收边）

- **自变量 \(x\)：** `[0, 4]`（260 点），归一化频率轴。
- **QM-like：** Logistic（Sigmoid）\(\sigma(x; c, k) = 1/(1+\exp(-k(x-c)))\)，固定 \(c=2.0,\; k=20\)。
- **Ripple：** 同形式，\(c,k\) 可调。
- **意图：** 对比吸收边 **陡变/截止** 形状。

### 2.3 `mri_larmor`（MRI 拉莫尔线性）

- **自变量 \(x\)：** `[0, 3]` T（180 点）。
- **QM-like：** \(\omega = \gamma_\mathrm{QM}\, x\)，\(\gamma_\mathrm{QM}=42.577\)（与 ¹H 旋磁比同数量级的玩具数值，单位与脚本内部一致抽象）。
- **Ripple：** \(\omega = \gamma_\mathrm{derived}\, x + q\, x^2\)，其中 \(\gamma_\mathrm{derived}=\mu\kappa/(\rho(1+\eta))\)，\(q\) 为可调小二次项。
- **意图：** 在 **引入轻微非线性** 的同时，检查线性主项的 **推导常数** 能否落入容差。

### 2.4 `atomic_clock_modes`（原子钟谱线/模式）

- **自变量 \(x\)：** `[9.1918, 9.1934]` GHz（500 点），覆盖 Cs 超精细线附近。
- **QM-like：** 以 \(f_{0,\mathrm{QM}}=9.192631770\) GHz、\(\sigma_\mathrm{QM}=3\times 10^{-5}\) GHz 为中心的高斯。
- **Ripple：** 高斯中心 \(f_0 = n\,v/(2L)\)（GHz），线宽 \(\sigma\) 可调；\(n\) 为整数模指数（优化中取连续变量后四舍五入到 \([1,4]\)）。
- **意图：** **分离** “腔体几何给出的特征频率”与“线宽（损耗/谱展宽）”：前者走推导公式，后者为形状匹配自由度。

---

## 3. 优化阶段（v4）

- **算法：** `scipy.optimize.differential_evolution`，各子问题独立、各有参数盒；`maxiter=120`，`seed=42`（与当前归档 JSON 一致）。
- **激光：** 优化 \((th, a_\mathrm{hi}, a_\mathrm{lo})\)，最小化 NRMSE。
- **半导体：** 优化 \((c, k)\)，最小化 NRMSE。
- **MRI：** 优化 \((\mu,\kappa,\rho,\eta,q)\)，损失为 \(\gamma\) 相对误差 + NRMSE 项 + 违反形状/常数阈值的惩罚项（见源码 `_loss_mri`）。
- **原子钟：** 优化 \((L, v, n_\mathrm{float}, \sigma)\)，损失为 NRMSE + 中心频偏（Hz 标度）+ 惩罚项（见源码 `_loss_atomic`）。

**重要说明：** 激光与半导体的 Ripple **与参考同属一个解析函数族** 时，优化可以把 NRMSE 压到数值零附近——这属于 **曲线重合/参数识别**，不等于从独立物理定律推出了新结论。

---

## 4. 结果数值汇总（当前归档）

### 4.1 基线（v3 风格默认 Ripple 参数，未跑全局优化）

| 测试 | NRMSE | shape_pass | constant_pass | final_pass | 备注（摘录） |
|------|------:|:----------:|:-------------:|:----------:|--------------|
| laser_threshold | 0.028013 | Y | Y | Y | th=0.5, a_hi=2.05, a_lo=0.03 |
| semiconductor_cutoff | 0.027911 | Y | Y | Y | c=2.03, k=16.5 |
| mri_larmor | 0.098210 | Y | N | N | γ_derived=35.299448，rel_err≈0.1709 |
| atomic_clock_modes | 0.182292 | N | N | N | f0_ripple≈9.194251 GHz，err≈1.619 MHz |

### 4.2 优化后（差分进化 + 有界域）

| 测试 | NRMSE | shape_pass | constant_pass | final_pass | 备注（摘录） |
|------|------:|:----------:|:-------------:|:----------:|--------------|
| laser_threshold | ≈ 4.96×10⁻¹⁵ | Y | Y | Y | th≈0.5, a_hi≈2.2, a_lo≈0.02（与 QM-like 分段参数一致） |
| semiconductor_cutoff | 0.0 | Y | Y | Y | c=2.0, k=20.0（与 QM-like 一致） |
| mri_larmor | ≈ 1.60×10⁻⁴ | Y | Y | Y | γ_derived≈42.577 MHz/T（与目标一致到 ~10⁻¹¹ 相对误差）；μ≈3.567, κ≈80.32, ρ≈6.194, η≈0.0863, q≈0.00506 |
| atomic_clock_modes | ≈ 1.92×10⁻¹⁰ | Y | Y | Y | f0_ripple≈9.192631770 GHz；center_err_hz≈2.66×10⁻⁵；L≈0.016301 m, v≈2.99692623×10⁸ m/s, n=1, σ≈3×10⁻⁵ GHz |

---

## 5. 请审阅人重点挑毛病的问题（建议攻击面）

1. **参考曲线本身**是手写玩具，不是实验数据；任何拟合成功是否只对 **自造目标** 成立？  
2. **NRMSE 分母用 \(\max x-\min x\)** 而非 \(\max y-\min y\)**，是否低估/高估某些尺度下的形状误差？  
3. **MRI** 的 \(\gamma\) 公式 \(\mu\kappa/(\rho(1+\eta))\) 与二次项 \(qx^2\) 的 **量纲与可辨识性**：是否多解、是否过参数化？  
4. **原子钟** 同时优化 \(L,v,\sigma\) 与离散 \(n\)：在 **固定 QM 参考高斯** 下，是否存在 **本质上的等价类**（不同 \(L,v\) 组合给出同一 \(f_0\)）？线宽 \(\sigma\) 与腔 Q 的物理联系是否缺失？  
5. **优化后** 激光/半导体与参考 **参数重合**，是否说明测试对“Ripple 是否区别于 QM” **没有鉴别力**（identifiability）？  
6. **多重任务分开优化**：未联合验算参数在 **跨实验间是否一致**（同一组介质参数是否应同时解释四现象）。  
7. **统计显著性**：无噪声模型、无 bootstrap；**单次确定性曲线** 上 NRMSE 接近 0 的 **随机对照** 未建立。

---

## 附录：v5 对审阅点的代码层回应

脚本：`scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v5_rigorous.py`，默认输出 `artifacts/ripple_quantum_tests_v5/`。

- **尺度风险**：每项同时记录 **`nrmse_x`、`nrmse_y`（按参考 \(y\) 量程）与 \(R^2\)**，`shape_pass` 默认要求双 NRMSE 与 \(R^2\) 阈（可用 `--r2-min -1` 关闭 \(R^2\) 硬门）。
- **MRI 可辨识性**：固定 \(\mu,\rho,\eta\)，**代数求** \(\kappa=\gamma_\mathrm{QM}\rho(1+\eta)/\mu\)，不再对四元组做无约束搜索；`quad` 仅保留为可选固定项（默认 0）。
- **原子钟 \((L,v)\) 等价类**：**固定 \(v=c\)**，由目标 \(f_0\) 与整数 \(n\) **代数求** \(L\)，**仅优化线宽 `bw`** 做形状匹配。
- **异族半导体（可选）**：`--semi-tanh` 用 tanh 型阶跃逼近 logistic 参考（仍可能在数值上极好贴合，需结合真实数据或更严物理约束进一步加压）。

**v6（联合优化）**：`scripts/explore/ripple_quantum_tests/ripple_quantum_tests_v6_joint.py` — 对 `(μ,ρ,η,bw)` 联合最小化四项 `nrmse_y` + `f0` 惩罚；激光/半导体由 **toy bridge** 从介质三元组映射。**桥接公式仍非第一性原理**，但满足「单一账本」式的参数对齐与 `joint_pass` 报告。

---

*文档生成说明：数值与 `RIPPLE_QUANTUM_TESTS_V4_RESULTS.json`（`meta.optimization` 与 `baseline` / `optimized` 节）对齐；若重新运行脚本，以最新 JSON 为准。*
