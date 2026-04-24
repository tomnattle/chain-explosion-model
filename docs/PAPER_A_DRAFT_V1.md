# Paper A Draft v1

## 标题（建议）

Statistical Measure Dependence in CHSH Analysis:  
A Reproducible `Δ`-Mapping Closure Case Study

---

## 中文主稿

### 摘要

Bell/CHSH 文献长期聚焦实验漏洞封闭条件，但在“漏洞已封闭”的前提下，统计对象定义本身是否改变结论绑定仍缺乏系统化审计。本文围绕该问题，构建了一个可复现的 `Δ` 映射闭合流程：在逐次事件数据上并行计算 `binary`、`continuous_raw` 与 `NCC` 三口径，固定预处理顺序与随机种，执行 bootstrap、exact paired-swap permutation 与映射敏感性扫描，并采用 Definition/Dimensional/Process/Statistical 四闭合检查与失败降格规则。

在当前主映射（`half_split`）下，我们观察到 `LowCos` 相对 Bell 折线基线具有更低拟合误差（`wRMSE(Bell)=0.058318`，`wRMSE(LowCos)=0.014459`，`wRMSE(HighCos)=0.016552`），`wRMSE(LowCos)-wRMSE(Bell)` 的 95% CI 为 `[-0.049243, -0.036555]`，且 `P(wRMSE(LowCos) < wRMSE(Bell))=1.000000`；9-bin exact permutation 检验给出单侧 `p=0.0117188`（双侧 `p=0.0234375`）。自动汇总草判显示四闭合均为 `PASS`，但我们保留显式边界：`slot->±1` 规则属于假设定义，结论仅在当前映射与流程条件域内成立。

本文贡献在于提供统计对象敏感性的审计范式，而非给出理论终局判断。我们建议将该流程作为 Bell 风格结果报告中的补充协议，以降低指标选择偏见与叙事外推风险。

**关键词：** CHSH，统计对象一致性，`Δ` 映射，闭合检查，可复现审计

### 1. 引言

Bell/CHSH 相关研究长期聚焦于实验漏洞（如探测效率、局域性与自由选择）及其封闭条件。然而，即使在“漏洞已封闭”的理想语境下，仍存在一个方法学问题：当统计对象定义发生改变时，结论绑定是否保持不变。本文关注这一“对象层一致性”问题，而非对既有理论进行本体裁决。

我们在同一事件样本上并行计算 `binary`、`continuous_raw` 与 `NCC` 三种统计对象，并对 `E(Δ)` 曲线采用统一可复现流程进行比较。研究目标是提供一个可审计、可复跑、可证伪的统计对象敏感性案例。

本文贡献有三点：  
（1）给出 `Δ` 映射的预注册操作化定义，并将其与误差传播和稳健性扰动流程绑定；  
（2）提供跨口径并行报告与闭合判据（Definition/Dimensional/Process/Statistical），把结论前提显式化；  
（3）在公开脚本和固定产物路径下形成可复现实验链，便于第三方重复与反驳。

### 2. 方法

#### 2.1 研究目标与边界

本文目标是审计 CHSH 分析中统计对象对结论的敏感性，而非裁决某一统计口径在本体论上的唯一正确性。我们在同一输入样本上并行构建 `binary`、`continuous_raw` 与 `NCC` 三种统计对象，比较其对应 `S` 值差异，并要求所有结论受预注册流程约束。

#### 2.2 数据与预注册

分析使用逐次事件数据（NIST HDF5）。执行前固定并记录：数据路径与校验、预处理顺序、`Δ` 映射定义、统计公式、bootstrap 次数与随机种。脚本与输出路径在仓库公开，以保证可复现性。

#### 2.3 `Δ` 映射与事件聚合

one-hot 槽位解码为离散 slot（`v=2^k -> slot k`）；以 Alice/Bob slot 的循环距离构造 `Δ`，折叠到 `0..8` 并映射到 `0..180°`。  
该步骤属于工程可复现定义，不宣称为官方唯一定义。`slot->±1` 的二值赋值规则作为显式假设预先注册，并在映射敏感性实验中做替代测试。

#### 2.4 模型比较与误差指标

对 `E(Δ)` 曲线，比较三类基线：

- Bell 分段线性基线（局域对照曲线）
- `LowCos`: `a*cos(Δ)+b`（加权最小二乘拟合）
- `HighCos`: `sign(a)*cos(Δ)`（高对称余弦基线）

点估计采用加权 RMSE。统计不确定性通过 binomial parametric bootstrap（95% CI）给出，并使用 9-bin exact paired-swap permutation test 检验 `LowCos` 相对 Bell 基线的误差优势显著性。

#### 2.5 闭合判据与失败条件

采用四闭合检查：Definition、Dimensional、Process、Statistical。  
任一失败触发降格规则：NIST 段落标注为 `provisional evidence`，并在失败日志中保留复现命令、触发条件与处置记录。

#### 2.6 稳健性设计

除主映射 `half_split` 外，执行 `parity` 与 `quadrant_split` 替代映射。验证逻辑采用 LOBO 与 L2O 双策略，并比较 raw 与 clipped 设定，以排除单一验证配置导致的伪优势。

#### 2.7 复现入口

主执行入口：

- `scripts/explore/run_delta_validation_pack.ps1`
- `scripts/explore/summarize_delta_closure.py`

主输出：

- `artifacts/public_validation_pack/NIST_E_DELTA_RIGOR_REPORT.md`
- `artifacts/public_validation_pack/NIST_E_DELTA_VALIDATION_SANITY.md`
- `artifacts/public_validation_pack/DELTA_CLOSURE_SUMMARY.md`
- `artifacts/public_validation_pack/DELTA_CLOSURE_CHECKLIST.md`

