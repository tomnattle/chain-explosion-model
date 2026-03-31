# 统一测试套件说明（34 项样本）

面向 `run_unified_suite.py`。**默认 `-g all` 共 31 条**（`ce` + `verify` + `explore` + `critique`）；**`-g extended` 再增 3 条**，全仓库清单 **34 条**。下列「测什么」以 runner 当前实现为准；**PASS 只表示「满足该条脚本 + 校验器定义的成功条件」**，不等于物理定理已在自然界被证明。

---

## 1. 如何运行

| 命令 | 条数 | 含义简略 |
|------|------|----------|
| `python run_unified_suite.py` | 31 | `all` |
| `python run_unified_suite.py -g extended` | 3 | 额外验证脚本 |
| 连续跑两遍 `all` 与 `extended` | **34** | 全清单 |

`--relaxed` 会放宽部分数值门禁（如 verify 波恩的相关系数下限、critique 部分条目的回归带等），详见 `run_unified_suite.py` 内帮助与校验函数。

---

## 2. 按组分：31 条（`all`）

### 2.1 `ce`（11）：链式爆炸 / 双缝内核演示与扫描

| # | 脚本 | 主要测什么 | Runner 门禁特点 |
|---|------|------------|-----------------|
| 1 | `ce_00_double_slit_demo.py` | 双缝传播演示 | 子进程成功为主 |
| 2 | `ce_01_visibility_vs_screen_distance.py` | 对比度随屏距 | 同上 |
| 3 | `ce_02_double_slit_screen_statistics.py` | 屏上统计 | 同上 |
| 4 | `ce_03_visibility_vs_side_coupling_S.py` | 侧向耦合 S 与可见度 V | 期望 PNG 存在 |
| 5 | `ce_04_measurement_absorption_at_slit.py` | 缝口吸收（测量效应示意） | 期望 PNG |
| 6 | `ce_05_finite_absorber_detector.py` | 有限吸收体 | 期望 PNG |
| 7 | `ce_06_delayed_choice_absorber.py` | 延迟选择类设置 | 期望 PNG |
| 8 | `ce_07_measurement_phase_diagram_scan.py` | 测量相图扫描 | 期望 PNG |
| 9 | `ce_08_entanglement_split_wavepackets.py` | 分包/纠缠示意 | 期望 PNG |
| 10 | `ce_09_entanglement_with_phase_field.py` | 相位场与纠缠 | 期望 PNG |
| 11 | `ce_10_entanglement_distance_scan.py` | 纠缠随距离扫描 | 期望 PNG |

**含义**：在**固定离散更新规则**下，各类几何与参数扫描能否稳定跑出图与日志；多为**工程烟雾 / 产物检查**，不逐项对标希尔伯特空间中的标准量子定理编号。

### 2.2 `verify` + `discover`（5）：与统计或「发现」叙事对齐的校验

| # | 脚本 | 主要测什么 | Runner 门禁特点 |
|---|------|------------|-----------------|
| 12 | `verify_born_rule.py` |  Born 规则：出生概率 vs \|ψ\|² 类对照 | **硬**：皮尔逊 r ≥ 阈值（strict 约 0.9） |
| 13 | `verify_uncertainty.py` | 不确定性相关现象、拟合指数 α | **现象记录**；解析 α，**不与 −1 硬比** |
| 14 | `discover_visibility_decay.py` | 对比度随传播衰减 | **硬**：末端 V 应低于初值 |
| 15 | `discover_measurement_continuity.py` | 吸收「连续」与可见度叙事 | 须有 `[OK]` 或 `[警告]`（后者仍 PASS） |
| 16 | `discover_coupling_constant.py` | 耦合常数探索 | 偏 smoke；有最优 S/A 则做粗 sanity |

### 2.3 `explore`（8）：洛伦兹代数、能量、因果、条纹与边界探针

| # | 脚本 | 主要测什么 | Runner 门禁特点 |
|---|------|------------|-----------------|
| 17 | `explore_lorentz_selfcheck.py` | 速度合成代数自洽 | **硬**：交换/结合误差近零，v′≈1 |
| 18 | `explore_visibility_vs_uniform_loss.py` | 均匀损耗对总强度 | **硬**：median(loss/base) 须明显 &lt;1 |
| 19 | `explore_energy_budget.py` | 步间能量比（未全局归一时增长） | **硬**：中位步间比 &gt;1 |
| 20 | `explore_causal_front.py` | 2D 因果前缘速度 | **硬**：dx/dt 中位数约在 ~1 格/步一带 |
| 21 | `explore_fringe_spacing_vs_slit.py` | 条纹间隔 vs 缝距 log-log 斜率 | 须能解析斜率；**斜率与远场 −1 偏离**仅备注，**非硬失败** |
| 22 | `explore_causal_cone_anisotropy.py` | L1 前缘 vs 轴向前缘比 | **硬**：比值相对标定 GOLD 在公差内 + PNG 非空 |
| 23 | `explore_relativity_light_speed_invariant.py` | 公式层 v′（与格子核叙述分离） | **硬**：v′≈1，PNG 非空 |
| 24 | `explore_double_slit_mirror_parity.py` | 镜像对称几何下的残差 | **硬**：asym、r_mirror 在回归带内 + PNG 非空 |

