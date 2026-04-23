# 标题（中文）

GHZ 三体模型中的分母回收与后选择审计：一项基于两阶段搜索的机制核查

## 摘要

本文针对 GHZ 三体模型中的高相关主张，提出一种“分母回收”审计框架，用于区分真实相关机制与后选择偏差。我们在统一脚本下对比 `none` 与 `energy_weighted` 分母逻辑，采用两阶段搜索（two-stage search：90 deg 粗搜与 2 deg 细搜），并结合 `F` 与 `coincidence_rate` 的交易关系进行穿透式核查。当前结果显示，在 `samples=80000`、`numba_cpu` 后端与既定门控条件下，细搜最佳值仅达到 `F=0.085396`，与目标 `F=4` 仍有 `|err|=3.914604` 的明显差距，且失败分解指向相关形状失配而非单纯样本稀疏。本文结论限定为方法级结论，不将统计结果外推为本体级结论。

## 1. 引言

GHZ 型不等式及其扩展常用于讨论多体相关结构与经典模型边界。然而，在存在探测阈值、共享扰动与后选择门控的建模条件下，统计量定义本身会影响最终可见的相关强度。若只比较最终 `F` 值而忽略分母与样本包含规则，容易把“簿记变化”误判为“机制突破”。

基于这一动机，本文采用穿透式审计思路：第一，显式登记指标定义并区分分母机制；第二，用固定协议复扫参数空间，避免只挑最优点；第三，把 `F` 与 `coincidence_rate` 绑定检查，识别潜在筛样伪增益。本文贡献是构建并运行一条可复现的 GHZ 审计流程，给出当前配置下的负结果证据链及其边界解释。

### 1.1 相关工作（占位）

后续将按以下方向补充文献：

1. GHZ 与多体相关见证量的标准定义与实验实现；
2. 探测阈值、后选择与样本率塌缩对统计结果的影响；
3. 参数搜索与模型稳健性评估在基础物理建模中的方法；
4. 负结果与边界声明在高争议问题中的写作规范。

## 2. 方法

### 2.1 指标与分母机制

本研究在同一实验脚本中注册以下统计定义：

1. `none`：基于门控后样本的条件均值，不额外引入能量权重；
2. `energy_weighted`：在门控样本上以本地响应幅值绝对值乘积作为权重，计算加权归一化均值。

两者共享相同的事件产生与门控规则，仅在分母与权重处理上不同。需要强调的是：本文中的 ternary 输出与门控统计不等价于标准二值 GHZ witness，因此本文比较的是“审计协议内的相对变化”，而非直接替代标准 GHZ 命题。

### 2.2 两阶段搜索协议

搜索参数包含 `pump_gain` 与四个上下文相位偏置（`XXX/XYY/YXY/YYX`）。

- 粗搜阶段：相位步长 `90 deg`，在给定增益网格上全组合扫描；
- 细搜阶段：以粗搜 Top-k 候选为中心，使用 `2 deg` 步长在局部邻域再扫描；
- 约束条件：设置 `coincidence_rate` 下限，过滤极低样本率配置；
- 稳健性：记录 bootstrap 与 seed sweep 指标，并输出失败分解表。

## 3. 结果

### 3.1 主结果

在 `samples=80000`、`threshold=0.35`、`pump_gain=0.45`、`denominator_mode=energy_weighted`、后端 `numba_cpu` 的配置下：

- 默认上下文相位下，`context_pump_gated_mean` 得到 `F=-0.001124`，`coincidence_rate=0.5844`；
- 粗搜（90 deg）最佳候选为 `F=0.074761`（`R=0.5691`）；
- 细搜（2 deg）最佳候选为 `F=0.085396`（`R=0.6704`）；
- 与目标 `F=4` 的误差仍为 `|err|=3.914604`。

以上结果显示，当前模型在审计协议下未出现逼近 4 的非线性跃迁。对应图表建议使用：

- 图1：`fig1_f_vs_threshold.png`
- 图2：`fig2_mechanism_heatmap.png`

### 3.2 交易关系与稳健性

稳健性摘要如下：

- bootstrap：`draws=10`，`F_context_mean_bootstrap_sd=0.056036`；
- seed sweep：`count=3`，`seed_sweep_context_f_sd=0.010787`；
- 失败分解：coarse 与 fine 均被判定为 `correlation shape mismatch dominates`。

交易关系方面，`F_context_pump_gated` 在不同 `R` 分箱中均未表现出向 4 靠拢的趋势。典型分箱均值从 `[0.0,0.2)` 的 `-0.019317` 到 `[0.8,1.0]` 的 `-0.001344`，整体仍围绕零附近波动。对应图表建议：

- 图3：`fig3_f_vs_coincidence_tradeoff.png`
- 表1：搜索配置注册表
- 表2：coarse/fine Top-k 汇总表
- 表3：稳健性统计表

## 4. 讨论

当前结果支持以下解释：在既定模型族与门控机制中，`F` 的提升主要受相关结构形状限制，而非仅靠放宽样本筛选即可达到目标值。细搜阶段虽然把 `F` 从粗搜最佳进一步提升，但提升幅度有限，且仍远离 4。

从审计视角看，分母回收的价值在于把“分子相关强度”与“分母/样本包含规则”明确拆账。即便在启用 `energy_weighted` 后，结果仍未显示异常跃迁，这有助于排除“只因簿记方式变化而产生奇迹值”的解释。

本文也存在边界：当前多 seed 数量仍偏小，且尚未完成与 `denominator_mode=none` 的系统 A/B 汇总。后续需要扩大样本与 seed 数，以进一步收紧结论置信度。

## 5. 结论

可确认结论：

1. 在当前 GHZ 三体审计协议下，未观察到 `F` 向 4 接近的证据；
2. 失败分解更支持“相关形状失配”而非“样本率阈值主导”；
3. 分母回收方案提升了指标可解释性与审计透明度。

不可确认结论：

- 不能据此宣称对所有 GHZ 相关模型的普适否定；
- 不能将本审计统计量等同于标准 GHZ witness 的严格替代。

后续实验路线：

- 补全 `none` vs `energy_weighted` 的同网格同 seed A/B；
- 扩展到 `>=20` seeds 的稳健性统计；
- 增加更高样本量与更细邻域扰动扫描。

## 附录

参数与输出文件：

- 结果汇总：`artifacts/ghz_threshold_experiment/GHZ_THRESHOLD_SUMMARY.md`
- 审计报告：`artifacts/ghz_threshold_experiment/AUDIT_REPORT.md`
- 机器读写结果：`artifacts/ghz_threshold_experiment/GHZ_THRESHOLD_RESULTS.json`
- 图：`ghz_threshold_F_vs_T.png`、`ghz_threshold_mechanism_heatmap.png`

复现命令（当前已运行配置）：

```bash
python scripts/explore/ghz_threshold/explore_ghz_threshold_pipeline.py --compute-backend numba_cpu --samples 80000 --search --search-samples 25000 --search-gain-steps 4 --search-phase-step-deg 90 --search-top-k 20 --fine-search --fine-seed-k 5 --fine-phase-half-span-deg 4 --fine-phase-step-deg 2 --fine-gain-steps 4 --audit-bootstrap-draws 10 --audit-bootstrap-subsample 12000 --audit-seeds 0,1,2 --out-dir artifacts/ghz_threshold_experiment
```

术语统一：

- 统一术语表见 `papers/TERMINOLOGY.md`。