### 3. 结果

在预注册 `Δ` 映射（`half_split`）与公开脚本下，我们对 NIST 数据的 `E(Δ)` 进行了定义闭合与统计严谨性检查。结果显示，`LowCos` 对实测点的拟合误差显著低于 Bell 折线基线：`wRMSE(Bell)=0.058318`，`wRMSE(LowCos)=0.014459`，`wRMSE(HighCos)=0.016552`。Bootstrap 给出 `wRMSE(LowCos)-wRMSE(Bell)` 的 95% CI 为 `[-0.049243, -0.036555]`，且 `P(wRMSE(LowCos) < wRMSE(Bell)) = 1.000000`。9-bin exact paired-swap 置换检验结果为单侧 `p=0.0117188`（双侧 `p=0.0234375`）。

闭合草判（自动汇总）为：Definition=`PASS`，Dimensional=`PASS`，Process=`PASS`，Statistical=`PASS`。上述结论限定在当前映射定义与样本处理流程下成立，不外推为对理论本体的裁决；其中 `slot->±1` 映射仍属于显式假设，应在讨论节保留边界声明。

#### 结果表

| 项目 | 数值 |
|---|---:|
| 映射模式 | `half_split` |
| wRMSE(Bell) | 0.058318 |
| wRMSE(LowCos) | 0.014459 |
| wRMSE(HighCos) | 0.016552 |
| P(wRMSE(LowCos) < wRMSE(Bell)) | 1.000000 |
| permutation p(one-sided) | 0.0117188 |
| permutation p(two-sided) | 0.0234375 |

#### 四闭合草判

| 闭合项 | 草判 |
|---|---|
| 定义闭合 | PASS |
| 量纲闭合 | PASS |
| 流程闭合 | PASS |
| 统计闭合 | PASS |

### 4. 讨论

结果层面，当前主映射下 `LowCos` 相比 Bell 折线呈现更低误差，且在 bootstrap 与 permutation 检验下保持统计支持。与此同时，我们强调：该优势结论成立于“预注册映射定义 + 指定样本处理流程”这一条件域，而不直接外推为基础理论的裁决。

换言之，本文核心不是“某理论被推翻”，而是“统计对象定义变化可显著影响结论绑定，且这种影响可被结构化审计”。边界方面，`slot->±1` 规则仍属显式假设，`Δ` 映射虽具工程可复现性，但不等同于官方唯一定义。

基于此，我们将失败条件前置：若出现结论翻转级敏感性、跨实现不可复现或量纲链失配，则自动触发降格叙述（`provisional evidence`）并记录失败日志。这种“先写失败条件、后写正结论”的做法，旨在降低指标选择偏见与叙事过度外推风险。

未来工作包括：扩展更全面的映射策略与参数扰动、完成跨数据集重复、以及将 GHZ 三体场景独立为专门问题而非并入当前主线。本文应被视作方法论文：提供的是“如何审计统计对象一致性”的流程资产，而非终局理论声明。

### 5. 结论

本文给出一个可复现的 CHSH 统计对象审计流程，并在当前 `Δ` 映射定义下展示了稳定的对象依赖性信号。结论限定于当前定义与流程条件域；其核心价值在于提供审计协议与失败降格机制，为后续跨数据集、跨映射的系统复核提供基础。

### 参考产物与脚本

- `docs/DELTA_MAPPING_VALIDATION_PROTOCOL.md`
- `docs/DELTA_MAPPING_RUNBOOK.md`
- `artifacts/public_validation_pack/NIST_E_DELTA_RIGOR_REPORT.md`
- `artifacts/public_validation_pack/NIST_E_DELTA_VALIDATION_SANITY.md`
- `artifacts/public_validation_pack/DELTA_CLOSURE_SUMMARY.md`

---

## English Mirror (Compact)

### Abstract

This paper presents a reproducible audit workflow for statistical-object dependence in CHSH analysis. On event-level data, we compare `binary`, `continuous_raw`, and `NCC` tracks under a preregistered `Δ` mapping protocol, with bootstrap, exact paired-swap permutation, and robustness scans.

Under the current primary mapping (`half_split`), `LowCos` yields lower fitting error than the Bell polyline baseline (`wRMSE(Bell)=0.058318`, `wRMSE(LowCos)=0.014459`, `wRMSE(HighCos)=0.016552`), with 95% CI for `wRMSE(LowCos)-wRMSE(Bell)` equal to `[-0.049243, -0.036555]`, and one-sided permutation `p=0.0117188` (two-sided `p=0.0234375`). Draft closure checks are all `PASS`.

Claims are explicitly bounded: `slot->±1` remains an assumption, and conclusions are restricted to the current mapping/protocol domain. We position the work as a methods contribution rather than a foundational adjudication.

### Structured Sections

- **Introduction:** object-level consistency problem in loophole-closed contexts.
- **Methods:** preregistered `Δ` mapping, three-track statistics, four-closure criteria, downgrade-on-failure.
- **Results:** lower error of `LowCos` vs Bell baseline under current protocol.
- **Discussion:** failure-first reporting, boundary conditions, and replication roadmap.
- **Conclusion:** an auditable workflow for statistical-object sensitivity.

### Reproducibility

- Runner: `scripts/explore/run_delta_validation_pack.ps1`
- Summarizer: `scripts/explore/summarize_delta_closure.py`
- Core artifacts under `artifacts/public_validation_pack/`