### 2.4 `critique`（7）：可审计表述 + 数值/图像硬回归

| # | 脚本 | 主要测什么 | Runner 门禁特点 |
|---|------|------------|-----------------|
| 25 | `explore_critique_01_unification_scope.py` | 「统一」宣称须可审计的清单 | PNG 非空 + `[OK]` |
| 26 | `explore_critique_02_bell_hypothesis_boundary.py` | Bell/坍缩叙事边界 | 同上 |
| 27 | `explore_critique_03_analogy_vs_mechanism.py` | 类比 vs 同一机制措辞 | 同上 |
| 28 | `explore_critique_04_sr_not_derived_from_lattice.py` | SR 非从本格点核推导；对照格点 v 与公式 v′ | **硬**：v_grid、v′ 区间 + PNG |
| 29 | `explore_critique_05_decay_nonuniqueness.py` | 可见度轨迹可被均匀损耗模仿 | **硬**：r_V 高阈值 + PNG |
| 30 | `explore_critique_06_energy_growth_explosion.py` | sum(E) 爆炸式增长非标量守恒 | **硬**：R_E 巨大、步间中位比 &gt;1 + PNG |
| 31 | `explore_critique_07_fringe_spacing_theory_gap.py` | 条纹 log-log 斜率 vs 远场 −1 | **硬**：斜率在相对 **仓库 GOLD（约 −0.118）** 的公差内；**不**要求等于 −1 |

---

## 3. `extended`（+3，合计 34）

| # | 脚本 | 主要测什么 | Runner 门禁特点 |
|---|------|------------|-----------------|
| 32 | `verify_interference_decay.py` | 干涉衰减验证 | 期望 PNG 存在（默认校验） |
| 33 | `verify_delayed_choice.py` | 延迟选择验证 | 同上 |
| 34 | `verify_which_way.py` | Which-way 验证 | 同上 |

---

## 4. 「模型自洽」在这里指什么

一致的含义是**在离散、`ce_engine_v2` 规则、以及各脚本固定参数**之下：

1. **可执行**：脚本按设计跑完，exit code 与 runner 一致。  
2. **内部数值关系**：门禁所检查的量（因果速度、能量步比、洛伦兹公式层、部分回归 GOLD 等）与**当前实现**一致或落在设定公差内。  
3. **叙事分层**：多处刻意区分「格子层现象 / 公式层验算 / 教科书连续极限」，避免把演示与推导链混为一谈（尤其 critique 01–04、07）。

这不是说「与所有连续 QM+SR 教材在同一无量纲标度上逐式相等」，而是说**仓库内规则与检查项彼此不打架**。

---

## 5. 能确定什么（在「通过默认门禁」的前提下）

- **实现层面**：当前仓库里的 CE 仿真在这些场景下**可重复地**产生预期数量级与图像；关键硬门禁条目（verify Born、若干 explore/critique）**未被当前 runner 判失败**。  
- **离散动力学**：在给定邻居与更新下，因果前缘速度、能量非守恒增长、Born 统计对照等**与该内核设计一致**。  
- **表述边界**：critique 组把「什么能对外说、什么只能当假说/类比」固定成可回归文本与图；通过表示**这些工件按设计生成**。

---

## 6. 不能确定什么（即使 34/34 PASS）

- **自然界**：不能由本仓库替代实验；Bell/非定域等仍以实验与标准理论为准。  
- **唯一机理**：例如仅看可见度衰减**不能**唯一锁定微观机理（critique 05 的方向）。  
- **从格点严格推出 SR**：critique 04 与相关 explore 明确**未声称**已完成闵氏几何+洛伦兹群的格点推导。  
- **连续远场双缝标度**：当前条纹 log-log 斜率在 critique 07 中与远场 **−1** 仍有**大偏差**；通过 critique 07 只说明**与仓库 GOLD 一致**，**不**表示已对齐 \( \Delta y \propto 1/d \) 的极限。  
- **全局 ce 脚本**：许多 `ce_*` 条目以 smoke / PNG 为主，**不**逐项绑定到某一教科书定理编号与误差界。

---

## 7. 维护建议

- 若有意改变 `ce_engine_v2` 或 critique/explore 的标定参数，请同步更新 `run_unified_suite.py` 中的 **GOLD/阈值**，并理解失败是「与旧标定不一致」而非必然「物理错了」。  
- 若某条科学目标改为「必须与连续理论某式一致」，应**改仿真或单测定义**，而不是假定现有离散网格会自动给出该极限。

---

*文档与 `run_unified_suite.py` 中 `build_jobs()` 及校验器实现同步；若任务表增删，请以代码为准并更新本页。*
