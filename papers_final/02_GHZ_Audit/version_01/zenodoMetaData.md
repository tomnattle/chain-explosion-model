# Zenodo Metadata: GHZ-Type Mermin Statistic Audit (V10.4)
# Zenodo 元数据：GHZ 型 Mermin 统计量后选择审计 (V10.4)

## Published record / 已发布记录（当前引用）
- **Zenodo record:** https://zenodo.org/records/19785022  
- **DOI:** https://doi.org/10.5281/zenodo.19785022  
- **Companion code / 配套代码:** https://github.com/tomnattle/chain-explosion-model  

## Title / 标题
[EN] Post-Selection Sensitivity in a GHZ-Type Mermin Statistic: An In-Silico Audit (medium-v10)
[中] GHZ 型 Mermin 统计量的后选择敏感性：`medium-v10` 仿真审计（非硬件复刻）

## Description / 描述
[EN] 
This deposit documents a rigorous **in-silico** post-selection audit of a **GHZ-type Mermin statistic** in the repository's **`medium-v10` wave model** (three local phase-locked sources), motivated by textbook/laboratory GHZ narratives—it is **not** claimed to replay one specific hardware run. Within that simulator class, we show that chasing high \(F\) couples to amplitude gating and **low retention**, and matched-retention random controls fail to reproduce the gated lift—supporting a **selection-driven** reading of the reported metric **inside the model**. 

Using the V10.4 real cost curve and matched-retention random controls, we show that elevated \(F\) values in this simulator class are tightly coupled to selection rules and retention trade-offs. We frame this as a method-level sensitivity result inside the model class, not as a hardware-level claim.

[中]
本归档记录对 **`medium-v10` 波动模型**中 **GHZ 型 Mermin 统计量**的严格**仿真**后选择审计（三个局域相位锁定源），动机来自教科书/实验室叙事，**不**声称复刻某一具体硬件实验。在该模拟器类内，我们展示：追逐高 \(F\) 与振幅门控及**低保留率**绑定，而同保留率随机对照无法复现门控抬升——从而在**模型内**支持对报告指标的**筛选驱动**解读。

通过 V10.4 真实代价曲线和同保留率随机对照，我们展示了：在该模拟器类内，较高 \(F\) 与筛选规则及保留率权衡紧密耦合。本文将其定位为模型内的方法学敏感性结果，而非硬件层结论。

**Reproducibility (repository):** from repo root run `python scripts/explore/ghz_medium_v10/v10_4_real_cost_curve.py` (see script header for output paths). Companion figure in this deposit: `figures/V10_4_REAL_COST_CURVE.png`.

**可复现（配套仓库）：** 在仓库根目录运行 `python scripts/explore/ghz_medium_v10/v10_4_real_cost_curve.py`（输出路径见脚本头部）。本归档插图：`figures/V10_4_REAL_COST_CURVE.png`。

## Keywords / 关键词
- GHZ State / GHZ 态
- Post-Selection Audit / 后选择审计
- Protocol Sensitivity / 协议敏感性
- Geometric Illusion / 几何幻觉
- Model-Scope Interpretation / 模型范围解释
- Selection Tax / 选择税
