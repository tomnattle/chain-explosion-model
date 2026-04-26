# Zenodo Metadata: Bell Inequality Audit (NIST Data Reconciliation)
# Zenodo 元数据：贝尔不等式审计 (NIST 数据对账)

## Published record / 已发布记录（当前引用）
- **Zenodo record:** https://zenodo.org/records/19784937  
- **DOI:** https://doi.org/10.5281/zenodo.19784937  
- **Companion code / 配套代码:** https://github.com/tomnattle/chain-explosion-model  

## Title / 标题
[EN] Denominator Audit of Bell/CHSH Statistics: Protocol Sensitivity to Pairing-Rule Definitions
[中] 贝尔不等式的分母审计：配对规则定义的协议敏感性分析

## Description / 描述
[EN] 
This paper presents a "Denominator Audit" of Bell/CHSH violations using NIST experimental data. Historically, violations of S > 2.0 are cited as proof of non-locality. Our audit reveals that these results are not intrinsic to the physical system but are "manufactured" through the selective manipulation of coincidence windows (Accounting Fraud). 

On the **same** NIST complete-blind stream, we compare a **strict** pairing tolerance (**0.0**) versus the Round-1 **standard** tolerance (**15.0**) in **NIST grid-index units** on the exported CSV `t` axis (not calibrated seconds in this deposit). The frozen binary-CHSH snapshot gives **S_strict = 2.336276** vs **S_standard = 2.839387** (**Δ = +0.503111**). A bootstrap CI for the standard branch **includes** \(2\sqrt{2}\) (`artifacts/reports/chsh_bootstrap_ci_standard15.json`, `ci_contains_tsirelson: true`); we therefore discuss **protocol sensitivity**, not Tsirelson violation. Separately, the “30 cm truth” is a **laboratory heuristic** (about **1 ns ↔ ~30 cm** in vacuum); it motivates coincidence bookkeeping sensitivity and **must not** be read as “parameter 15.0 equals 15 ns” here.

**Reproducibility (repository):** data file `data/nist_completeblind_side_streams.csv`; run from repo root `python scripts/explore/chsh_denominator_audit.py` (writes `artifacts/bell_window_scan_v1/`).

[中]
在**同一组** NIST complete-blind 事件流上，我们在导出 CSV 的 `t` 网格上对比**严苛**配对容差（**0.0**）与第一轮**标准**容差（**15.0**），单位为 **NIST 网格指数**（本归档不将其标定为秒）。冻结的二元 CHSH 快照为 **S_strict = 2.336276** 与 **S_standard = 2.839387**（**Δ = +0.503111**）。标准分支的 bootstrap 置信区间**覆盖** \(2\sqrt{2}\)（`artifacts/reports/chsh_bootstrap_ci_standard15.json`，`ci_contains_tsirelson: true`）；因此本文强调**协议敏感性**，而非 Tsirelson 违背。另：“30 厘米的真相”是**实验室启发**（真空中约 **1 纳秒 ↔ 约 30 厘米**），用于提示符合会计的敏感性，**不应**被读作“参数 15.0 等于 15 纳秒”。

**可复现（配套仓库）：** 数据 `data/nist_completeblind_side_streams.csv`；在仓库根目录运行 `python scripts/explore/chsh_denominator_audit.py`（输出写入 `artifacts/bell_window_scan_v1/`）。

## Keywords / 关键词
- Bell Inequality / 贝尔不等式
- CHSH Statistics / CHSH 统计
- Accounting Fraud / 会计造假
- Coincidence Window / 配对窗口
- Denominator Audit / 分母审计
- Geometric Illusion / 几何幻觉
- NIST Data / NIST 数据
